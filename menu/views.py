from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from .models import Food_Item, Food_Category, Food_Combo
from django.core import serializers
import itertools


# Create your views here.
def menu(request):
    """ A view to reveal the menu items """
    items = Food_Item.objects.all()
    category = request.GET['category']
    categories = request.GET['category'].split(',')

    if 'popular' == category:
        """ Gets the most popular of 4 main categories and joins the queryset together """
        burger_items = items.filter(category__name='burgers').order_by('-total_purchased')[:5]
        side_items = items.filter(category__name='sides').order_by('-total_purchased')[:2]
        drink_items = items.filter(category__name='drinks').order_by('-total_purchased')[:2]
        dessert_items = items.filter(category__name='dessert').order_by('-total_purchased')[:1]
        items = list(itertools.chain(burger_items, side_items, drink_items, dessert_items))
    else:
        if 'category' in request.GET:
            items = items.filter(category__name__in=categories)

    categories = Food_Category.objects.filter(name__in=categories)

    context = {
        'items': items,
        'selected_category': categories,
    }
    counter = 0
    for item in items:
        counter += 1

    return render(request, 'menu/menu_items.html', context)


def sort_items(request):
    """ A view to reveal the filtered menu items """

    items = Food_Item.objects.all()
    category = request.GET.get('category')
    items = items.filter(category__name=category)

    if request.is_ajax and request.method == "GET":
        sortkey = request.GET.get('sort_key')

    if sortkey == 'price-asc':
        items = items.order_by('price')
    if sortkey == 'price-desc':
        items = items.order_by('-price')

    sorted_items_ser = serializers.serialize('json', items)
    data = {"items": sorted_items_ser, 'selected_category': category}
    return JsonResponse(data, status=200)


def combo(request):
    """ A view to reveal the menu items """

    combos = Food_Combo.objects.all()
    # Create an instance of each combo
    combo1 = Food_Combo.objects.get(pk=1)
    combo2 = Food_Combo.objects.get(pk=2)
    combo3 = Food_Combo.objects.get(pk=3)

    # Get items belonging to each combo set and split them into categories
    # listed in alphabetical order
    c1_burgers = combo1.food_items.filter(category__name='burgers').order_by('name')
    c1_sides = combo1.food_items.filter(category__name='sides').order_by('name')
    c1_drinks = combo1.food_items.filter(category__name='drinks').order_by('name')

    c2_burgers = combo2.food_items.filter(category__name='burgers').order_by('name')
    c2_sides = combo2.food_items.filter(category__name='sides').order_by('name')
    c2_drinks = combo2.food_items.filter(category__name='drinks').order_by('name')

    c3_burgers = combo3.food_items.filter(category__name='burgers').order_by('name')
    c3_sides = combo3.food_items.filter(category__name='sides').order_by('name')
    c3_drinks = combo3.food_items.filter(category__name='drinks').order_by('name')
    c3_dessert = combo3.food_items.filter(category__name='dessert').order_by('name')
    
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


def get_item(request):
    item_id = request.GET.get('food_id')
    item = Food_Item.objects.filter(pk=item_id) 
    item_ser = serializers.serialize('json', item)

    return JsonResponse(item_ser, status=200, safe=False)
