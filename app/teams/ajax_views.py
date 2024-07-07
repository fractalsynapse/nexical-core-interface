from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views import View
from rest_framework import status

from app.utils.auth import TeamAccessMixin

from .models import Team, TeamInvite, get_active_team, set_active_team


class TeamOwnershipAJAXMixin(TeamAccessMixin):
    def get_queryset(self):
        return self.model.objects.filter(team=self.team)

    def get_team_url(self, name, **kwargs):
        return reverse(name, kwargs={**kwargs, "team": self.team.id})

    def dispatch(self, request, *args, **kwargs):
        self._initialize_team(request)
        if not self.team:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["team"] = self.team
        return context

    def _initialize_team(self, request):
        self.team = get_active_team(request.user)


class SetActiveView(TeamAccessMixin, View):
    def get(self, request, *args, **kwargs):
        team = get_object_or_404(Team, pk=self.kwargs["pk"])
        set_active_team(request.user, team.id)
        return JsonResponse({}, status=status.HTTP_200_OK)


class InviteSendView(TeamAccessMixin, View):
    def get(self, request, *args, **kwargs):
        team = get_object_or_404(Team, pk=self.kwargs["team"])
        email = request.GET.get("email", None)
        if not email:
            return JsonResponse(
                {"error": "Email parameter 'email' required with valid email address"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        TeamInvite.objects.filter(team=team, email=email).delete()
        invite = TeamInvite.objects.create(team=team, email=email)
        invite.send(request)

        return JsonResponse({}, status=status.HTTP_200_OK)
