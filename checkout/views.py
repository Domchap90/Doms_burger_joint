from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.conf import settings

from .forms import OrderForm
from food_order.contexts import order_contents

from .models import Order, OrderLineItem
from menu.models import Food_Item

import stripe

# Create your views here.


def checkout(request):
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY
    

    

    if request.method == 'POST':
        food_order = request.session.get('food_order', {})

        form_data = {
            'name': request.POST['name'],
            'mobile_number': request.POST['mobile_number'],
            'email': request.POST['email'],
            'address_line1': request.POST['address_line1'],
            'address_line2': request.POST['address_line2'],
            'postcode': request.POST['postcode'],
            'delivery_instructions': request.POST['delivery_instructions'],
        }

        order_form = OrderForm(form_data)
        if order_form.is_valid():
            order = order_form.save()
            for order_itemid, quantity in food_order.items():
                try:
                    food_item = Food_Item.objects.get(id=order_itemid)
                    order_line_item = OrderLineItem(
                        order=order,
                        food_item=food_item,
                        quantity=quantity,
                    )
                    order_line_item.save()

                except Food_Item.DoesNotExist:
                    messages.error(request, (
                        "Unfortunately our database was unable to detect an item selected in your order."
                    ))
                    order.delete()
                    return redirect(reverse('food_order'))

            request.session['save_info'] = 'save-info' in request.POST

            return redirect(reverse('checkout_success', args=[order.order_number] ))    
        else:
            messages.error(request, "Form could not be submitted.")

    else:
        total = order_contents(request)['grand_total']
        stripe_total = round(total*100)
        stripe.api_key = stripe_secret_key

        intent = stripe.PaymentIntent.create(
            amount=stripe_total,
            currency=settings.STRIPE_CURRENCY,
            # Verify your integration in this guide by including this parameter
            metadata={'integration_check': 'accept_a_payment'},
        )

        order_form = OrderForm()

    if not stripe_public_key:
        messages.warning(request, 'Stripe public key is missing. Please ensure \
             that it is set in the environment variables.')

    context = {
        'form': order_form,
        'stripe_public_key': stripe_public_key,
        'client_secret': intent.client_secret,
        'total': total,
    }
    
    return render(request, 'checkout/checkout.html', context)


def checkout_success(request, order_number):
    """ Directs to this page if checkout was successful """
    # save_info = request.session.get('save_info')
    order = get_object_or_404(Order, order_number=order_number)
    messages.success(request, f'Thank you for completing your order. \
        You will shortly receive an email to confirm it has been placed. \
        Order Number: {order.order_number} \
        Confirmation email sent to {order.email}.')
    
    if 'food_order' in request.session:
        del request.session['food_order']

    context = {
        'order': order,
    }

    return render(request, 'checkout/checkout_success.html', context)