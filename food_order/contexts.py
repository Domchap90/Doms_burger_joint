from decimal import Decimal
from django.conf import settings
from django.shortcuts import get_object_or_404
from menu.models import Food_Item, Food_Combo


def order_contents(request):

    order_items = []
    # identical_items will be a nested dictionary with outer key as combo_index taking 
    # a dictionary of item ids (inner keys) along with their quantities as values.
    identical_items = {}
    combo_items = {}
    order_items_count = 0
    total_items = 0
    total_combos = 0
    combo_count = 0
    order = request.session.get('food_order', {})

    for key, quantity in order.items():
        if key:
            if 'combo' not in key:
                food_item = get_object_or_404(Food_Item, pk=key)
                total_items += quantity * food_item.price
                order_items_count += quantity
                order_items.append({
                    'item_id': key,
                    'food_item': food_item,
                    'quantity': quantity
                })
            else:
                print(f'key is {key}')
                combo_id = int(key.split('_')[1])
                combo_item = get_object_or_404(Food_Combo, pk=combo_id)
                total_combos += combo_item.price * len(order[key])
                combo_count += len(order[key]) 
                combo_index = 0
                for combo in order[key]:
                    # combo_index used as reference to collect identical items in same combo item
                    combo_index += 1
                    for item in combo:
                        food_item = get_object_or_404(Food_Item, pk=item)
                        if combo_id == 2:
                            if combo_index in identical_items:
                                if food_item in identical_items[combo_index]:
                                    identical_items[combo_index][food_item] += 1
                                else:
                                    identical_items[combo_index][food_item] = 1
                            else:
                                identical_items[combo_index] = {}
                                identical_items[combo_index][food_item] = 1
                        elif combo_item in combo_items:
                            if combo_index in combo_items[combo_item]:
                                combo_items[combo_item][combo_index][food_item] = 1
                            else:
                                combo_items[combo_item][combo_index] = {}
                                combo_items[combo_item][combo_index][food_item] = 1
                        else:
                            combo_items[combo_item] = {}
                            combo_items[combo_item][combo_index] = {}
                            combo_items[combo_item][combo_index][food_item] = 1

                combo_items[get_object_or_404(Food_Combo, pk=2)] = identical_items

                print('identical_items dict:')
                for combo, quantity_map in identical_items.items():
                    print(f'{combo} -> {quantity_map}')
                print('identical_items dict:')
                for comboID in combo_items:
                    print(f'comboID is {comboID}')
                    for combo, quantity_map in combo_items[comboID].items():
                        print(f'{combo} -> {quantity_map}')

    total_items_and_combos = total_items + total_combos

    if total_items_and_combos < settings.MIN_DELIVERY_THRESHOLD:
        remaining_delivery_amount = settings.MIN_DELIVERY_THRESHOLD - float(total_items_and_combos)
    else:
        remaining_delivery_amount = 0

    grand_total = total_items_and_combos + Decimal(settings.DELIVERY_FEE)

    context = {
        'order_items': order_items,
        'combo_items': combo_items,
        'order_count': order_items_count,
        'min_delivery_threshold': settings.MIN_DELIVERY_THRESHOLD,
        'delivery_fee': settings.DELIVERY_FEE,
        'remaining_delivery_amount': remaining_delivery_amount,
        'total': total_items_and_combos,
        'grand_total': grand_total
    }

    return context
