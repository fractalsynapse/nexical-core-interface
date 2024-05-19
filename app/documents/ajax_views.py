from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View
from rest_framework import status

from app.teams.ajax_views import TeamOwnershipAJAXMixin
from app.teams.models import get_active_team

from .models import TeamDocumentCollection


class ProgressView(TeamOwnershipAJAXMixin, View):
    def get(self, request, *args, **kwargs):
        team = get_active_team(request.user)
        collection = get_object_or_404(TeamDocumentCollection, pk=self.kwargs["pk"], team=team)
        return JsonResponse({"processed_time": collection.processed_time}, status=status.HTTP_200_OK)
