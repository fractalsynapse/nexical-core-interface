from app.api import permissions, serializers, views

from . import models


#
# Update Handler
#
def create_project_event(self, instance):
    if not self.context["request"].user.check_member("engine"):
        instance.create_event()


#
# Model Endpoints
#
views.generate(
    models.TeamProject,
    permission_classes=[permissions.TeamModelPermissions],
    filter_fields={
        "id": "id",
        "name": "short_text",
        "created": "date_time",
        "updated": "date_time",
        "summary_model": "short_text",
        "summary_persona": "long_text",
        "format_prompt": "long_text",
        "temperature": "number",
        "top_p": "number",
        "repetition_penalty": "number",
        "team__id": "id",
        "team__name": "short_text",
        "team__created": "date_time",
        "team__updated": "date_time",
        "team__owner__id": "id",
        "team__owner__email": "short_text",
        "team__owner__first_name": "short_text",
        "team__owner__last_name": "short_text",
        "team__owner__date_joined": "date_time",
        "team__owner__last_login": "date_time",
        "team__members__user__id": "id",
        "team__members__user__email": "short_text",
        "team__members__user__first_name": "short_text",
        "team__members__user__last_name": "short_text",
        "team__members__user__date_joined": "date_time",
        "team__members__user__last_login": "date_time",
        "documents__id": "id",
        "documents__name": "short_text",
        "documents__created": "date_time",
        "documents__updated": "date_time",
        "documents__processed_time": "date_time",
    },
    validator=serializers.validate_team_membership,
    get_queryset=views.get_team_queryset,
    ordering_fields=["name"],
    search_fields=["name"],
    view_fields=[
        "id",
        "name",
        "created",
        "updated",
        "summary_model",
        "summary_persona",
        "format_prompt",
        "documents",
        "projects",
        "access_teams",
    ],
    save_fields=[
        "id",
        "name",
        "team",
        "access_teams",
        "summary_model",
        "summary_persona",
        "format_prompt",
        "documents",
        "projects",
    ],
    view_relation_fields=["team", "access_teams", "documents", "projects"],
    reverse_prefix="Project",
    handler=create_project_event,
)
