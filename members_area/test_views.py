from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from menu.models import Food_Category, Food_Combo, Food_Item
from .models import MemberProfile
from checkout.models import Order, OrderLineItem, ComboLineItem


class TestMembersAreaView(TestCase):

    def setUp(self):
        # Create test food categories
        categories = ['burgers', 'vegetarian', 'sides', 'drinks', 'dessert',
                      'popular']
        for counter, cat in enumerate(categories, 1):
            Food_Category.objects.create(pk=counter, name=cat)

        # Create test food items
        category_id = 1
        price = 10.00
        # Creates 2 food items for each category all with differing total
        # purchased amounts
        for item in range(1, 11):
            category = Food_Category.objects.get(pk=category_id)
            Food_Item.objects.create(
                pk=item, name="test_food_item"+str(item),
                description="This is a description of food item"+str(item),
                price=price, category=category, total_purchased=item
                )

            price += 1.00
            if item % 2 == 0:
                category_id += 1

        # Create test food combos
        combos = ['combo1', 'combo2', 'combo3']
        for counter, combo in enumerate(combos, 1):
            price = counter * 15.00
            Food_Combo.objects.create(
                pk=counter, name=combo,
                description="This is a description of "+combo, price=price
                )

        # Assign food items with even ids to combo 1
        combo1 = Food_Combo.objects.get(pk=1)
        combo1.food_items.set([2, 4, 6, 8, 10])
        # Assign food items with odd ids to combo 2
        combo2 = Food_Combo.objects.get(pk=2)
        combo2.food_items.set([1, 3, 5, 7, 9])
        # Assign all food items to combo 3
        combo3 = Food_Combo.objects.get(pk=3)
        combo3.food_items.set([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

        # Create test users
        self.user = User.objects.create_user(
            username='john_wick', email='johnwick@badass.com',
            password='love_dog'
            )

        self.user2 = User.objects.create_user(
            username='indiana_jones', email='dr_jones@archaeologist.com',
            password='whipit'
            )

        self.test_member = MemberProfile.objects.get(member=self.user2)

        # Create test orders for user 2 (for order history test)
        self.test_order1 = Order.objects.create(
            order_number='1234', member_profile=self.test_member,
            name='Indy', email='', mobile_number=''
        )
        self.test_order1.save()

        self.test_order2 = Order.objects.create(
            order_number='1235', member_profile=self.test_member,
            name='Indy', email='', mobile_number=''
        )
        self.test_order2.save()

        # create orderline items for order test_order1 ('1234')
        test_food_4 = Food_Item.objects.get(pk=4)
        test_food_9 = Food_Item.objects.get(pk=9)

        test_oli_1 = OrderLineItem.objects.create(
            order=self.test_order1, food_item=test_food_4, quantity=1)
        test_oli_1.save()

        test_oli_2 = OrderLineItem.objects.create(
            order=self.test_order1, food_item=test_food_9, quantity=3)
        test_oli_2.save()

        # create orderline items for order test_order2 ('1235')
        test_food_1 = Food_Item.objects.get(pk=1)
        test_food_3 = Food_Item.objects.get(pk=3)
        test_food_8 = Food_Item.objects.get(pk=8)

        self.test_oli_3 = OrderLineItem.objects.create(
            order=self.test_order2, food_item=test_food_1, quantity=5)
        self.test_oli_3.save()

        self.test_oli_4 = OrderLineItem.objects.create(
            order=self.test_order2, combo_id='c123', combo_item=combo2,
            combo_quantity=1
            )
        self.test_oli_4.save()

        self.test_oli_5 = OrderLineItem.objects.create(
            order=self.test_order2, combo_id='c234', combo_item=combo3,
            combo_quantity=2
            )
        self.test_oli_5.save()

        # create comboline items for orderline test_oli_4
        self.test_cli_1 = ComboLineItem.objects.create(
            combo=self.test_oli_4, food_item=test_food_9, quantity=1
        )
        self.test_cli_1.save()
        self.test_cli_2 = ComboLineItem.objects.create(
            combo=self.test_oli_4, food_item=test_food_3, quantity=2
        )
        self.test_cli_2.save()

        # create comboline items for orderline test_oli_5
        self.test_cli_3 = ComboLineItem.objects.create(
            combo=self.test_oli_5, food_item=test_food_4, quantity=1
        )
        self.test_cli_3.save()
        self.test_cli_4 = ComboLineItem.objects.create(
            combo=self.test_oli_5, food_item=test_food_8, quantity=1
        )
        self.test_cli_4.save()

    def test_members_area(self):
        """ Test case where user has no order history or saved delivery
        details """

        # log user in to get linked form and order attributes
        self.client.force_login(self.user)
        url = '/members_area/'
        response = self.client.post(url)

        self.assertTemplateUsed(response, 'members_area/profile_page.html')
        # Check context contains empty form from view
        self.assertEqual(
            [field.value() for field in response.context['memberform']],
            [None for _ in range(6)]
            )

        # Check order history has NO orders inside it
        self.assertEqual(len(response.context['order_history']), 0)

        """ Test case where user has an order history and saved delivery
        details """

        # Update member form details to be posted
        data = {'saved_email': 'dr_jones@archaeologist.com',
                'saved_mobile_number': '07777 777 777',
                'saved_postcode': 'SE10 9UX',
                'saved_address_line1': '23 sunshine lane',
                'saved_delivery_instructions': 'Come round back'}

        self.client.force_login(self.user2)
        response = self.client.post(url, data)

        # Check Member's delivery details are updated correctly on the form
        self.assertEqual(
            [field.value() for field in response.context['memberform']],
            ['dr_jones@archaeologist.com', '07777 777 777', 'SE10 9UX',
             '23 sunshine lane', None, 'Come round back'])

        # Format response context data into 3 lists
        order_info = []
        orderline_info = []
        comboline_info = []
        for order in response.context['order_history']:
            order_info.extend(
                [order.order_number, order.order_count,
                 float(order.grand_total)]
            )
            for line in order.lineitems.all():
                if line.food_item:
                    orderline_info.extend([line.food_item.name, line.quantity])
                else:
                    orderline_info.extend(
                        [line.combo_item.name, line.combo_quantity]
                        )
                    for c_line in line.combocontents.all():
                        comboline_info.extend(
                            [c_line.food_item.name, c_line.quantity]
                            )

        # Check top level of orders are as follows:
        # order num= 1235, order count= 8, grand_total= 171.99 &
        # order num= 1234, order count= 4, grand_total= 68.99
        self.assertEqual(order_info, ['1235', 8, 171.99, '1234', 4, 68.99])

        # Check second level of orders are as follows:
        self.assertEqual(
            orderline_info,
            ['test_food_item1', 5, 'combo2', 1, 'combo3', 2, 'test_food_item4',
             1, 'test_food_item9', 3]
            )

        # Check third level of orders are as follows:
        self.assertEqual(
            comboline_info,
            ['test_food_item9', 1, 'test_food_item3', 2, 'test_food_item4', 1,
             'test_food_item8', 1]
            )

        # Check returns correct status code and renders correct template
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'members_area/profile_page.html')

    def test_rewards(self):
        url = '/members_area/rewards/'
        response = self.client.post(url)
        self.assertTemplateUsed(response, 'members_area/rewards.html')
        self.assertEqual(response.status_code, 200)

    def test_repeat_order(self):
        """ Tests order to be repeated successfully changes the session
        variable food_order & redirects to checkout """

        url = '/members_area/repeat_order/'
        data = {'order_id': self.test_order2.order_number}

        self.client.session['food_order'] = {
            'c112': [3, 1, {'1': 1, '5': 2, '8': 3}],
            '5': 2,
            '10': 1
        }

        response = self.client.post(url, data)
        food_order = self.client.session.get('food_order')

        # Check redirects to checkout page
        self.assertRedirects(response, reverse('checkout'))

        # Check initial session variable order is cleared and order with the
        # id selected, is added to session variable food_order
        self.assertEqual(food_order, {'1': 5, 'c123': [2, 1, {'9': 1, '3': 2}],
                                      'c234': [3, 2, {'4': 1, '8': 1}]})
