from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages

from menu.models import Food_Item, Food_Combo
# Create your views here.


def food_order(request):
    """ Order page view """

    return render(request, 'food_order/order_items.html')


def add_to_order(request, item_id):
    """ Add a quantity of the specified product to the food order """
    food_item = get_object_or_404(Food_Item, pk=item_id)
    redirect_url = request.POST.get('redirect_url')

    order = request.session.get('food_order', {})
    print(order.keys())

    if item_id in list(order.keys()):
        if order[item_id] < 10:
            order[item_id] += 1
            messages.success(request, f'Added {food_item.name} to your order.')
        else:
            messages.error(request, f'You have reached your order limit for {food_item.name}.')
    else:
        order[item_id] = 1
        messages.success(request, f'Added {food_item.name} to your order.')
    request.session['food_order'] = order

    return redirect(redirect_url)


def add_combo_to_order(request, combo_id):
    """ Adds combo to order object as a list within a list of all
        the matching combos """

    form = request.POST.dict()
    order = request.session.get('food_order', {})
    redirect_url = request.POST.get('redirect_url')
    # combo_item = get_object_or_404(Food_Combo, pk=combo_id)
    # combo_key = 'combo_'+str(combo_id)
    # if combo_key not in list(order.keys()):
    #     order[combo_key] = []
    # combo_to_append = []

    combo_to_append = {}

    for field in form:
        print(field)
        if field != 'redirect_url' and field != 'csrfmiddlewaretoken':
            item_id = form[field]
            # food_item = get_object_or_404(Food_Item, pk=item_id)
            # combo as dict below
            if item_id in combo_to_append:
                combo_to_append[item_id] += 1
            else:
                combo_to_append[item_id] = 1

    combo_hash = hash(str(combo_to_append))
    combo_key = 'c' + str(combo_hash)
    if combo_key in list(order.keys()):
        order[combo_key][1] += 1
    else:
        order[combo_key] = [combo_id, 1, combo_to_append] 

    request.session['food_order'] = order
    print(f'Order is {order}')

    return redirect(redirect_url)


def remove_from_order(request, item_id):
    """ Removes item from order effectively taking that item's quantity
    to zero. """

    order = request.session.get('food_order', {})
    order.pop(item_id)
    request.session['food_order'] = order
    print(request.session.get('food_order'))

    return HttpResponse(status=200)


def edit_order(request, item_type, item_id):
    """ Edits quantity of the specified product to the food order """

    order = request.session.get('food_order', {})
    changed_quantity_value = int(request.POST.get('qtyVal'))
    if item_type == 'item':
        order[item_id] = changed_quantity_value
    else:
        print(f'order object is {order}')
        order[request.POST.get('comboHashKey')][1] = changed_quantity_value

    request.session['food_order'] = order
    print(request.session.get('food_order'))

    return HttpResponse(status=204)
