from django.shortcuts import render
from django.http import JsonResponse
from .models import Food_Item, Food_Category, Food_Combo
from django.core import serializers
import itertools


def menu(request):
    """ A view to reveal the menu items """
    items = Food_Item.objects.all()
    category = request.GET['category']
    categories = request.GET['category'].split(',')

    if category == 'popular':
        items = get_popular_items(items)
    else:
        if 'category' in request.GET:
            items = items.filter(category__name__in=categories)

    categories = Food_Category.objects.filter(name__in=categories)

    context = {
        'items': items,
        'selected_category': categories,
    }

    return render(request, 'menu/menu_items.html', context)


def get_popular_items(all_items):
    """ Gets the most popular of 4 main categories and joins the queryset
    together """
    burgers = join_queries(all_items, 'burgers', 'vegetarian')
    burger_items = burgers.order_by('-total_purchased')[:3]
    side_items = all_items.filter(category__name='sides').order_by(
        '-total_purchased')[:1]
    drink_items = all_items.filter(category__name='drinks').order_by(
        '-total_purchased')[:1]
    dessert_items = all_items.filter(category__name='dessert').order_by(
        '-total_purchased')[:1]

    items = list(itertools.chain(burger_items, side_items, drink_items,
                 dessert_items))

    return items


def sort_items(request):
    """ GET Ajax call made to view, returns sorted results according to the
    data sent """

    items = Food_Item.objects.all()
    category = request.GET.get('category')
    items = items.filter(category__name=category)

    if request.is_ajax and request.method == "GET":
        sortkey = request.GET.get('sort_key')

    if sortkey == 'price_asc':
        items = items.order_by('price')
    if sortkey == 'price_desc':
        items = items.order_by('-price')

    sorted_items_ser = serializers.serialize('json', items)
    data = {"items": sorted_items_ser, 'selected_category': category}
    return JsonResponse(data, status=200)


def combo(request):
    """ A view to reveal the combo items """

    combos = Food_Combo.objects.all()
    # Create an instance of each combo
    combo1 = Food_Combo.objects.get(pk=1)
    combo2 = Food_Combo.objects.get(pk=2)
    combo3 = Food_Combo.objects.get(pk=3)

    # Get items belonging to each combo set and split them into categories
    # listed in alphabetical order
    c1_burgers_unordered = join_queries(combo1.food_items, 'burgers',
                                        'vegetarian')
    c1_burgers = c1_burgers_unordered.order_by('name')
    c1_sides = combo1.food_items.filter(category__name='sides').order_by(
        'name')
    c1_drinks = combo1.food_items.filter(category__name='drinks').order_by(
        'name')

    c2_burgers_unordered = join_queries(combo2.food_items, 'burgers',
                                        'vegetarian')
    c2_burgers = c2_burgers_unordered.order_by('name')
    c2_sides = combo2.food_items.filter(category__name='sides').order_by(
        'name')
    c2_drinks = combo2.food_items.filter(category__name='drinks').order_by(
        'name')

    c3_burgers_unordered = join_queries(combo3.food_items, 'burgers',
                                        'vegetarian')
    c3_burgers = c3_burgers_unordered.order_by('name')
    c3_sides = combo3.food_items.filter(category__name='sides').order_by(
        'name')
    c3_drinks = combo3.food_items.filter(category__name='drinks').order_by(
        'name')
    c3_dessert = combo3.food_items.filter(category__name='dessert').order_by(
        'name')
    
    context = {
        'combos': combos,
        'combo1_burgers': c1_burgers,
        'combo1_sides': c1_sides,
        'combo1_drinks': c1_drinks,
        'combo2_burgers': c2_burgers,
        'combo2_sides': c2_sides,
        'combo2_drinks': c2_drinks,
        'combo3_burgers': c3_burgers,
        'combo3_sides': c3_sides,
        'combo3_drinks': c3_drinks,
        'combo3_dessert': c3_dessert,
    }

    return render(request, 'menu/combo_items.html', context)


def join_queries(objects, category_1, category_2):
    """ Effectively combines all objects from two categories together """
    query_1 = objects.filter(category__name=category_1)
    query_2 = objects.filter(category__name=category_2)
    joined_query = query_1 | query_2

    return joined_query


def get_item(request):
    """ Ajax call asking for item object details from id """
    item_id = request.GET.get('food_id')
    item = Food_Item.objects.filter(pk=item_id)
    item_ser = serializers.serialize('json', item)

    return JsonResponse(item_ser, status=200, safe=False)
