from django.http import HttpResponse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from decimal import Decimal

from .models import Order
from members_area.models import MemberProfile

from .views import get_discount, save_to_orderlineitem

import json
import time


class StripeWH_Handler:
    """ Handles webhooks from stripe """

    def __init__(self, request):
        self.request = request

    def _send_confirmation_email_to_nonmember(self, order):
        cust_email = order.email
        subject = render_to_string(
            'checkout/confirmation_email/email_subject.txt',
            {'order': order}
        )
        body = render_to_string(
            'checkout/confirmation_email/email_body_nonmember.txt',
            {'order': order, 'from_email': settings.DEFAULT_FROM_EMAIL}
        )

        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [cust_email],
                  fail_silently=False)

    def _send_confirmation_email_to_member(self, order, member):
        cust_email = order.email
        subject = render_to_string(
            'checkout/confirmation_email/email_subject.txt',
            {'order': order}
        )
        if member.reward_status == 0:
            reward_msg = "Congratulations, you earned a free burger on this \
order."
        elif member.reward_status == 5:
            reward_msg = "Almost there, you will receive a free burger on your \
next order."
        else:
            reward_msg = f"Just {5-member.reward_status} more order(s) \
needed to grab your free burger."

        body = render_to_string(
            'checkout/confirmation_email/email_body_member.txt',
            {'order': order, 'reward_msg': reward_msg, 'from_email':
             settings.DEFAULT_FROM_EMAIL}
        )

        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [cust_email],
                  fail_silently=False)

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
        username = intent.metadata.username
        is_collection = intent.metadata.is_collection
        discount_result = None

        if username != 'AnonymousUser':
            memberprofile = MemberProfile.objects.get(
                            member__username=username)
            if memberprofile.reward_status == 5:
                discount = get_discount(json.loads(food_order))
                if not isinstance(discount, str):
                    discount_result = discount

        else:
            memberprofile = None

        billing_details = intent.charges.data[0].billing_details
        shipping_details = intent.shipping
        grand_total = round(intent.charges.data[0].amount / 100, 2)

        # Empty fields become None, to be consistent with billing details
        if not is_collection:
            for field, value in shipping_details.address.items():
                if value == "":
                    shipping_details.address[field] = None

        order_exists = False
        iterations = 1
        while iterations <= 5:
            try:
                if is_collection:
                    order = Order.objects.get(
                        name__iexact=shipping_details.name,
                        mobile_number__iexact=billing_details.phone,
                        email__iexact=billing_details.email,
                        grand_total=grand_total,
                        pid=pid
                    )
                else:
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
                break
            except Order.DoesNotExist:
                iterations += 1
                time.sleep(1)
        if order_exists:
            if memberprofile is None:
                self._send_confirmation_email_to_nonmember(order)
            else:
                self._send_confirmation_email_to_member(order, memberprofile)
            return HttpResponse(
                    content=f"Webhook received: {event['type']} | SUCCESS: Database already contains this order.",
                    status=200
                    )
        else:
            order = None
            try:
                if is_collection:
                    order = Order.objects.create(
                        name=shipping_details.name,
                        mobile_number=billing_details.phone,
                        email=billing_details.email,
                        pid=pid
                    )
                else:
                    order = Order.objects.create(
                        name=shipping_details.name,
                        mobile_number=billing_details.phone,
                        email=billing_details.email,
                        address_line1=shipping_details.address.line1,
                        address_line2=shipping_details.address.line2,
                        postcode=shipping_details.address.postal_code,
                        pid=pid
                    )

                for order_itemid, value in json.loads(food_order).items():
                    save_to_orderlineitem(order_itemid, value, order)

            except Exception as e:
                if order:
                    order.delete()

                return HttpResponse(
                        content=f"Webhook received: {event['type']} | \
                            ERROR: {e}",
                        status=500
                    )

        if memberprofile is None:
            self._send_confirmation_email_to_nonmember(order)
        else:
            if discount_result:
                # if discount exists, apply it and reset the reward status for
                # that member.
                order.discount = discount_result
                order.grand_total = round(Decimal(order.grand_total) - order.discount, 2)
                memberprofile.reward_status -= 5
            else:
                # no discount means progress reward status
                memberprofile.reward_status += 1
            MemberProfile.save(memberprofile)
            order.member_profile = memberprofile
            self._send_confirmation_email_to_member(order, memberprofile)

        order.save()

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