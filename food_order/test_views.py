from django.test import TestCase, Client
from unittest.mock import patch
from django.urls import reverse
from menu.models import Food_Category, Food_Combo, Food_Item
from .templatetags.order_tools import get_subtotal


class TestFoodOrderView(TestCase):

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
                id=item, name="test_food_item"+str(item),
                description="This is a description of food item"+str(item),
                price=price, category=category, total_purchased=item)

            price += 1.00
            if item % 2 == 0:
                category_id += 1

        # Create test food combos
        combos = ['combo1', 'combo2', 'combo3']
        for counter, combo in enumerate(combos, 1):
            price = counter * 5.00
            Food_Combo.objects.create(
                pk=counter, name=combo,
                description="This is a description of "+combo, price=price)

        # Assign food items with even ids to combo 1
        combo1 = Food_Combo.objects.get(pk=1)
        combo1.food_items.set([2, 4, 6, 8, 10])
        # Assign food items with odd ids to combo 2
        combo2 = Food_Combo.objects.get(pk=2)
        combo2.food_items.set([1, 3, 5, 7, 9])
        # Assign all food items to combo 3
        combo3 = Food_Combo.objects.get(pk=3)
        combo3.food_items.set([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

    def test_food_order(self):
        self.c = Client()
        response = self.c.post(reverse('food_order'))
        self.assertTemplateUsed(response, 'food_order/order_items.html')

    def test_add_to_order(self):
        self.c = Client()
        data = {'redirect_url': '/menu/?category=burgers'}
        # Test Client adds item with id 1 to the otherwise empty order
        response = self.c.post('/food_order/add/1/', data)

        # Check session variable 'food_order' has been correctly updated
        food_order = self.c.session.get('food_order')
        self.assertEqual(food_order, {'1': 1})

        # Check the add to order view correctly redirects back to the menu page
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, data['redirect_url'])

        # Patches setup to intercept messages sent from view
        self._patcherS = patch('django.contrib.messages.success')
        self.mock_success_msg = self._patcherS.start()

        # Adds item 5 to non-empty order
        session = self.c.session
        session['food_order'] = {'5': 9}
        session.save()
        self.c.post('/food_order/add/5/', data, follow=True)

        # Check correct message sent after add button pressed with item
        # quantity UNDER upper limit (10)
        self.assertEqual(
            self.mock_success_msg.call_args[0][1],
            'Added "test_food_item5" to your order.')

        self._patcherS.stop()

        self._patcherE = patch('django.contrib.messages.error')
        self.mock_err_msg = self._patcherE.start()

        # then with item quantity ON upper limit
        self.c.post('/food_order/add/5/', data)
        self.assertEqual(
            self.mock_err_msg.call_args[0][1],
            'You have reached your order limit for "test_food_item5".')

        self._patcherE.stop()

    def test_add_combo_to_order(self):
        self.c = Client()
        data = {'redirect_url': '/menu/combo/', 'test_combo_item1': '4',
                'test_combo_item2': '6', 'test_combo_item3': '8'}
        # Test Client adds combo 1 with ids 3, 6, 7 to the otherwise empty
        # order
        response = self.c.post('/food_order/add_combo/1/', data)

        # Check session variable 'food_order' has been correctly updated
        food_order = self.c.session.get('food_order')
        self.assertEqual(food_order[list(food_order.keys())[0]],
                         [1, 1, {'4': 1, '6': 1, '8': 1}])
        # Check the add combo to order view correctly redirects back to the
        # combo deals page
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, data['redirect_url'])

        # Setup food order to contain combo id 2 ON the upper limit of 3
        session = self.c.session
        session['food_order'] = {'c999': [2, 3, {'1': 2, '5': 2, '7': 2}]}
        session.save()

        self._patcherE = patch('django.contrib.messages.error')
        self.mock_err_msg = self._patcherE.start()

        err_data = {
            'redirect_url': '/menu/combo/',
            'test_combo_item1': '4',
            'test_combo_item2': '4',
            'test_combo_item3': '6',
            'test_combo_item4': '6',
            'test_combo_item5': '8',
            'test_combo_item6': '8'
            }
        self.c.post('/food_order/add_combo/2/', err_data)
        # Check combo is NOT added
        self.assertEqual(
            self.mock_err_msg.call_args[0][1],
            'You have reached your order limit for "combo2".')

        # Setup food order to contain combo id 3 BELOW the upper limit of 5
        combo_key = 'c'+str(hash(str({'1': 1, '5': 2, '7': 1})))
        session['food_order'] = {combo_key: [3, 4, {'1': 1, '5': 2, '7': 1}]}
        session.save()

        self._patcherE.stop()
        self._patcherS = patch('django.contrib.messages.success')
        self.mock_success_msg = self._patcherS.start()

        success_data = {
            'redirect_url': '/menu/combo/',
            'test_combo_item1': '1',
            'test_combo_item2': '5',
            'test_combo_item3': '5',
            'test_combo_item4': '7',
        }
        # Add identical combo to check they are grouped correctly
        self.c.post('/food_order/add_combo/3/', success_data)
        self.assertEqual(
            self.mock_success_msg.call_args[0][1],
            'Added "combo3" to your order.')

        self.assertEqual(
            self.c.session.get('food_order'),
            {combo_key: [3, 5, {'1': 1, '5': 2, '7': 1}]})

    def test_remove_from_order(self):
        self.c = Client()
        session = self.c.session
        session['food_order'] = {'1': 5, '4': 2, '6': 3}
        session.save()

        # Check view can remove item 6 succesfully
        response = self.c.post('/food_order/remove/item/6/')
        self.assertEqual(self.c.session.get('food_order'), {'1': 5, '4': 2})

        # Check returns 200 http response
        self.assertEqual(response.status_code, 200)

        # combos in food order have the following structure:
        # combohashkey: [combo_id, combo_qty, {item_id: item_qty, ...}]
        session['food_order'] = {'c234': [2, 1, {'3': 1, '8': 2, '2': 1}],
                                 'c123': [1, 2, {'4': 1, '5': 1, '9': 1}],
                                 'c345': [3, 1, {'1': 2, '4': 2, '6': 1}]}
        session.save()
        data = {'comboHashKey': 'c234'}

        # Check view can remove combo with hashkey c234 and id 2 succesfully
        response = self.c.post('/food_order/remove/combo/2/', data)
        self.assertEqual(
            self.c.session.get('food_order'), {
                'c123': [1, 2, {'4': 1, '5': 1, '9': 1}],
                'c345': [3, 1, {'1': 2, '4': 2, '6': 1}]
                })

        # Check again returns 200 http response
        self.assertEqual(response.status_code, 200)

    def test_edit_order(self):
        self.c = Client()
        session = self.c.session
        session['food_order'] = {'5': 5, '7': 2, '6': 1}
        session.save()
        data = {'newQtyVal': 3, 'oldQtyVal': 2}
        response = self.c.post('/food_order/edit_item/item/7/', data)

        # Check value has been updated in food order
        self.assertEqual(self.c.session.get('food_order'),
                         {'5': 5, '7': 3, '6': 1})
        self.assertEqual(response.status_code, 200)

        # Check values of subtotal and subtotal changed are correct
        edit_item = Food_Item.objects.get(pk=7)
        subtotal = edit_item.price * data['newQtyVal']
        subtotal_change = (
            data['newQtyVal'] - data['oldQtyVal']) * edit_item.price

        self.assertJSONEqual(str(response.content, encoding='utf8'),
                             {"subtotal": str(subtotal),
                             "subtotal_change": str(subtotal_change)})

        # Check for combo edit
        session['food_order'] = {'c678': [2, 4, {'1': 1, '5': 2, '6': 1}],
                                 'c789': [1, 8, {'2': 1, '3': 1, '4': 1}],
                                 'c891': [3, 3, {'6': 2, '7': 2, '9': 1}]}
        session.save()
        data = {'comboHashKey': 'c789', 'newQtyVal': 6, 'oldQtyVal': 8}
        response = self.c.post('/food_order/edit_item/combo/1/', data)

        # Check value has been updated in food order: food_order['c789'][1] = 6
        self.assertEqual(self.c.session.get('food_order'),
                         {'c678': [2, 4, {'1': 1, '5': 2, '6': 1}],
                          'c789': [1, 6, {'2': 1, '3': 1, '4': 1}],
                          'c891': [3, 3, {'6': 2, '7': 2, '9': 1}]})
        self.assertEqual(response.status_code, 200)

        # Check values of subtotal and subtotal changed for combo
        edit_combo = Food_Combo.objects.get(pk=1)
        subtotal = edit_combo.price * data['newQtyVal']
        subtotal_change = (
            data['newQtyVal'] - data['oldQtyVal']) * edit_combo.price

        self.assertJSONEqual(str(response.content, encoding='utf8'),
                             {"subtotal": str(subtotal),
                              "subtotal_change": str(subtotal_change)})

    def test_recalculate_remaining_delivery_amount(self):
        self.c = Client()

        # Test when total > delivery threshold whose value is given in
        # settings.py of 15.00
        data = {'total': 20.00}
        response = self.c.get(
            '/food_order/recalculate_remaining_delivery_amount/', data)

        # IF total < threshold: remaining delivery amount is the difference
        # between them, otherwise 0
        self.assertJSONEqual(str(response.content, encoding='utf8'),
                             {'remaining_delivery_amount': 0.00})
        self.assertEqual(response.status_code, 200)

        # Test when total = delivery threshold
        data = {'total': 15.00}
        response = self.c.get(
            '/food_order/recalculate_remaining_delivery_amount/', data)
        self.assertJSONEqual(str(response.content, encoding='utf8'), {
            'remaining_delivery_amount': 0.00})
        self.assertEqual(response.status_code, 200)

        # Test when total < delivery threshold
        data = {'total': 10.00}
        response = self.c.get(
            '/food_order/recalculate_remaining_delivery_amount/', data)
        self.assertJSONEqual(str(response.content, encoding='utf8'),
                             {'remaining_delivery_amount': 5.00})
        self.assertEqual(response.status_code, 200)

    def test_get_subtotal(self):
        self.assertEqual(get_subtotal(10.99, 5), 54.95)
