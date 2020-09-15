from django.http import HttpResponse


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
        return HttpResponse(
            content=f"Webhook received: {event['type']}.",
            status=200
            )

    def handles_failed_payment_intent(self, event):
        """ handles payment_intent.payment_failed """
        return HttpResponse(
            content=f"Webhook received (Payment Failed): {event['type']}.",
            status=200
            )