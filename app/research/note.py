import time

from rest_framework import status

from app.teams.models import TeamTag
from app.utils.python import get_identifier

from .models import ProjectNote


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

    note.create_event()

    return response_class(
        {"id": note.id, "name": note.name, "message": note.message, "tags": tags}, status=status.HTTP_200_OK
    )
