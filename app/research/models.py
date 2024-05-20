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
    project = models.ForeignKey(TeamProject, on_delete=models.CASCADE, related_name="research_data", blank=False)
    tags = models.ManyToManyField(TeamTag, related_name="research_data", blank=True)


class ProjectSummary(ProjectResearchBase):
    prompt = models.TextField(_("Summary Prompt"), blank=False)
    persona = models.TextField(_("Summary Persona"), blank=True, default="")
    format = models.TextField(_("Summary Format"), blank=True, default="")
    endings = ListField(_("Summary allowed endings"), blank=True, default=[".", "?", "!"])
    temperature = models.FloatField(_("Summary Temperature"), blank=False, default=0.1)
    top_p = models.FloatField(_("Summary Top-P"), blank=False, default=0.9)
    repetition_penalty = models.FloatField(_("Summary Repetition Penalty"), blank=False, default=0.9)
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
                "project_id": str(self.project.id),
                "team_id": str(self.project.team.id),
                "prompt": self.prompt,
                "persona": self.persona,
                "format": self.format,
                "endings": self.endings,
                "temperature": self.temperature,
                "top_p": self.top_p,
                "repetition_penalty": self.repetition_penalty,
                "documents": [str(id) for id in self.project.documents.values_list("id", flat=True)],
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
