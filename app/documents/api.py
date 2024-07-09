from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field

from app.api import permissions, serializers, views
from app.utils.file import get_file_content

from . import models


#
# Access Permissions Checks
#
def validate_document(self, validated_data):
    return serializers.validate_team_membership(self, validated_data, team=validated_data["collection"].team)


def validate_bookmark(self, validated_data):
    return serializers.validate_team_membership(self, validated_data, team=validated_data["collection"].team)


#
# Query Scope
#
def get_document_queryset(self):
    return views.get_team_queryset(self, "collection__team")


def get_bookmark_queryset(self):
    return views.get_team_queryset(self, "collection__team")


#
# Field Overrides
#
@extend_schema_field(OpenApiTypes.STR)
def field_file_content(self, instance):
    return get_file_content(instance.file)


#
# Update Handler
#
def create_document_collection_event(self, instance):
    if not self.context["request"].user.check_member("engine"):
        instance.create_event()


def create_document_event(self, instance):
    if not self.context["request"].user.check_member("engine"):
        instance.collection.create_event()


def create_bookmark_event(self, instance):
    if not self.context["request"].user.check_member("engine"):
        instance.collection.create_event()


#
# Serializers
#
serializers.generate(
    models.TeamDocument, class_prefix="DocumentCollection", fields=["id", "file", "description", "created", "updated"]
)
serializers.generate(
    models.TeamBookmark, class_prefix="DocumentCollection", fields=["id", "url", "description", "created", "updated"]
)


#
# Model Endpoints
#
views.generate(
    models.TeamDocument,
    permission_classes=[permissions.TeamModelPermissions],
    filter_fields={
        "id": "id",
        "created": "date_time",
        "updated": "date_time",
        "description": "long_text",
        "collection__id": "id",
        "collection__name": "short_text",
        "collection__created": "date_time",
        "collection__updated": "date_time",
        "collection__processed_time": "date_time",
        "collection__team__id": "id",
        "collection__team__name": "short_text",
        "collection__team__created": "date_time",
        "collection__team__updated": "date_time",
        "collection__team__owner__id": "id",
        "collection__team__owner__email": "short_text",
        "collection__team__owner__first_name": "short_text",
        "collection__team__owner__last_name": "short_text",
        "collection__team__owner__date_joined": "date_time",
        "collection__team__owner__last_login": "date_time",
        "collection__team__members__user__id": "id",
        "collection__team__members__user__email": "short_text",
        "collection__team__members__user__first_name": "short_text",
        "collection__team__members__user__last_name": "short_text",
        "collection__team__members__user__date_joined": "date_time",
        "collection__team__members__user__last_login": "date_time",
    },
    validator=validate_document,
    get_queryset=get_document_queryset,
    ordering_fields=["id"],
    search_fields=["description", "file"],
    fields=["id", "description", "file", "created", "updated"],
    relation_fields=["collection"],
    object_method_fields={"content": field_file_content},
    handler=create_document_event,
)

views.generate(
    models.TeamBookmark,
    permission_classes=[permissions.TeamModelPermissions],
    filter_fields={
        "id": "id",
        "created": "date_time",
        "updated": "date_time",
        "url": "short_text",
        "description": "long_text",
        "collection__id": "id",
        "collection__name": "short_text",
        "collection__created": "date_time",
        "collection__updated": "date_time",
        "collection__processed_time": "date_time",
        "collection__team__id": "id",
        "collection__team__name": "short_text",
        "collection__team__created": "date_time",
        "collection__team__updated": "date_time",
        "collection__team__owner__id": "id",
        "collection__team__owner__email": "short_text",
        "collection__team__owner__first_name": "short_text",
        "collection__team__owner__last_name": "short_text",
        "collection__team__owner__date_joined": "date_time",
        "collection__team__owner__last_login": "date_time",
        "collection__team__members__user__id": "id",
        "collection__team__members__user__email": "short_text",
        "collection__team__members__user__first_name": "short_text",
        "collection__team__members__user__last_name": "short_text",
        "collection__team__members__user__date_joined": "date_time",
        "collection__team__members__user__last_login": "date_time",
    },
    validator=validate_bookmark,
    get_queryset=get_bookmark_queryset,
    ordering_fields=["id"],
    search_fields=["description", "url"],
    fields=["id", "description", "url", "created", "updated"],
    relation_fields=["collection"],
    handler=create_bookmark_event,
)

views.generate(
    models.TeamDocumentCollection,
    permission_classes=[permissions.TeamModelPermissions],
    filter_fields={
        "id": "id",
        "name": "short_text",
        "description": "long_text",
        "created": "date_time",
        "updated": "date_time",
        "processed_time": "date_time",
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
        "files__id": "id",
        "files__created": "date_time",
        "files__updated": "date_time",
        "files__description": "long_text",
        "bookmarks__id": "id",
        "bookmarks__created": "date_time",
        "bookmarks__updated": "date_time",
        "bookmarks__url": "short_text",
        "bookmarks__description": "long_text",
    },
    validator=serializers.validate_team_membership,
    get_queryset=views.get_team_queryset,
    ordering_fields=["name"],
    search_fields=["name"],
    view_fields=["id", "name", "created", "updated", "access_teams"],
    save_fields=["id", "name", "description", "team", "access_teams", "files", "bookmarks"],
    view_relation_fields=["team", "access_teams"],
    update_fields=["processed_time"],
    reverse_prefix="DocumentCollection",
    view_reverse_fields=["files", "bookmarks"],
    handler=create_document_collection_event,
)
