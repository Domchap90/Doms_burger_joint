from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.core import serializers

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

    if item_id in list(order.keys()):
        if order[item_id] < 10:
            order[item_id] += 1
            messages.success(request, f'Added {food_item.name} to your order.')
        else:
            messages.error(request, f'You have reached your order limit for \
                           {food_item.name}.')
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
    combo_counter = 0
    combo_id = int(combo_id)
    combo_item = get_object_or_404(Food_Combo, pk=combo_id)

    for key, value in order.items():
        if key[0] == 'c':
            combo_key = key
            if order[combo_key][0] == combo_id:
                combo_counter += order[combo_key][1]

    combo_to_append = {}

    # combo limits set in quantity_buttons.js
    if (combo_id == 2 and combo_counter < 3) or (
            combo_id != 2 and combo_counter < 5):
        for field in form:
            if field != 'redirect_url' and field != 'csrfmiddlewaretoken':
                item_id = form[field]
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

        messages.success(request, f'Added {combo_item.name} to your order.')
        combo_counter += 1

    else:
        messages.error(request, f'You have reached your order limit for {combo_item.name}.')
    request.session['food_order'] = order

    return redirect(redirect_url)


def remove_from_order(request, item_type, item_id):
    """ Removes item from order effectively taking that item's quantity
    to zero. """
    order = request.session.get('food_order', {})
    if item_type == 'item':
        order.pop(item_id)
    else:
        order.pop(request.POST.get('comboHashKey'))
    request.session['food_order'] = order

    return HttpResponse(status=200)


def edit_order(request, item_type, item_id):
    """ Edits quantity of the specified product to the food order """

    order = request.session.get('food_order', {})
    # combo_value = order[request.POST.get('comboHashKey')]
    changed_quantity_value = int(request.POST.get('newQtyVal'))
    original_quantity_value = int(request.POST.get('oldQtyVal'))
    if item_type == 'item':
        order[item_id] = changed_quantity_value
        item = get_object_or_404(Food_Item, pk=item_id)
    else:
        order[request.POST.get('comboHashKey')][1] = changed_quantity_value
        item = get_object_or_404(Food_Combo, pk=order[request.POST.get('comboHashKey')][0])

    subtotal = item.price * changed_quantity_value
    subtotal_change = (changed_quantity_value - original_quantity_value) * item.price

    request.session['food_order'] = order
    data = {"subtotal": subtotal, "subtotal_change": subtotal_change}

    return JsonResponse(data, status=200)
