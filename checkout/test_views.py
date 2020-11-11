from django.contrib.auth.models import User
from django.contrib import sessions
from django.test import TestCase, Client
from menu.models import Food_Item, Food_Category
from members_area.models import MemberProfile
from .models import Order
from django.conf import settings

import stripe


class TestCheckoutView(TestCase):
    def setUp(self):
        # engine = settings.SESSION_ENGINE
        # store = engine.SessionStore()
        # store.save()  # we need to make load() work, or the cookie is worthless
        # self.cookies[settings.SESSION_COOKIE_NAME] = store.session_key

        self.user = User.objects.create_user(
            username='elvisTheKing', email='heartbreak@hotel.com',
            password='getsolonely')

        self.user2 = User.objects.create_user(
            username='bobDylan', email='rollingstone@bd.com',
            password='howdoesitfeel')

        # Use this client when not logged in
        self.c = Client()

        # Use when logged in
        self.cient = Client()
        self.client2 = Client()

        self.fruit = Food_Category.objects.create(id=1, name='Fruit')

        self.apple = Food_Item.objects.create(
            id=1, name='Apple', description="Sweet & juicy", price=0.99,
            category=self.fruit)
        self.orange = Food_Item.objects.create(
            id=2, name='Orange', description="Fresh and zesty", price=1.50,
            category=self.fruit)

        self.test_order = Order.objects.create(
            order_number='o123', grand_total=8.47)
        self.test_order.save()

        self.checkout_data = {
            'client_secret': 'pid124_secret_s456',
            'name': 'bobDylan',
            'mobile_number': '07771 555229',
            'email': 'rollingstone@bd.com',
            'for_collection': False,
            'address_line1': '72 Shaftesbury Ave.',
            'address_line2': 'London',
            'postcode': 'W1D 6PA',
            'delivery_instructions': ''
            }

    def test_checkout_GET_no_login(self):
        """ Test for no user logged in, no food order """

        url = '/checkout/'
        response = self.c.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['discount'], None)
        self.assertEqual(float(round(response.context['total'], 2)), 1.99)
        self.assertEqual(response.context['reward_notification'], None)

        # Check form reads out empty values
        self.assertEqual([field.value() for field in response.context['form']],
                         [None for field in range(8)])

    def test_checkout_GET_with_login(self):
        """ Test for user logged in with saved address details, discount
        eligibility and food order exists """

        self.client.force_login(self.user)

        session = self.client.session
        session['food_order'] = {'1': 2, '2': 3}
        session.save()

        test_member = MemberProfile.objects.get(member=self.user)

        test_member.reward_status = 5
        test_member.saved_email = self.user.email
        test_member.saved_mobile_number = '07771 555 229'
        test_member.saved_postcode = 'TN 38116'
        test_member.saved_address_line1 = '3764 Elvis Presley Boulevard'
        test_member.saved_address_line2 = 'Memphis, Tennessee'
        test_member.save()

        self.test_order.member_profile = test_member

        url = '/checkout/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(float(round(response.context['total'], 2)), 7.48)
        self.assertEqual(float(response.context['discount']), 0.99)
        self.assertEqual(response.context['reward_notification'], None)
        self.assertEqual(   
            [field.value() for field in response.context['form']],
            ['elvisTheKing', '07771 555 229', 'heartbreak@hotel.com', False,
             '3764 Elvis Presley Boulevard', 'Memphis, Tennessee', 'TN 38116',
             None])

    def test_checkout_GET_discount_unused(self):
        """ Case whereby user doesn't select the free item they are
        entitled to """

        doughnuts = Food_Category.objects.create(id='2', name='doughnuts')
        Food_Item.objects.create(
            id='3', name='ice_glazed', price=2.99,
            description="extremely delicious", category=doughnuts)

        self.client2.force_login(self.user2)

        test_member2 = MemberProfile.objects.get(member=self.user2)
        # Ensure member is entitled to discount
        test_member2.reward_status = 5
        test_member2.saved_mobile_number = '07555 668 444'
        test_member2.saved_email = self.user2.email
        test_member2.save()

        # Set up food order session var containing NO category 1 items
        session = self.client2.session
        session['food_order'] = {'3': 4}
        session.save()

        url = '/checkout/'
        response2 = self.client2.get(url, {'is_collect': 'True'})
        # Check reward notification is correct when reward status is 5 but no
        # discount item selected (category_id = 1)
        self.assertEqual(
            response2.context['reward_notification'],
            "You haven't selected your free burger yet! Remember this can't be \
part of a combo.")

        # Check form fields are limited to only 4 when is_collect is selected
        self.assertEqual(
            [field.value() for field in response2.context['form']],
            [self.user2.username, '07555 668 444', self.user2.email, True]
        )

    def test_checkout_POST_redirects_foodorder(self):
        """ Redirects to 'food_order' when item not recognized """

        self.client2.force_login(self.user2)
        session = self.client2.session
        # Item 4 doesn't exist
        session['food_order'] = {'1': 3, '4': 1}
        session.save()

        url = '/checkout/'
        response = self.client2.post(url, self.checkout_data)

        # Check invalid food item redirects to food order page
        self.assertEqual(response.url, '/food_order/')
        self.assertEqual(response.status_code, 302)

    def test_checkout_POST_redirects_success(self):
        """ Test all data is valid and checkout success page is reached """

        self.client.force_login(self.user)
        session = self.client.session
        session['food_order'] = {'1': 2, '2': 3}
        session.save()

        elvis_prof = MemberProfile.objects.get(member=self.user)
        elvis_prof.reward_status = 1
        elvis_prof.save()

        url = '/checkout/'
        response = self.client.post(url, self.checkout_data)

        # Check valid data successfully redirects to checkout success
        self.assertEqual(response.status_code, 302)
        self.assertTrue("/checkout/success/" in response.url)
        # Check Member's reward status has increased by 1
        elvis_ordernum = response.url.split('/checkout/success/')[1]
        elvis_order = Order.objects.get(order_number=elvis_ordernum)
        self.assertEqual(elvis_order.member_profile.reward_status,
                         elvis_prof.reward_status + 1)

    def test_checkout_POST_rewardstatus_reset(self):
        """ Ensures reward status zeros after receiving the discount """

        self.client.force_login(self.user)
        session = self.client.session
        session['food_order'] = {'1': 2, '2': 3}
        session.save()

        elvis_prof = MemberProfile.objects.get(member=self.user)
        elvis_prof.reward_status = 5
        elvis_prof.save()

        url = '/checkout/'
        self.checkout_data['discount'] = '0.99'

        response = self.client.post(url, self.checkout_data)

        # Check Member's reward status has reset
        elvis_ordernum = response.url.split('/checkout/success/')[1]
        elvis_order = Order.objects.get(order_number=elvis_ordernum)
        self.assertEqual(elvis_order.member_profile.reward_status, 0)

        # Check discount is correct & applied correctly
        self.assertEqual(float(elvis_order.discount), 0.99)
        self.assertEqual(
            float(elvis_order.grand_total), (self.apple.price * 2) +
            (self.orange.price * 3) + 1.99 - 0.99)

    # def test_is_form_valid(self):

    # def test_save_to_orderlineitem(self):

    # def test_get_discount(self):
    
    # def test_set_order_form(self):
    
    # def test_collect_or_delivery(self):
    
    # def test_get_sent_info(self):
    
    # def test_checkout_success(self):