from django.shortcuts import render
from .models import Food_Item

# Create your views here.


def menu(request):
    """ A view to reveal the menu items """

    items = Food_Item.objects.all()

    context = {
        'items': items,
    }

    return render(request, 'menu/menu_items.html', context)
