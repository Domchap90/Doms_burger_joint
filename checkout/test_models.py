from django.test import TestCase
from .models import Order, OrderLineItem, ComboLineItem
from menu.models import Food_Item, Food_Category, Food_Combo
from django.conf import settings


class TestCheckoutModel(TestCase):
    def setUp(self):
        self.item1 = Food_Item.objects.create(id=1, name='item1', price=3.50)
        self.item2 = Food_Item.objects.create(id=2, name='item2', price=2.00)
        self.combo = Food_Combo.objects.create(id=1, name='combo1', price=10.00)

        self.order = Order.objects.create(name='testname1')
        self.order2 = Order.objects.create(name='testname2')
        self.order3 = Order.objects.create(name='testname3')

        # create orderline items
        self.oli = OrderLineItem.objects.create(order=self.order, food_item=self.item1, quantity=1)
        self.oli2 = OrderLineItem.objects.create(order=self.order, combo_item=self.combo, combo_quantity=1, combo_id='c111')

    def test_update_total(self):
        self.assertEqual(self.order.grand_total, self.item1.price + self.combo.price + settings.DELIVERY_FEE)
        self.assertEqual(self.order2.grand_total, 0)

    def test_order_save(self):
        self.order.order_number = None

        self.order.save()
        # Check order number has changed after saving
        self.assertNotEqual(self.order.order_number, None)

        # uuid outputs 128 bit string
        self.assertEqual(len(self.order.order_number), 32)
        self.assertIsInstance(self.order.order_number, str)

    def test_order_string_method(self):
        self.assertEqual(str(self.order), self.order.order_number)

    def test_changeform_link(self):
        # Assess the change link in admin page for the Order returns correct url
        self.assertEqual(
            self.oli2.changeform_link(),
            '<a href="/admin/checkout/orderlineitem/2/change/" target="_blank">See Contents</a>'
            )

    def test_orderlineitem_save(self):
        self.oli.quantity = 3

        # Quantity hasn't been updated until the save method is executed
        self.assertNotEqual(self.oli.lineitem_total,  self.oli.quantity * self.oli.food_item.price)

        self.oli.save()
        self.assertEqual(self.oli.lineitem_total,  self.oli.quantity * self.oli.food_item.price)

    def test_orderlineitem_string_method(self):
        # Check individual item in order line item is stringed correctly
        self.assertEqual(str(self.oli), 'Item Id 1 on order ' + self.order.order_number)

        # Check Combo item in order line item is stringed correctly
        self.assertEqual(str(self.oli2), 'Combo Id 1 on order ' + self.order.order_number)

    def test_combolineitem_string_method(self):
        self.cli = ComboLineItem.objects.create(combo=self.oli2, food_item=self.item1, quantity=1)
        self.cli2 = ComboLineItem.objects.create(combo=self.oli2, food_item=self.item2, quantity=2)

        # Check method returns the correct string pattern
        self.assertEqual(str(self.cli), 'Food item Id: '+str(self.item1.pk)+' added to combo '+self.oli2.combo_id)
        self.assertEqual(str(self.cli2), 'Food item Id: '+str(self.item2.pk)+' added to combo '+self.oli2.combo_id)
