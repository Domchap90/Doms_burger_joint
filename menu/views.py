from django.shortcuts import render
from django.template.loader import render_to_string
from django.http import HttpResponse, JsonResponse
from .models import Food_Item, Food_Category


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

    # categories = request.GET['category'].split(',')
    # items = Food_Item.objects.all().filter(category__name__in=categories)
    # categories = Food_Category.objects.filter(name__in=categories)

    context = {
        'items': items,
        'selected_category': categories,
    }

    return render(request, 'menu/menu_items.html', context)


def sort_items(request):
    """ A view to reveal the filtered menu items """

    items = Food_Item.objects.all()
    category = request.GET.get('category')

    print('request.is_ajax = '+str(request.is_ajax))

    #if request.is_ajax and request.method == "GET":
    sortkey = request.GET.get('sort_key')
    print("sortkey = "+str(sortkey))

    if sortkey == 'price-asc':
        print("price-asc is sortkey")
        items = items.order_by('price')
    if sortkey == 'price-desc':
        items = items.order_by('-price')
        print("price-desc is sortkey")
    
    context = {
        'items': items,
        'selected_category': category,
    }
    for item in items:
        print("price of item: "+str(item.price))

    return render(request, 'menu/menu_items.html', context)
    #return JsonResponse('menu/menu_items.html', context)
