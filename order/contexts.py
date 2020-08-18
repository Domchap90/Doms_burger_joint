from decimal import Decimal
from django.conf import settings

def order_contents(request):

    order_items = []
    combo_items = 0
    total = 0

    if total < settings.MIN_DELIVERY_THRESHOLD:
        remaining_delivery_amount = settings.MIN_DELIVERY_THRESHOLD - total
    else:
        remaining_delivery_amount = 0

    grand_total = total + settings.DELIVERY_FEE

    context = {
        'order_items': order_items,
        'combo_items': combo_items,
        'min_delivery_threshold': Decimal(settings.MIN_DELIVERY_THRESHOLD),
        'remaining_delivery_amount': remaining_delivery_amount,
        'total': total,
        'grand_total': grand_total
    }

    return context
