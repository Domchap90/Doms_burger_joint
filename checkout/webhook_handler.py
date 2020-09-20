from django.http import HttpResponse
from .models import Order, OrderLineItem
from menu.models import Food_Item

import json
import time


class StripeWH_Handler:
    """ Handles webhooks from stripe """

    def __init__(self, request):
        self.request = request

    def handle_event(self, event):
        """ Handles generic Webhooks """
        return HttpResponse(
            content=f"Unhandled Webhook received: {event['type']}.",
            status=200
            )

    def handle_successful_payment_intent(self, event):
        """ handles payment_intent.succeeded """
        intent = event.data.object
        pid = intent.id
        food_order = intent.metadata.food_order

        billing_details = intent.charges.data[0].billing_details
        shipping_details = intent.shipping
        grand_total = round(intent.charges.data[0].amount / 100, 2)

        # Empty fields become None, to be consistent with billing details
        for field, value in shipping_details.address.items():
            if value == "":
                shipping_details.address[field] = None
        
        order_exists = False
        iterations = 1
        while iterations <= 5:
            try:
                order = Order.objects.get(
                    name__iexact=shipping_details.name,
                    mobile_number__iexact=billing_details.phone,
                    email__iexact=billing_details.email,
                    address_line1__iexact=shipping_details.address.line1,
                    address_line2__iexact=shipping_details.address.line2,
                    postcode__iexact=shipping_details.address.postal_code,
                    grand_total=grand_total,
                    pid=pid
                )
                order_exists = True

            except Order.DoesNotExist:
                iterations += 1
                time.sleep(1)
        if order_exists:
            return HttpResponse(
                    content=f"Webhook received: {event['type']} | SUCCESS: Database already contains this order.",
                    status=200
                    )
        else:
            order = None
            try:
                order = Order.object.create(
                    name=shipping_details.name,
                    mobile_number=billing_details.phone,
                    email=billing_details.email,
                    address_line1=shipping_details.address.line1,
                    address_line2=shipping_details.address.line2,
                    postcode=shipping_details.address.postal_code,
                    pid=pid
                )
                for order_itemid, quantity in json.loads(food_order).items():
                    food_item = Food_Item.objects.get(id=order_itemid)
                    order_line_item = OrderLineItem(
                        order=order,
                        food_item=food_item,
                        quantity=quantity,
                    )
                    order_line_item.save()
            except Exception as e:
                if order:
                    order.delete()

                return HttpResponse(
                        content=f"Webhook received: {event['type']} | \
                            ERROR: {e}",
                        status=500
                    )
        return HttpResponse(
                    content=f"Webhook received: {event['type']} \
                        | SUCCESS: order created in webhook.",
                    status=200
                    )

    def handles_failed_payment_intent(self, event):
        """ handles payment_intent.payment_failed """
        return HttpResponse(
            content=f"Webhook received (Payment Failed): {event['type']}.",
            status=200
            )