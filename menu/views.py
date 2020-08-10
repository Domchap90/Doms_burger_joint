from django.shortcuts import render
from django.http import JsonResponse
from .models import Food_Item, Food_Category
from django.core import serializers


# Create your views here.
def menu(request):
    """ A view to reveal the menu items """
    items = Food_Item.objects.all()
    categories = None

    if request.GET:
        if 'category' in request.GET:
            categories = request.GET['category'].split(',')
            items = items.filter(category__name__in=categories)
            categories = Food_Category.objects.filter(name__in=categories)

    context = {
        'items': items,
        'selected_category': categories,
    }

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
