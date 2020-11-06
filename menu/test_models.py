from django.test import TestCase
from .models import Food_Item, Food_Combo, Food_Category


class TestMenuModel(TestCase):

    def test_defaults(self):
        item = Food_Item.objects.create(name='test_item', price=10)
        # Check total purchased is initiated to a value of 0
        self.assertEqual(item.total_purchased, 0)

    def test_string_methods(self):
        test_item = Food_Item.objects.create(name='banana', price=0.99,
                                             description='yellow and curvy')
        test_category = Food_Category.objects.create(name='fruit',
                                                     friendly_name='Fruit')
        test_combo = Food_Combo.objects.create(
            name='basket', description='A lovely collection of treats',
            price=20.00)

        # Check outputs instance of object to its name when the string of
        # instance is called
        self.assertEqual(str(test_item), 'banana')
        self.assertEqual(str(test_category), 'fruit')
        self.assertEqual(str(test_combo), 'basket')

        # Check category friendly name
        self.assertEqual(test_category.friendly_name, 'Fruit')

    def test_verbose_name_plural(self):
        self.assertEqual(str(Food_Category._meta.verbose_name_plural),
                         'Food_Categories')
