from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.shortcuts import HttpResponse
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.conf import settings

from .forms import OrderFormDelivery, OrderFormCollection
from food_order.contexts import order_contents

from .models import Order, OrderLineItem, ComboLineItem
from menu.models import Food_Item, Food_Combo
from members_area.models import MemberProfile

import json
import stripe
import re


@require_POST
def cached_payment_intent(request):
    """ Complete remainder of payment intent based upon successful form
    validation """
    try:
        pid = request.POST.get('client_secret').split('_secret')[0]
        is_collection = request.POST.get('is_collection')
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe.PaymentIntent.modify(pid, metadata={
            'food_order': json.dumps(request.session.get('food_order', {})),
            'username': request.user,
            'order': json.dumps(request.session.get('food_order')),
            'is_collection': is_collection,
        })

        return HttpResponse(status=200)

    except Exception as e:
        print(f'Exception is {e}')
        messages.error(request, 'Unfortunately your payment could not be processed at this time. \
            Please try again in a few minutes.')
        return HttpResponse(content=e, status=400)


def checkout(request):
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY
    food_order = request.session.get('food_order', {})
    total = order_contents(request)['grand_total']
    intent = None

    is_collect = request.GET.get('is_collect', None)
    reward_notification = None
    discount_result = None

    if request.method == 'POST':
        for_collection = True
        if request.POST['for_collection'] == "False":
            for_collection = False

        form_data = {
            'name': request.POST['name'],
            'mobile_number': request.POST['mobile_number'],
            'email': request.POST['email'],
            'for_collection': request.POST['for_collection'],
        }
        if not for_collection:
            # Adds extra data for delivery ONLY
            form_data['address_line1'] = request.POST['address_line1']
            form_data['address_line2'] = request.POST['address_line2']
            form_data['postcode'] = request.POST['postcode']
            form_data['delivery_instructions'] = request.POST['delivery_instructions']

        order_form = set_order_form(form_data, for_collection)

        if order_form.is_valid():
            # Commit false allows the information obtained from the form to be
            # saved whilst not fully creating the order object just yet
            order = order_form.save(commit=False)
            pid = request.POST.get('client_secret').split('_secret')[0]
            order.pid = pid
            if request.user.is_authenticated:
                member_profile = MemberProfile.objects.get(member=request.user)
                if request.POST.get('discount'):
                    # if hidden discount input exists rendered by non-POST
                    # checkout view it means there is a discount to be
                    # applied as well as resetting the reward status for
                    # that member.
                    order.discount = request.POST.get('discount')
                    member_profile.reward_status -= 5
                else:
                    # no discount means progress reward status
                    member_profile.reward_status += 1
                MemberProfile.save(member_profile)

            order.save()
            for order_itemid, value in food_order.items():
                try:
                    save_to_orderlineitem(order_itemid, value, order)

                except Food_Item.DoesNotExist:
                    messages.error(request, (
                        "Unfortunately our database was unable to detect an \
                         item selected in your order."
                    ))
                    order.delete()
                    return redirect(reverse('food_order'))

            return redirect(reverse('checkout_success',
                                    args=[order.order_number]))
        else:
            messages.error(request, "Form could not be submitted.")

    else:
        order_form = set_order_form({}, is_collect)

        if request.user.is_authenticated:
            try:
                member_profile = MemberProfile.objects.get(member=request.user)
                if is_collect:
                    order_form = OrderFormCollection(initial={
                        'name': member_profile.member.get_username(),
                        'email': member_profile.saved_email,
                        'mobile_number': member_profile.saved_mobile_number,
                        'for_collection': True,
                    })
                else:
                    order_form = OrderFormDelivery(initial={
                        'name': member_profile.member.get_username(),
                        'email': member_profile.saved_email,
                        'mobile_number': member_profile.saved_mobile_number,
                        'for_collection': False,
                        'postcode': member_profile.saved_postcode,
                        'address_line1': member_profile.saved_address_line1,
                        'address_line2': member_profile.saved_address_line2,
                        'delivery_instructions': member_profile.saved_delivery_instructions,
                    })
                if member_profile.reward_status == 5:
                    discount = get_discount(food_order)
                    if isinstance(discount, str):
                        reward_notification = discount
                    else:
                        discount_result = discount
                        total -= discount_result

            except MemberProfile.DoesNotExist:
                order_form = set_order_form({}, is_collect)
        else:
            order_form = set_order_form({}, is_collect)

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
        'form': order_form,
        'is_collect': is_collect,
        'stripe_public_key': stripe_public_key,
        'reward_notification': reward_notification,
        'discount': discount_result,
        'total': total,
    }
    if intent:
        context['client_secret'] = intent.client_secret

    return render(request, 'checkout/checkout.html', context)


