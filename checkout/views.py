from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.shortcuts import HttpResponse
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
# import googlemaps
import requests


@require_POST
def cached_payment_intent(request):
    try:
        pid = request.POST.get('client_secret').split('_secret')[0]
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe.PaymentIntent.modify(pid, metadata={
            'food_order': json.dumps(request.session.get('food_order', {})),
            'username': request.user,
            'order': json.dumps(request.session.get('food_order'))
        })
        return HttpResponse(status=200)
    except Exception as e:
        messages.error(request, 'Unfortunately your payment could not be processed at this time. \
            Please try again in a few minutes.')
        return HttpResponse(content=e, status=400)


def checkout(request):
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY
    food_order = request.session.get('food_order', {})

    delivery_eligibility = request.session.get('delivery_eligibility', None)
    reward_notification = None
    discount_result = None

    if request.method == 'POST':
        form_data = {
            'name': request.POST['name'],
            'mobile_number': request.POST['mobile_number'],
            'email': request.POST['email'],
            'for_collection': request.POST['for_collection'],
            'address_line1': request.POST['address_line1'],
            'address_line2': request.POST['address_line2'],
            'postcode': request.POST['postcode'],
            'delivery_instructions': request.POST['delivery_instructions'],
        }
        postcode_is_valid = check_postcode_checkout(request.POST['postcode'])
        if not postcode_is_valid:
            # disable button js
            msg = "Sorry it looks like you are not eligible for delivery. However \
            please feel free to make an order for collection."
            delivery_eligibility = msg
            request.session['delivery_eligibility'] = delivery_eligibility
            # request.session['delivery_eligibility']['postcode'] = postcode
            
            return redirect(reverse('checkout'))

        order_form = set_order_form(form_data, request.POST['for_collection'])
        if order_form.is_valid():
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
        is_collect = request.GET.get('is_collect', None)
        total = order_contents(request)['grand_total']
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
        'stripe_public_key': stripe_public_key,
        'client_secret': intent.client_secret,
        'reward_notification': reward_notification,
        'discount': discount_result,
        'total': total,
    }

    return render(request, 'checkout/checkout.html', context)


def save_to_orderlineitem(order_itemid, value, order):
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
    order_form = OrderFormDelivery(form_data)
    if is_collection:
        order_form = OrderFormCollection(form_data)

    return order_form

def check_postcode_home(request):
    """
    Determines whether able to deliver to address
    or if they must collect.
    """

    postcode_valid = False
    if request.method == 'POST':
        postcode = request.POST.get('postcode')

        postcode_valid = is_postcode_valid(postcode)

        msg = "Sorry it looks like you are not eligible for delivery. However \
        please feel free to make an order for collection."
        if postcode_valid:
            msg = "Good news! You are eligible for delivery."

        request.session['delivery_eligibility'] = {}
        request.session['delivery_eligibility']['message'] = msg
        request.session['delivery_eligibility']['postcode'] = postcode

    return redirect(reverse('home'))


def check_postcode_checkout(postcode):
    """ Used for form validation to check delivery eligibility """
    postcode_valid = is_postcode_valid(postcode)

    if postcode_valid:
        return True

    return False


def is_postcode_valid(postcode):
    # Check if post code valid
    postcode_valid = False
    if len(postcode) > 4 and len(postcode) < 9:
        if re.match("^[a-zA-Z][a-zA-Z0-9\\s]+[a-zA-Z]$", postcode) is not None:
            postcode_valid = True

    if postcode_valid:
        formatted_postcode = []
        # format postcode so all entries are standardized with no spaces or lower
        # case characters
        for char in postcode:
            if char != " ":
                formatted_postcode.append(char.upper())
        postcode_string = "".join(formatted_postcode)
        accepted_prefixes = ['WC1', 'WC2', 'W1', 'SW1']
        # Check it's in listed postcode region
        for prefix in accepted_prefixes:
            if re.match("^"+prefix, postcode_string) is None:
                postcode_valid = False
            else:
                postcode_valid = True
                break

    if postcode_valid:
        # API convert postcode to geocode
        # gmap_key = googlemaps.Client(key=settings.GOOGLEMAPS_API_KEY)
        geocode_url = "https://maps.googleapis.com/maps/api/geocode/json?address=components=postal_code:\
        "+postcode_string+"|country:GB&key="+settings.GOOGLEMAPS_API_KEY
        try:
            geocode_response = requests.get(geocode_url).json()
        except requests.exceptions.Timeout:
            "We were unable to process the postcode at this time sorry, please try again later."

        # coordinates for user's address
        user_lat = str(geocode_response['results'][0]['geometry']['location']['lat'])
        user_lng = str(geocode_response['results'][0]['geometry']['location']['lng'])

        store_lat = '51.512647'
        store_lng = '-0.13375'

        # API check distance (using imperial units to get miles)
        distance_url = "https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&origins=\
            "+user_lat+","+user_lng+"&destinations="+store_lat+","+store_lng+"&key="+settings.GOOGLEMAPS_API_KEY
        try:
            distance_response = requests.get(distance_url).json()
        except requests.exceptions.Timeout:
            "We were unable to process the postcode at this time sorry, please try again later."

        # extract value from JSON response object & split the string to get the value only.
        distance_miles = float(distance_response['rows'][0]['elements'][0]['distance']['text'].split(' ')[0])

        if distance_miles > 1.5:
            postcode_valid = False

        return postcode_valid


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
