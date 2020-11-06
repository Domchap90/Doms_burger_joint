from django.test import TestCase, Client
from .models import Food_Item, Food_Combo, Food_Category
from .views import get_popular_items, sort_items, join_queries
from django.urls import reverse


class TestMenuView(TestCase):

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

    def test_menu(self):
        # Check when url takes extra keyword argument it returns correct
        # template and status code
        response = self.client.get('%s?category=burgers' % reverse('menu'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'menu/menu_items.html')

        # returns correct context to template
        self.assertQuerysetEqual(response.context['selected_category'],
                                 ["<Food_Category: burgers>"], ordered=False)
        self.assertQuerysetEqual(
            response.context['items'],
            ["<Food_Item: test_food_item1>", "<Food_Item: test_food_item2>"],
            ordered=False)

        response2 = self.client.get('%s?category=popular' % reverse('menu'))
        self.assertQuerysetEqual(response2.context['selected_category'],
                                 ["<Food_Category: popular>"], ordered=False)
        # returns correctly sorted items for popular category: top 3 burgers,
        # top side, top drink, top dessert
        popular_item_ids = []
        for item in response2.context['items']:
            popular_item_ids.append(item.id)
        self.assertEqual(popular_item_ids, [4, 3, 2, 6, 8, 10])

    def test_get_popular_items(self):
        # Case where max number of items exist - 3 burgers, 1 side,
        # 1 drink & 1 dessert should be outputted by function.
        test_items = Food_Item.objects.all()
        result = get_popular_items(test_items)
        self.assertEqual(len(result), 6)
        result_ordered_item_ids = []
        for item in result:
            result_ordered_item_ids.append(item.id)
        self.assertEqual(result_ordered_item_ids, [4, 3, 2, 6, 8, 10])

        # Case where 6 items don't exist - 1 vegetarian burger, 2 sides &
        # 1 drink to be sorted
        test_items2 = Food_Item.objects.filter(id__range=(4, 7))
        result2 = get_popular_items(test_items2)
        self.assertEqual(len(result2), 3)
        result2_ordered_item_ids = []
        for item in result2:
            result2_ordered_item_ids.append(item.id)
        self.assertEqual(result2_ordered_item_ids, [4, 6, 7])

        # Case where NO items exist
        test_items3 = Food_Item.objects.filter(id__range=(19, 20))
        result3 = get_popular_items(test_items3)

        self.assertEqual(len(result3), 0)
        result3_ordered_item_ids = []
        for item in result3:
            result3_ordered_item_ids.append(item.id)
        self.assertEqual(result3_ordered_item_ids, [])

    def test_sort_items(self):
        client = Client()
        request = client.get("sort/", {"sort_key": "price_asc",
                                       "category": "dessert"}, format='json')
        sorted_dessert_items = Food_Item.objects.filter(
            category__name='dessert').order_by('price')
        self.assertGreater(sorted_dessert_items[1].price, sorted_dessert_items[0].price)

        request = self.client.get("sort/", {"sort_key": "price_desc",
                                            "category": "vegetarian"}, format='json')

        sorted_vegetarian_items = Food_Item.objects.filter(
            category__name='vegetarian').order_by('-price')
        self.assertGreater(sorted_vegetarian_items[0].price, 
                           sorted_vegetarian_items[1].price)

    def test_combo(self):
        response = self.client.post(reverse('combo'))
        self.assertTemplateUsed(response, 'menu/combo_items.html')

        # Test context output for burgers
        c1_burgers = []
        for burger in response.context['combo1_burgers']:
            c1_burgers.append(burger.id)
        c2_burgers = []
        for burger in response.context['combo2_burgers']:
            c2_burgers.append(burger.id)
        c3_burgers = []
        for burger in response.context['combo3_burgers']:
            c3_burgers.append(burger.id)

        self.assertEqual(c1_burgers, [2, 4])
        self.assertEqual(c2_burgers, [1, 3])
        self.assertEqual(c3_burgers, [1, 2, 3, 4])

        # Test context output for sides
        c1_sides = []
        for side in response.context['combo1_sides']:
            c1_sides.append(side.id)
        c2_sides = []
        for side in response.context['combo2_sides']:
            c2_sides.append(side.id)
        c3_sides = []
        for side in response.context['combo3_sides']:
            c3_sides.append(side.id)

        self.assertEqual(c1_sides, [6])
        self.assertEqual(c2_sides, [5])
        self.assertEqual(c3_sides, [5, 6])

        # Test context output for drinks
        c1_drinks = []
        for drink in response.context['combo1_drinks']:
            c1_drinks.append(drink.id)
        c2_drinks = []
        for drink in response.context['combo2_drinks']:
            c2_drinks.append(drink.id)
        c3_drinks = []
        for drink in response.context['combo3_drinks']:
            c3_drinks.append(drink.id)

        self.assertEqual(c1_drinks, [8])
        self.assertEqual(c2_drinks, [7])
        self.assertEqual(c3_drinks, [7, 8])

        # Test context output for desserts
        c3_dessert = []
        for dessert in response.context['combo3_dessert']:
            c3_dessert.append(dessert.id)

        # order of food items is reversed due to ordering by name in the combo
        # view food_item'1'0 comes before food_item'9'
        self.assertEqual(c3_dessert, [10, 9])

    def test_join_queries(self):
        test_items = Food_Item.objects.all()
        dessert_and_sides = join_queries(test_items, 'dessert', 'sides')
        result_ids = []
        for item in dessert_and_sides:
            result_ids.append(item.id)
        self.assertEqual(result_ids, [5, 6, 9, 10])

        no_categories = join_queries(test_items, '', '')
        result_ids = []
        for item in no_categories:
            result_ids.append(item.id)
        self.assertEqual(result_ids, [])

    # def test_get_item(self):
