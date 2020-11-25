from django.test import TestCase
from menu.models import Food_Item, Food_Combo
from .models import Order, OrderLineItem, ComboLineItem


class TestCheckoutSignals(TestCase):

    def setUp(self):
        # Create test items & combo to setup
        self.item1 = Food_Item.objects.create(
            id=1, name='item1', price=3.50, total_purchased=10)
        self.item2 = Food_Item.objects.create(
            id=2, name='item2', price=2.00, total_purchased=5)
        self.combo = Food_Combo.objects.create(
            id=1, name='combo1', price=10.00)

        self.order = Order.objects.create(name='testname1')

        # create orderline items
        self.oli = OrderLineItem.objects.create(
            order=self.order, food_item=self.item1, quantity=1)
        self.oli2 = OrderLineItem.objects.create(
            order=self.order, combo_item=self.combo, combo_quantity=1,
            combo_id='c111')

    def test_update_orderline_after_save(self):
        self.assertEqual(self.order.order_total, 13.50)
        self.assertEqual(Food_Item.objects.get(id=1).total_purchased, 11)

    def test_update_comboline_after_save(self):
        self.cli = ComboLineItem.objects.create(
            combo=self.oli2, food_item=self.item1, quantity=1)
        self.cli2 = ComboLineItem.objects.create(
            combo=self.oli2, food_item=self.item2, quantity=2)

        # Food item's total purchased increases as expected
        self.assertEqual(Food_Item.objects.get(id=1).total_purchased, 12)
        self.assertEqual(Food_Item.objects.get(id=2).total_purchased, 7)

    def test_update_orderline_after_delete(self):
        # Upon deleting a lineitem the total is restored to its original value
        # in setup
        self.order.lineitems.get(id=1).delete()
        self.assertEqual(self.order.order_total, 10.00)
        # Similarly for total purchased
        self.assertEqual(Food_Item.objects.get(id=1).total_purchased, 10)

    def test_update_comboline_after_delete(self):
        self.cli = ComboLineItem.objects.create(
            combo=self.oli2, food_item=self.item1, quantity=1)
        self.cli2 = ComboLineItem.objects.create(
            combo=self.oli2, food_item=self.item2, quantity=2)

        self.order.lineitems.get(id=2).combocontents.get(id=2).delete()
        # After deleting only combline 2 with item 2 on it
        # total purchased for item 1 stays at 12 whilst item 2 drops to 5
        self.assertEqual(Food_Item.objects.get(id=1).total_purchased, 12)
        self.assertEqual(Food_Item.objects.get(id=2).total_purchased, 5)
