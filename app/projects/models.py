from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from app.documents.models import TeamDocumentCollection
from app.events.models import Event
from app.teams.models import Team, get_team_settings, update_team_settings
from app.utils.models import BaseUUIDModel

SUMMARY_MODELS = (("mixtral_di_7bx8", _("Mixtral 8x7b (Default)")),)


def get_active_project(user, id_only=False):
    try:
        team_settings = get_team_settings(user)
        project_id = team_settings.get("active_project", None)
        if project_id:
            return TeamProject.objects.get(id=project_id) if not id_only else project_id
    except TeamProject.DoesNotExist:
        pass
    return None


def set_active_project(user, project_id):
    update_team_settings(user, active_project=str(project_id))


class TeamProject(BaseUUIDModel):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="projects")
    name = models.CharField(_("Project Name"), blank=False, max_length=255)

    summary_model = models.CharField(
        _("Summarization Model"), max_length=60, choices=SUMMARY_MODELS, default="mixtral_di_7bx8"
    )
    summary_persona = models.TextField(_("Research Persona"), blank=True, default="")
    format_prompt = models.TextField(
        _("Format instructions"),
        blank=True,
        default="""
Generate an engaging summary on the topic with appropriate headings, subheadings, paragraphs, and bullet points.
    """.strip(),
    )

    temperature = models.FloatField(_("Summary Temperature"), blank=False, default=0.1)
    top_p = models.FloatField(_("Summary Top-P"), blank=False, default=0.9)
    repetition_penalty = models.FloatField(_("Summary Repetition Penalty"), blank=False, default=0.9)

    documents = models.ManyToManyField(TeamDocumentCollection, related_name="projects", blank=True)

    def __str__(self):
        return self.name

    def create_event(self, operation="update"):
        Event.objects.create(
            type="project",
            data={
                "operation": operation,
                "team_id": str(self.team.id),
                "team_name": self.team.name,
                "id": str(self.id),
                "name": self.name,
                "summary_model": self.summary_model,
                "summary_persona": self.summary_persona,
                "format_prompt": self.format_prompt,
                "temperature": self.temperature,
                "top_p": self.top_p,
                "repetition_penalty": self.repetition_penalty,
                "documents": [str(id) for id in self.documents.values_list("id", flat=True)],
            },
        )
        if operation != "delete":
            self.save()


@receiver(post_delete, sender=TeamProject)
def delete_project_hook(sender, instance, using, **kwargs):
    instance.create_event("delete")
