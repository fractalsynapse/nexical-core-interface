from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views import View
from rest_framework import status

from .models import Feedback


class SendView(LoginRequiredMixin, View):
    def validate_params(self, path, rating, message):
        if not path or not rating or not message:
            return JsonResponse(
                {"error": "Parameters 'path', 'rating, and 'message' are required for feedback submission"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                raise Exception()
        except Exception:
            return JsonResponse(
                {"error": "Parameter 'path' must be an integer between 1 and 5"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return None

    def post(self, request, *args, **kwargs):
        path = request.POST.get("path", None)
        rating = request.POST.get("rating", None)
        message = request.POST.get("message", None)

        error = self.validate_params(path, rating, message)
        if error:
            return error

        try:
            Feedback.objects.create(user=request.user, path=path, rating=int(rating), message=message)
        except Exception as e:
            return JsonResponse(
                {"error": f"Feedback submission failed with error: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        return JsonResponse({"path": path, "rating": int(rating), "message": message}, status=status.HTTP_200_OK)
