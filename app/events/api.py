from django.utils.timezone import now
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from app.api import permissions, views

from . import models


#
# Model Endpoints
#
@action(
    detail=False,
    methods=["get"],
    url_path="follow",
    permission_classes=[permissions.EnginePermissions],
    filter_backends=[],
)
def follow(self, request, *args, **kwargs):
    queryset = self.get_queryset().order_by("created")
    current_time = now().strftime("%Y-%m-%dT%H:%M:%SZ")

    if request.user.settings.get("event_access_time", None):
        queryset = queryset.filter(created__gt=request.user.settings["event_access_time"])

    serializer = self.get_serializer(queryset, many=True)
    request.user.settings["event_access_time"] = current_time
    request.user.save()

    return Response(serializer.data, status=status.HTTP_200_OK)


views.generate(
    models.Event,
    permission_classes=[permissions.EnginePermissions],
    filter_fields={"type": "short_text", "created": "date_time"},
    ordering_fields=[],
    search_fields=["-created"],
    fields=["id", "type", "data"],
    view_fields=["created"],
    extra_serializers={"follow": "list"},
    follow=follow,
)
