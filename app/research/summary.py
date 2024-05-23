from app.teams.models import TeamTag
from app.utils.python import get_identifier

from .models import ProjectSummary


def summarize(project, name, prompt, tags, **config):
    persona = config.get("persona", "")
    output_format = config.get("format", "")
    output_endings = config.get("endings", [".", "?", "!"])
    temperature = config.get("temperature", 0.1)
    top_p = config.get("top_p", 0.9)
    repetition_penalty = config.get("repetition_penalty", 0.9)

    summary_id = get_identifier(
        {
            "project_id": str(project.id),
            "prompt": prompt,
            "format": output_format,
            "endings": output_endings,
            "persona": persona,
            "temperature": temperature,
            "top_p": top_p,
            "repetition_penalty": repetition_penalty,
        }
    )
    try:
        summary = ProjectSummary.objects.get(id=summary_id)
        created = False

    except ProjectSummary.DoesNotExist:
        try:
            summary = ProjectSummary.objects.create(
                id=summary_id, project_id=project.id, prompt=prompt, format=output_format, endings=output_endings
            )
            created = True

        except Exception:
            return None

    summary.tags.clear()
    for tag in [tag.lower() for tag in tags]:
        (tag, unused) = TeamTag.objects.get_or_create(name=tag, team=project.team)
        summary.tags.add(tag)

    summary.name = name
    summary.save()

    if created:
        summary.create_event()

    return summary
