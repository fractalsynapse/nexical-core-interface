from django.contrib import messages
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.views.generic import TemplateView

from app.projects.models import TeamProject, get_active_project
from app.teams.models import TeamTag
from app.teams.views import TeamOwnershipMixin
from app.utils.auth import BusinessTeamAccessMixin


class BasePanelView(TeamOwnershipMixin, BusinessTeamAccessMixin, TemplateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["active_project"] = get_active_project(self.request.user)
        context["projects"] = TeamProject.objects.filter(team=self.team)
        context["tags"] = TeamTag.objects.filter(team=self.team)

        context["help_title"] = "Research Help"
        context["help_body"] = render_to_string("research_help.html")
        return context


class PanelView(BasePanelView):
    template_name = "research.html"

    def dispatch(self, request, *args, **kwargs):
        if not get_active_project(request.user):
            messages.add_message(
                request,
                messages.WARNING,
                "Before conducting project related research you must create a project in the active team",
            )
            return redirect("projects:form_create")

        return super().dispatch(request, *args, **kwargs)


class ModalPanelView(BasePanelView):
    template_name = "research_modal.html"

    def render_to_response(self, context, **response_kwargs):
        response = super().render_to_response(context, **response_kwargs)
        response["Content-Security-Policy"] = "frame-ancestors 'self'"
        return response
