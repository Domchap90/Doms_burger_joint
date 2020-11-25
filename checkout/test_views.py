from django.contrib.auth.models import User
from django.conf import settings
from django.test import TestCase, Client
from menu.models import Food_Item, Food_Category, Food_Combo
from members_area.models import MemberProfile
from .forms import OrderFormCollection, OrderFormDelivery
from .models import Order
from .views import save_to_orderlineitem, get_discount, set_order_form
from .views import get_sent_info

import json


class TestCheckoutView(TestCase):
    def setUp(self):
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

        self.test_member = MemberProfile.objects.get(member=self.user)

        self.test_member.saved_email = self.user.email
        self.test_member.saved_mobile_number = '07771 555 229'
        self.test_member.saved_postcode = 'TN 38116'
        self.test_member.saved_address_line1 = '3764 Elvis Presley Boulevard'
        self.test_member.saved_address_line2 = 'Memphis, Tennessee'
        self.test_member.save()

        self.test_member2 = MemberProfile.objects.get(member=self.user2)

        self.test_member2.saved_email = self.user2.email
        self.test_member2.saved_mobile_number = '07555 668 444'
        self.test_member2.saved_postcode = 'W1D 6PA'
        self.test_member2.saved_address_line1 = '72 Shaftesbury Ave.'
        self.test_member2.saved_address_line2 = 'London'
        self.test_member2.save()

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

        expected_form_result = [None for field in range(8)]
        expected_form_result[3] = False
        # Check form reads out empty values
        self.assertEqual([field.value() for field in response.context['form']],
                         expected_form_result)

    def test_checkout_GET_with_login(self):
        """ Test for user logged in with saved address details, discount
        eligibility and food order exists """

        self.client.force_login(self.user)

        session = self.client.session
        session['food_order'] = {'1': 2, '2': 3}
        session.save()

        self.test_member.reward_status = 5
        self.test_member.save()

        self.test_order.member_profile = self.test_member

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

        # Ensure member is entitled to discount
        self.test_member2.reward_status = 5
        self.test_member2.save()

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

    def test_is_form_valid_for_collection_success(self):
        # Set food order items up to have total > 15.00
        # therefore making remaining spend 0.00
        session = self.client2.session
        session['food_order'] = {'2': 12}
        session.save()

        ajax_url = '/checkout/is_form_valid/true/'
        ajax_form_data = {
            'name': self.user2.username,
            'mobile_number': self.test_member2.saved_mobile_number,
            'email': self.test_member2.saved_email,
        }
        ajax_response = self.client2.post(ajax_url, ajax_form_data)

        self.assertEqual(ajax_response.status_code, 200)
        self.assertEqual(json.loads(ajax_response.content), {'valid': True})

    def test_is_form_valid_for_collection_fails(self):
        """ Form should feedback errors dictionary because of missing name &
        remaining spend > 0 """

        ajax_url = '/checkout/is_form_valid/true/'
        ajax_form_data = {
            'name': '',
            'mobile_number': self.test_member.saved_mobile_number,
            'email': 'bademailaddress.com',
        }
        ajax_response = self.client.post(ajax_url, ajax_form_data)

        self.assertEqual(ajax_response.status_code, 200)
        expected_errors = {
            'name': 'This field is required.',
            'email': 'Enter a valid email address.'
            }
        self.assertEqual(json.loads(ajax_response.content), expected_errors)

    def test_is_form_valid_for_delivery_success(self):
        # Indirectly set remaining_spend = 0
        session = self.client2.session
        session['food_order'] = {'2': 12}
        session.save()

        # Last parameter of url indicates is_collect=false
        ajax_url = '/checkout/is_form_valid/false/'
        ajax_form_data = {
            'name': self.user2.username,
            'mobile_number': self.test_member2.saved_mobile_number,
            'email': self.test_member2.saved_email,
            'address_line1': '72 Shaftesbury Ave.',
            'address_line2': 'London',
            'postcode': 'W1D 6PA',
            'delivery_instructions': ''
        }
        ajax_response = self.client2.post(ajax_url, ajax_form_data)
        self.assertEqual(json.loads(ajax_response.content), {'valid': True})
        self.assertEqual(ajax_response.status_code, 200)

    def test_is_form_valid_for_delivery_fails(self):
        """ Should fail with postcode not being in range & address line1
        being empty """

        session = self.client.session
        session['food_order'] = {'1': 20}
        session.save()

        ajax_url = '/checkout/is_form_valid/false/'
        ajax_form_data = {
            'name': self.user.username,
            'mobile_number': self.test_member.saved_mobile_number,
            'email': self.test_member.saved_email,
            'address_line1': '',
            'address_line2': 'Somewhere',
            'postcode': 'SE10 9HT',
            'delivery_instructions': ''
        }
        ajax_response = self.client.post(ajax_url, ajax_form_data)

        self.assertEqual(ajax_response.status_code, 200)
        expected_errors = {
            'address_line1': 'This field is required.',
            'postcode': 'Sorry it looks like you are not eligible for delivery. \
However please feel free to make an order for collection.'
            }
        self.assertEqual(json.loads(ajax_response.content), expected_errors)

    def test_save_item_to_orderlineitem(self):
        """ Checks that order is updated with relevant food item """

        self.test_order.grand_total = 0
        save_to_orderlineitem('1', 5, self.test_order)
        save_to_orderlineitem('2', 3, self.test_order)

        # Check quantities are correct
        self.assertEqual(
            [line.quantity for line in self.test_order.lineitems.all()],
            [5, 3])

        # Check ids are correct
        self.assertEqual(
            [line.food_item.pk for line in self.test_order.lineitems.all()],
            [1, 2]
        )
        # Check total is updated
        self.assertEqual(
            float(self.test_order.grand_total),
            (self.apple.price * 5) + (self.orange.price * 3) +
            settings.DELIVERY_FEE
            )

        # Check total purchased attribute of food item 2 is updated
        self.assertEqual(Food_Item.objects.get(id='2').total_purchased, 3)

    def test_save_combo_to_orderlineitem(self):
        """ Checks that order is updated with relevant combo item """

        self.test_order.grand_total = 0
        c1 = Food_Combo.objects.create(id=1, name='test_combo1', price=20.00)
        c2 = Food_Combo.objects.create(id=2, name='test_combo2', price=40.00)

        # combo instance follows structure as found in food order
        save_to_orderlineitem(
            'c998', [c1.id, 1, {'1': 3, '2': 5}], self.test_order)
        save_to_orderlineitem(
            'c999', [c2.id, 2, {'1': 4, '2': 6}], self.test_order)

        # Check combo ids, names & quantities updated
        self.assertEqual(
            [line.combo_id for line in self.test_order.lineitems.all()],
            ['c998', 'c999']
            )
        self.assertEqual(
            [line.combo_item.name for line in self.test_order.lineitems.all()],
            ['test_combo1', 'test_combo2'])
        self.assertEqual(
            [line.combo_quantity for line in self.test_order.lineitems.all()],
            [1, 2])

        # Check food items total purchased correctly updated using
        # total purchased += food_item.qty * combo_qty
        self.assertEqual(Food_Item.objects.get(id='1').total_purchased, 11)
        self.assertEqual(Food_Item.objects.get(id='2').total_purchased, 17)

        # Price is updated correctly
        self.assertEqual(
            float(self.test_order.grand_total),
            c1.price + (c2.price * 2) + settings.DELIVERY_FEE
            )

    def test_get_discount_returns_msg(self):
        """ Deals with orders whereby the order contains only combos and/or non-
        category 1 items """

        doughnuts = Food_Category.objects.create(id='2', name='doughnuts')
        Food_Item.objects.create(
            id='3', name='ice_glazed', price=2.99,
            description="extremely delicious", category=doughnuts)

        food_order = {'3': 2, 'c195': [1, 4, {'1': 4, '2': 1}]}

        self.assertIsInstance(get_discount(food_order), str)

    def test_get_discount_returns_value(self):
        """ Deals with orders containing category 1 items in non combos"""

        food_order = {'1': 3, '2': 3}
        self.assertEqual(float(get_discount(food_order)), 0.99)

    def test_set_order_form(self):
        """ Assigns the appropriate form class to the dataset given as an
        argument """

        self.assertIsInstance(set_order_form(
            self.checkout_data, True), OrderFormCollection)
        self.assertIsInstance(
            set_order_form(self.checkout_data, False), OrderFormDelivery)

    def test_collect_or_delivery(self):
        """ Check renders collect_or_delivery.html """

        response = self.client.post('/checkout/collect_or_delivery/')
        self.assertTemplateUsed(response, 'checkout/collect_or_delivery.html')

    def test_get_sent_info(self):
        """ Check correct address string is returned based on form fields
        completed """

        self.test_order.address_line1 = self.test_member.saved_address_line1
        self.test_order.address_line2 = self.test_member.saved_address_line2
        self.test_order.postcode = self.test_member.saved_postcode

        self.assertEqual(
            get_sent_info(self.test_order, True),
            "Available for collection from:\n\t20 Wardour St, " +
            "\n\tWest End,\n\tLondon,\n\tW1D 6QG"
            )
        self.assertEqual(
            get_sent_info(self.test_order, False),
            "Sent to:\n\t3764 Elvis Presley Boulevard," +
            "\n\tMemphis, Tennessee,\n\tTN 38116\n\t"
            )

        self.test_order.address_line2 = ''
        self.assertEqual(
            get_sent_info(self.test_order, False),
            "Sent to:\n\t3764 Elvis Presley Boulevard," +
            "\n\tTN 38116\n\t"
            )

    def test_checkout_success(self):
        """ Tests that order is saved to members profile and is displaying the
        correct info to template """

        self.client2.force_login(self.user2)
        session = self.client2.session
        session['food_order'] = {
            '1': 2,
            '2': 2
        }
        session.save()

        # Get order number assigned upon saving the order in checkout
        response = self.client2.post(
            '/checkout/success/'+self.test_order.order_number)

        # Check order is in context
        self.assertEqual(response.context['order'], self.test_order)

        # Check order is saved to member's profile if logged in
        self.assertEqual(response.context[
            'order'].member_profile, self.test_member2)

        # Check food order session variable is cleared after successful order
        self.assertFalse('food_order' in self.client2.session.keys())

        # Check template successfully rendered
        self.assertTemplateUsed(response, 'checkout/checkout_success.html')
