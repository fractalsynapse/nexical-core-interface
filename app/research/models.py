from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from app.events.models import Event
from app.projects.models import TeamProject
from app.teams.models import TeamTag
from app.utils.fields import ListField
from app.utils.models import BaseHashedModel, BaseUUIDModel


class ProjectResearchBase(BaseHashedModel):
    name = models.CharField(_("Name"), blank=True, null=True, max_length=255)
    project = models.ForeignKey(TeamProject, on_delete=models.CASCADE, related_name="research_data", blank=False)
    tags = models.ManyToManyField(TeamTag, related_name="research_data", blank=True)


class ProjectSummary(ProjectResearchBase):
    prompt = models.TextField(_("Summary Prompt"), blank=False)
    format = models.TextField(_("Summary Format"), blank=True)
    endings = ListField(_("Summary allowed endings"), blank=True, default=[".", "?", "!"])
    summary = models.TextField(_("Summary"), blank=True, null=True)
    token_count = models.IntegerField(_("Summary Token Count"), blank=True, null=True)
    processing_time = models.FloatField(_("Summary Processing Time"), blank=True, null=True)
    processing_cost = models.FloatField(_("Summary Processing Cost"), blank=True, null=True)
    processed_time = models.DateTimeField(_("Processed Time"), blank=True, null=True)

    def create_event(self, operation="update"):
        Event.objects.create(
            type="summary",
            data={
                "operation": operation,
                "id": str(self.id),
                "name": self.name,
                "team_id": str(self.project.team.id),
                "project_id": str(self.project.id),
                "prompt": self.prompt,
                "format": self.format,
                "endings": self.endings,
            },
        )
        if operation != "delete":
            self.processed_time = None
            self.save()


@receiver(post_delete, sender=ProjectSummary)
def delete_summary_hook(sender, instance, using, **kwargs):
    instance.create_event("delete")


class SummaryDocument(BaseUUIDModel):
    summary = models.ForeignKey(ProjectSummary, on_delete=models.CASCADE, related_name="references", blank=False)
    score = models.FloatField(_("Document Score"), blank=False)
    type = models.CharField(_("Document Type"), blank=False, max_length=255)
    document_id = models.CharField(_("Document ID"), blank=False, max_length=65)

    def __str__(self):
        return f"{self.summary.id}: {self.type} {self.document_id}"


class ProjectNote(ProjectResearchBase):
    message = models.TextField(_("Note Message"), blank=False)

    def create_event(self, operation="update"):
        Event.objects.create(
            type="note",
            data={
                "operation": operation,
                "id": str(self.id),
                "name": self.name,
                "team_id": str(self.project.team.id),
                "project_id": str(self.project.id),
                "message": self.message,
            },
        )


@receiver(post_delete, sender=ProjectNote)
def delete_note_hook(sender, instance, using, **kwargs):
    instance.create_event("delete")
