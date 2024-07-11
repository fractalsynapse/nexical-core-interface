from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from app.events.models import Event
from app.projects.models import TeamProject
from app.teams.models import TeamTag
from app.users.models import User
from app.utils.fields import ListField
from app.utils.models import BaseHashedModel, BaseUUIDModel


class ProjectResearchBase(BaseHashedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="research_artifacts", null=True)
    name = models.CharField(_("Name"), blank=True, null=True, max_length=255)
    project = models.ForeignKey(TeamProject, on_delete=models.CASCADE, related_name="research_data", blank=False)
    tags = models.ManyToManyField(TeamTag, related_name="research_data", blank=True)


class ProjectSummary(ProjectResearchBase):
    prompt = models.TextField(_("Summary Prompt"), blank=False)
    format = models.TextField(_("Summary Format"), blank=True)
    use_default_format = models.BooleanField(_("Summary Use Default Format"), default=True)
    endings = ListField(_("Summary Allowed Endings"), blank=True, default=[".", "?", "!"])
    max_sections = models.IntegerField(_("Summary Maximum Sections per Topic"), default=5)
    sentence_limit = models.IntegerField(_("Summary Maximum Ranked Sentences per Topic"), default=50)
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
                "team_name": self.project.team.name,
                "project_id": str(self.project.id),
                "prompt": self.prompt,
                "format": self.format,
                "use_default_format": self.use_default_format,
                "endings": self.endings,
                "max_sections": self.max_sections,
                "sentence_limit": self.sentence_limit,
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
                "team_name": self.project.team.name,
                "project_id": str(self.project.id),
                "message": self.message,
            },
        )


@receiver(post_delete, sender=ProjectNote)
def delete_note_hook(sender, instance, using, **kwargs):
    instance.create_event("delete")
