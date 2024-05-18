from rest_framework import serializers as drf_serializers

from app.api import permissions, serializers, views

from . import models


#
# Query Scope
#
def get_queryset(self):
    return self.queryset.filter(members__user__id=self.request.user.id).distinct()


#
# Field Overrides
#
def get_team_owner(model, field_name):
    return drf_serializers.HiddenField(default=drf_serializers.CurrentUserDefault())


#
# Update Handler
#
def create_team_event(self, instance):
    if not self.context["request"].user.check_member("engine"):
        instance.create_event()


#
# Serializers
#
serializers.generate(models.TeamMembership, fields=["created"], relation_fields=["user"])


#
# Model Endpoints
#
views.generate(
    models.Team,
    permission_classes=[permissions.TeamModelPermissions],
    filter_fields={
        "id": "id",
        "name": "short_text",
        "created": "date_time",
        "updated": "date_time",
        "owner__id": "id",
        "owner__email": "short_text",
        "owner__first_name": "short_text",
        "owner__last_name": "short_text",
        "owner__date_joined": "date_time",
        "owner__last_login": "date_time",
        "members__user__id": "id",
        "members__user__email": "short_text",
        "members__user__first_name": "short_text",
        "members__user__last_name": "short_text",
        "members__user__date_joined": "date_time",
        "members__user__last_login": "date_time",
    },
    get_queryset=get_queryset,
    ordering_fields=["name"],
    search_fields=["name"],
    view_fields=["id", "name", "created", "updated"],
    save_fields=["name", "owner"],
    view_relation_fields=["owner"],
    view_reverse_fields=["members"],
    create_extra_fields={"owner": get_team_owner},
    handler=create_team_event,
)
