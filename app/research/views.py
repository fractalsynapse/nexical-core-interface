# from django.template.loader import render_to_string
from django.views.generic import TemplateView

from app.projects.models import TeamProject, get_active_project
from app.teams.models import TeamTag, get_team_settings
from app.teams.views import TeamOwnershipMixin
from app.utils.auth import TeamAccessMixin

from . import models


class BasePanelView(TeamOwnershipMixin, TeamAccessMixin, TemplateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        settings = get_team_settings(self.request.user)
        active_project = get_active_project(self.request.user)

        context["active_project"] = active_project
        context["projects"] = TeamProject.objects.filter(team=self.team)
        context["tags"] = TeamTag.objects.filter(team=self.team)

        context["default_summary_depth"] = settings.get("default_summary_depth", 5)

        context["show_summary_help"] = models.ProjectSummary.objects.filter(user=self.request.user).count() < 10
        context["show_note_help"] = models.ProjectNote.objects.filter(user=self.request.user).count() < 10

        # context["help_title"] = "Research Help"
        # context["help_body"] = render_to_string("research_help.html")
        return context


class PanelView(BasePanelView):
    template_name = "research.html"


class ModalPanelView(BasePanelView):
    template_name = "research_modal.html"

    def render_to_response(self, context, **response_kwargs):
        response = super().render_to_response(context, **response_kwargs)
        response["Content-Security-Policy"] = "frame-ancestors 'self'"
        return response
