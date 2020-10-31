from decimal import Decimal
from django.conf import settings
from django.shortcuts import get_object_or_404
from menu.models import Food_Item, Food_Combo


def order_contents(request):

    order_items = []
    order_items_count = 0
    combo_count = 0
    total_items = 0
    total_combos = 0
    combo_hash_map = {}
    order = request.session.get('food_order', {})

    for key, quantity in order.items():
        if key:
            if key[0] != 'c':
                food_item = get_object_or_404(Food_Item, pk=key)
                total_items += quantity * food_item.price
                order_items_count += quantity
                order_items.append({
                    'item_id': key,
                    'food_item': food_item,
                    'quantity': quantity
                })
            else:
                combo_hash_map[key] = [None, None, None]
                combo_id = order[key][0]
                combo_hash_map[key][0] = get_object_or_404(Food_Combo,
                                                           pk=combo_id)

                # dictionary will replace current order[key][2] dict.
                item_obj_dict = {}
                # replace item_ids with the actual item objects so all the
                # information can be rendered on the order page.
                for item_id, qty in order[key][2].items():
                    item_obj_dict[get_object_or_404(Food_Item, pk=item_id)] = qty

                combo_hash_map[key][2] = item_obj_dict

                combo_quantity = order[key][1]
                combo_hash_map[key][1] = combo_quantity
                total_combos += combo_hash_map[key][0].price * combo_quantity
                combo_count += combo_quantity

    total_items_and_combos = total_items + total_combos

    if total_items_and_combos < settings.MIN_DELIVERY_THRESHOLD:
        remaining_delivery_amount = settings.MIN_DELIVERY_THRESHOLD - float(
                                    total_items_and_combos)
    else:
        remaining_delivery_amount = 0

    grand_total = total_items_and_combos + Decimal(settings.DELIVERY_FEE)

    context = {
        'order_items': order_items,
        'combo_items': combo_hash_map,
        'order_items_count': order_items_count,
        'combo_count': combo_count,
        'order_count': order_items_count + combo_count,
        'min_delivery_threshold': settings.MIN_DELIVERY_THRESHOLD,
        'delivery_fee': settings.DELIVERY_FEE,
        'remaining_delivery_amount': remaining_delivery_amount,
        'total': total_items_and_combos,
        'grand_total': grand_total
    }

    return context