def is_form_valid(request, is_collect):
    """ Get's called asynchronously from stripe_element.js to ensure form is
    valid before submitting """

    remaining_spend = order_contents(request)['remaining_delivery_amount']

    # convert javascript boolean to python boolean
    is_collect = False if 'false' else True

    # Retrieves each key, value pair as a list of tuples
    post_data = request.POST.lists()
    form_data = {}
    for pair in post_data:
        # Format the pair data so they can be added to form_data dict
        key = pair[0]
        # Eliminates special characters except for those required in emails &
        # spaces
        value = re.sub("[^a-zA-Z0-9\\s@.]", "", str(pair[1]))
        if key != 'csrfmiddlewaretoken':
            form_data[key] = value
 
    form = set_order_form(form_data, is_collect)

    if form.is_valid() and remaining_spend == 0:
        return JsonResponse({'valid': True}, status=200)

    # Create errors dictionary to populate the form with appropriate messages
    # in event that it isn't valid.
    err_dict = {}

    for field in form:
        for error in field.errors:
            err_dict[field.name] = error

    return JsonResponse(err_dict, status=200)


def save_to_orderlineitem(order_itemid, value, order):
    """ Used in both checkout (POST) and the webhook handler for successful
    payments which happen independently of each other."""

    # Items id doesn't begin with c, that only applies to combos.
    if order_itemid[0] != 'c':
        food_item = Food_Item.objects.get(id=order_itemid)
        order_line_item = OrderLineItem(
            order=order,
            food_item=food_item,
            quantity=value,
        )

        # Update the total purchased for each food in the
        # orderline for popular deals.
        food_item.total_purchased += value
        food_item.save()
    # For the instance of a combo
    else:
        combo_item = Food_Combo.objects.get(id=value[0])
        order_line_item = OrderLineItem(
            order=order,
            combo_item=combo_item,
            combo_id=order_itemid,
            combo_quantity=value[1],
        )
        order_line_item.save()
        # Iterate through combo contents to add each combo
        # line item to the combo
        for item, qty in value[2].items():
            food_item = Food_Item.objects.get(id=item)
            combo_line_item = ComboLineItem(
                                combo=order_line_item,
                                food_item=food_item,
                                quantity=qty)
            combo_line_item.save()
            # Update the total purchased for admin and popular
            # deals
            food_item.total_purchased += qty * value[1]
            food_item.save()
    order_line_item.save()


def get_discount(order):
    # Find cheapest burger for potential discount
    discount = 100.00

    for order_id, value in order.items():
        if order_id[0] != 'c':
            food_item = Food_Item.objects.get(id=order_id)
            if food_item.category.id == 1:
                if food_item.price < discount:
                    discount = food_item.price

    if discount < 100.00:
        return discount
    else:
        return "You haven't selected your free burger yet! Remember this can't \
                be part of a combo."


def set_order_form(form_data, is_collection):
    """ Determines whether form is for collection or delivery and returns
    correct form"""

    order_form = OrderFormDelivery(form_data)

    if is_collection:
        order_form = OrderFormCollection(form_data)

    return order_form


def collect_or_delivery(request):
    """ Renders page where user makes decision how they want to receive
    their food """

    return render(request, 'checkout/collect_or_delivery.html')


def checkout_success(request, order_number):
    """ Directs to this page if checkout was successful """

    order = get_object_or_404(Order, order_number=order_number)
    if request.user.is_authenticated:
        member = MemberProfile.objects.get(member=request.user)
        order.member_profile = member

    order.save()

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
