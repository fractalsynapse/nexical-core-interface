import time

from rest_framework import status

from app.teams.models import TeamTag
from app.utils.python import get_identifier

from .models import ProjectNote


def get_note(response_class, team, note_id):
    try:
        note = ProjectNote.objects.get(project__team=team, id=note_id)
    except ProjectNote.DoesNotExist:
        return response_class(
            {"error": "Project note does not exist within team"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    tags = list(note.tags.values_list("name", flat=True))
    tag_options = []

    for tag in TeamTag.objects.filter(team=team):
        tag_options.append({"name": tag.name, "active": tag.name in tags})

    return response_class(
        {"id": note.id, "name": note.name, "message": note.message, "tags": tag_options}, status=status.HTTP_200_OK
    )


def save_note(response_class, project, note_id, name, message, tags):
    if not note_id:
        note_id = get_identifier({"project_id": str(project.id), "timestamp": time.time_ns()})

    tags = [tag.lower() for tag in tags]

    try:
        note = ProjectNote.objects.get(id=note_id, project=project)
        note.name = name
        note.message = message
        note.save()

    except ProjectNote.DoesNotExist:
        note = ProjectNote.objects.create(id=note_id, project=project, name=name, message=message)

    note.tags.clear()
    for tag in tags:
        (tag, created) = TeamTag.objects.get_or_create(name=tag.lower(), team=project.team)
        note.tags.add(tag)

    return response_class(
        {"id": note.id, "name": note.name, "message": note.message, "tags": tags}, status=status.HTTP_200_OK
    )
