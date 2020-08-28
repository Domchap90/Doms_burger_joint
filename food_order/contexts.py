from decimal import Decimal
from django.conf import settings
from django.shortcuts import get_object_or_404
from menu.models import Food_Item


def order_contents(request):

    order_items = []
    combo_items = 0
    order_items_count = 0
    total = 0
    order = request.session.get('food_order', {})

    for order_itemid, quantity in order.items():
        food_item = get_object_or_404(Food_Item, pk=order_itemid)
        total += quantity * food_item.price
        order_items_count += quantity
        order_items.append({
            'item_id': order_itemid,
            'food_item': food_item,
            'quantity': quantity
        })

    if total < settings.MIN_DELIVERY_THRESHOLD:
        remaining_delivery_amount = settings.MIN_DELIVERY_THRESHOLD - float(total)
    else:
        remaining_delivery_amount = 0

    grand_total = total + Decimal(settings.DELIVERY_FEE)

    context = {
        'order_items': order_items,
        'combo_items': combo_items,
        'order_count': order_items_count,
        'min_delivery_threshold': settings.MIN_DELIVERY_THRESHOLD,
        'delivery_fee': settings.DELIVERY_FEE,
        'remaining_delivery_amount': remaining_delivery_amount,
        'total': total,
        'grand_total': grand_total
    }

    return context
