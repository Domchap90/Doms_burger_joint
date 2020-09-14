from django.http import HttpResponse


class webhook_handler:
    """ Handles webhooks from stripe """

    def __init__(self, request):
        self.request = request

    def handle_event(self, event):
        """ Handles generic Webhooks """
        return HttpResponse(
            content=f"Webhook received: {event['type']}.",
            status=200
            )
