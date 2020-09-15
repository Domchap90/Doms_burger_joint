from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from checkout.webhook_handler import StripeWH_Handler

import stripe


@require_POST
@csrf_exempt
def webhook(request):
    endpoint_secret = settings.STRIPE_WH_SECRET
    stripe.api_key = settings.STRIPE_SECRET_KEY
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)
    except Exception as e:
        return HttpResponse(content=e, status=400)

    handler = StripeWH_Handler(request)

    event_map = {
        'payment_intent.succeeded': handler.handle_successful_payment_intent,
        'payment_intent.payment_failed': handler.handles_failed_payment_intent,
    }

    event_type = event['type']

    # retrieves event from dictionary above
    event_handler = event_map.get(event_type, handler.handle_event)

    response = event_handler(event)

    return response
