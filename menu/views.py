from django.shortcuts import render
from .models import Food_Item, Food_Category

# Create your views here.


def menu(request):
    """ A view to reveal the menu items """

    items = Food_Item.objects.all()

    if request.GET:
        if 'category' in request.GET:
            categories = request.GET['category'].split(',')
            items = items.filter(category__name__in=categories)
            categories = Food_Category.objects.filter(name__in=categories)

    context = {
        'items': items,
        'selected_categories': categories,
    }

    return render(request, 'menu/menu_items.html', context)
