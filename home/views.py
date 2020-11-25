from django.shortcuts import render, redirect, reverse
from django.conf import settings

import re
import requests


def index(request):
    """ Main index page view """
    return render(request, 'home/index.html')


def check_postcode_home(request):
    """
    Determines whether able to deliver to address
    or if they must collect.
    """

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


def is_postcode_valid(postcode):
    # Check if post code valid
    postcode_valid = False
    if len(postcode) > 4 and len(postcode) < 9:
        if re.match("^[a-zA-Z][a-zA-Z0-9\\s]+[a-zA-Z]$", postcode) is not None:
            postcode_valid = True

    if postcode_valid:
        formatted_postcode = []
        # format postcode so all entries are standardized with no spaces or
        # lower case characters
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

            # coordinates for user's address
            user_lat = str(geocode_response['results'][0]['geometry'][
                'location']['lat'])
            user_lng = str(geocode_response['results'][0]['geometry'][
                'location']['lng'])

            store_lat = '51.512647'
            store_lng = '-0.13375'

            # API check distance (using imperial units to get miles)
            distance_url = "https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&origins=\
                "+user_lat+","+user_lng+"&destinations="+store_lat+",\
"+store_lng+"&key="+settings.GOOGLEMAPS_API_KEY

            distance_response = requests.get(distance_url).json()

            # extract value from JSON response object & split the string to
            # get the value only.
            distance_miles = float(
                distance_response['rows'][0]['elements'][0]['distance'][
                    'text'].split(' ')[0])

            if distance_miles > 1.5:
                postcode_valid = False

        except Exception:
            postcode_valid = False

    return postcode_valid
