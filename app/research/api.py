import time

from rest_framework.serializers import CharField, ListField

from app.api import permissions, serializers, views
from app.teams.models import TeamTag
from app.utils.python import get_identifier

from . import models


#
# Access Permissions Checks
#
def validate_summary(self, validated_data):
    validated_data = serializers.validate_team_membership(self, validated_data, field="project__team")

    if not self.instance:
        validated_data["id"] = get_identifier(
            {
                "project_id": str(validated_data["project"].id),
                "prompt": validated_data["prompt"],
                "format": validated_data.get("format", ""),
                "endings": validated_data.get("endings", [".", "?", "!"]),
                "max_sections": validated_data.get("max_sections", 10),
                "sentence_limit": validated_data.get("sentence_limit", 50),
                "persona": validated_data.get("persona", ""),
                "temperature": validated_data.get("temperature", 0.1),
                "top_p": validated_data.get("top_p", 0.9),
                "repetition_penalty": validated_data.get("repetition_penalty", 0.9),
            }
        )
        tags = []
        for tag_name in validated_data.pop("tag_names", []):
            (tag, created) = TeamTag.objects.get_or_create(team=validated_data["project"].team, name=tag_name.lower())
            tags.append(tag.id)

        validated_data["tags"] = tags
        self.Meta.model.objects.filter(id=validated_data["id"]).delete()

    return validated_data


def validate_note(self, validated_data):
    validated_data = serializers.validate_team_membership(self, validated_data, field="project__team")

    if not self.instance:
        validated_data["id"] = get_identifier(
            {
                "project_id": str(validated_data["project"].id),
                "timestamp": str(time.time_ns()),
            }
        )

    if "tag_names" in validated_data:
        tags = []
        for tag_name in validated_data.pop("tag_names", []):
            (tag, created) = TeamTag.objects.get_or_create(team=validated_data["project"].team, name=tag_name.lower())
            tags.append(tag.id)

        validated_data["tags"] = tags

    return validated_data


#
# Query Scope
#
def get_project_queryset(self):
    return views.get_team_queryset(self, "project__team")


#
# Field Overrides
#
def get_tags_field(model, field_name):
    return ListField(child=CharField(), write_only=True)


#
# Update Handler
#
def create_summary_event(self, instance):
    if not self.context["request"].user.check_member("engine"):
        instance.create_event()


#
# Serializers
#
serializers.generate(TeamTag, class_prefix="Project", fields=["name"])

serializers.generate(models.SummaryDocument, class_prefix="Summary", fields=["type", "document_id", "score"])

#
# Model Endpoints
#
views.generate(
    models.ProjectSummary,
    permission_classes=[permissions.TeamModelPermissions],
    filter_fields={
        "id": "id",
        "prompt": "long_text",
        "summary": "long_text",
        "created": "date_time",
        "updated": "date_time",
        "project__id": "id",
        "project__name": "short_text",
        "project__team__id": "id",
        "project__team__name": "short_text",
    },
    validator=validate_summary,
    get_queryset=get_project_queryset,
    ordering_fields=["-updated"],
    search_fields=["prompt", "format", "summary"],
    relation_prefix="Project",
    view_fields=[
        "id",
        "created",
        "updated",
        "prompt",
        "format",
        "endings",
        "max_sections",
        "sentence_limit",
        "token_count",
        "processing_time",
        "processed_time",
        "summary",
        "project",
        "tags",
    ],
    create_fields=[
        "prompt",
        "format",
        "endings",
        "max_sections",
        "sentence_limit",
        "project",
        ("tags", {"read_only": True}),
    ],
    create_extra_fields={"tag_names": get_tags_field},
    update_fields=["token_count", "processing_time", "processing_cost", "processed_time", "summary"],
    view_relation_fields=["project", "tags"],
    reverse_prefix="Summary",
    view_reverse_fields=["references"],
    update_reverse_fields=["references"],
    handler=create_summary_event,
)

views.generate(
    models.ProjectNote,
    permission_classes=[permissions.TeamModelPermissions],
    filter_fields={
        "id": "id",
        "message": "long_text",
        "created": "date_time",
        "updated": "date_time",
        "project__id": "id",
        "project__name": "short_text",
        "project__team__id": "id",
        "project__team__name": "short_text",
    },
    validator=validate_note,
    get_queryset=get_project_queryset,
    ordering_fields=["-updated"],
    search_fields=["message"],
    relation_prefix="Project",
    fields=[
        "message",
        "project",
        ("tags", {"read_only": True}),
    ],
    view_fields=["id", "created", "updated"],
    create_extra_fields={"tag_names": get_tags_field},
    view_relation_fields=["project", "tags"],
)
