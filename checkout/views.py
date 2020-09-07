from django.shortcuts import render
from django.contrib import messages
from django.conf import settings

from .forms import OrderForm
from food_order.contexts import order_contents

import stripe

# Create your views here.


def checkout(request):
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY

    form = OrderForm()

    total = order_contents(request)['grand_total']
    stripe_total = round(total*100)
    stripe.api_key = stripe_secret_key

    intent = stripe.PaymentIntent.create(
        amount=stripe_total,
        currency=settings.STRIPE_CURRENCY,
        # Verify your integration in this guide by including this parameter
        metadata={'integration_check': 'accept_a_payment'},
    )

    if not stripe_public_key:
        messages.warning(request, 'Stripe public key is missing. Please ensure \
             that it is set in the environment variables.')

    context = {
        'form': form,
        'stripe_public_key': stripe_public_key,
        'client_secret': intent.client_secret,
        'total': total,
    }

    return render(request, 'checkout/checkout.html', context)
