from django.http import JsonResponse
from django.views import View
from rest_framework import status

from app.teams.models import get_active_team
from app.utils.auth import TeamAccessMixin

from .models import TeamProject, set_active_project


class SetActiveView(TeamAccessMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            team = get_active_team(request.user)
            project = TeamProject.objects.get(pk=self.kwargs["pk"], team=team)

        except TeamProject.DoesNotExist:
            return JsonResponse({"error": ""}, status=status.HTTP_400_BAD_REQUEST)

        set_active_project(request.user, project.id)
        return JsonResponse({}, status=status.HTTP_204_NO_CONTENT)
