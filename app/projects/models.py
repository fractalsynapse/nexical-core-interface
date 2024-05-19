from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from app.events.models import Event
from app.teams.models import Team
from app.utils.models import BaseUUIDModel


class TeamProject(BaseUUIDModel):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="projects")
    name = models.CharField(_("Project Name"), blank=False, max_length=255)

    summary_prompt = models.TextField(_("Summarization instructions"), blank=True, default="")
    format_prompt = models.TextField(
        _("Format instructions"),
        blank=True,
        default="""
Generate an engaging summary on the topic with appropriate headings, subheadings, paragraphs, and bullet points.
    """.strip(),
    )

    def __str__(self):
        return self.name

    def create_event(self, operation="update"):
        Event.objects.create(
            type="project",
            data={
                "operation": operation,
                "team_id": str(self.team.id),
                "id": str(self.id),
                "name": self.name,
                "summary_prompt": self.summary_prompt,
                "format_prompt": self.format_prompt,
            },
        )
        if operation != "delete":
            self.save()


@receiver(post_delete, sender=TeamProject)
def delete_project_hook(sender, instance, using, **kwargs):
    instance.create_event("delete")
