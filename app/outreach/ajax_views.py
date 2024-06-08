from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View
from rest_framework import status

from app.utils.auth import OutreachAccessMixin

from . import models


class BaseAjaxMessageView(OutreachAccessMixin, View):
    pass


class SendView(BaseAjaxMessageView):
    def post(self, request, *args, **kwargs):
        subject = request.POST.get("subject", None)
        body = request.POST.get("body", None)

        if not subject or not body:
            return JsonResponse(
                {"error": "Parameters 'subject' and 'body' are required for sending outreach messages"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        message = get_object_or_404(models.Message, pk=self.kwargs["pk"])

        if message.sequence.campaign.owner != request.user:
            error = "Can not send in a campaign you don't own"
        elif not message.sequence.contact.checkout or message.sequence.contact.checkout.user != request.user:
            error = "Can not send to a checked out contact"
        else:
            message.sender = request.user
            message.subject = subject
            message.body = body
            message.processed = True
            message.save()
            return JsonResponse({}, status=status.HTTP_204_NO_CONTENT)

        return JsonResponse({"error": error}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SkipView(BaseAjaxMessageView):
    def post(self, request, *args, **kwargs):
        message = get_object_or_404(models.Message, pk=self.kwargs["pk"])

        if message.sequence.campaign.owner != request.user:
            error = "Can not skip a message in a campaign you don't own"
        elif not message.sequence.contact.checkout or message.sequence.contact.checkout.user != request.user:
            error = "Can not skip a message in a checked out contact"
        else:
            message.skipped = True
            message.save()
            return JsonResponse({}, status=status.HTTP_204_NO_CONTENT)

        return JsonResponse({"error": error}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BlockView(BaseAjaxMessageView):
    def post(self, request, *args, **kwargs):
        message = get_object_or_404(models.Message, pk=self.kwargs["pk"])

        if message.sequence.campaign.owner != request.user:
            error = "Can not block a contact in a campaign you don't own"
        elif not message.sequence.contact.checkout or message.sequence.contact.checkout.user != request.user:
            error = "Can not block a contact in a checked out contact"
        else:
            message.sequence.contact.blocked = True
            message.sequence.contact.save()

            message.skipped = True
            message.save()
            return JsonResponse({}, status=status.HTTP_204_NO_CONTENT)

        return JsonResponse({"error": error}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
