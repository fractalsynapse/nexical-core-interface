from zoneinfo import available_timezones

from rest_framework import serializers as drf_serializers
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from app.api import permissions, serializers, views

from .models import User


#
# Query Scope
#
def get_queryset(self):
    return views.get_team_queryset(self, "membership__team")


#
# Field Overrides
#
def get_timezone_serializer(model, field_name):
    return drf_serializers.ChoiceField(choices=available_timezones())


#
# Model Endpoints
#
@action(detail=False, permission_classes=[permissions.UserModelPermissions], filter_backends=[])
def me(self, request):
    serializer = serializers.UserListSerializer(request.user, context={"request": request})
    return Response(status=status.HTTP_200_OK, data=serializer.data)


views.generate(
    User,
    permission_classes=[permissions.TeamModelPermissions],
    filter_fields={
        "id": "id",
        "email": "short_text",
        "first_name": "short_text",
        "last_name": "short_text",
        "date_joined": "date_time",
        "last_login": "date_time",
        "membership__team__id": "id",
        "membership__team__name": "short_text",
        "membership__team__created": "date_time",
        "membership__team__updated": "date_time",
    },
    get_queryset=get_queryset,
    ordering_fields=["email"],
    search_fields=["first_name", "last_name", "email"],
    fields=["id", "email", "first_name", "last_name"],
    view_fields=["date_joined", "last_login"],
    extra_fields={"timezone": get_timezone_serializer},
    me=me,
)
