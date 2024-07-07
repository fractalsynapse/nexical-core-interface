from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views import View
from rest_framework import status
from rest_framework.authtoken.models import Token

from app.utils.auth import TeamAccessMixin


class SettingsView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return JsonResponse(request.user.settings, status=status.HTTP_200_OK)


class SaveSettingsView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            for key, value in request.POST.items():
                request.user.settings[key] = value
            request.user.save()

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return JsonResponse({}, status=status.HTTP_200_OK)


class GenerateTokenView(TeamAccessMixin, View):
    def get(self, request, *args, **kwargs):
        Token.objects.filter(user=request.user).delete()
        token = Token.objects.create(user=request.user)
        return JsonResponse({"token": token.key}, status=status.HTTP_200_OK)


class RevokeTokenView(TeamAccessMixin, View):
    def get(self, request, *args, **kwargs):
        Token.objects.filter(user=request.user).delete()
        return JsonResponse({"token": ""}, status=status.HTTP_200_OK)
