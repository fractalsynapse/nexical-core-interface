from django.http import JsonResponse
from django.views.generic import View
from rest_framework import status

from app.utils.mailgun import MailgunError, get_event

from . import models


class MailgunWebhookView(View):
    def post(self, request, *args, **kwargs):
        try:
            event = get_event(request.body)
            event_type = event.get("event", None)
            email = event.get("recipient", None)

        except MailgunError as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if not event_type:
            return JsonResponse({"error": "No event type found"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if not email:
            return JsonResponse({"error": "No email recipient found"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        event = models.MessageEvent.objects.create(type=event_type, email=email, payload=event)
        event.create_event()
        return JsonResponse({"status": "Success"})
