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
        _("Summarization AI Model"),
        max_length=60,
        choices=SUMMARY_MODELS,
        default="mixtral_di_7bx8",
        help_text="An AI summarization model is a type of artificial intelligence that can automatically create"
        " a shorter version of a given text, while retaining its most important information."
        " It uses natural language processing and understanding techniques to analyze the source text,"
        " identify key concepts, and generate a coherent and concise summary."
        " This AI summarization model is used for all AI summarization requests in this project.",
    )
    summary_persona = models.TextField(
        _("Research Persona"),
        blank=True,
        default="",
        help_text="A persona in the context of an AI model refers to a detailed representation"
        " of a specific user or user group, incorporating characteristics, behaviors, needs, and motivations."
        " This persona aids in creating personalized and effective AI interactions,"
        " tailoring responses and services to align with the user's preferences and expectations."
        " By understanding the persona, AI models can deliver more contextually relevant and engaging"
        " user experiences, ultimately fostering a stronger connection between the user and the AI system."
        " This research persona is automatically included with all AI summarization requests in this project.",
    )
    format_prompt = models.TextField(
        _("Format instructions"),
        blank=True,
        default="""
Generate an engaging summary on the topic with appropriate headings, subheadings, paragraphs, and bullet points.
    """.strip(),
        help_text="In the context of an AI model, a prompt is the initial input provided to the model"
        " to generate a response. In the case of a format prompt, it is a specific type of prompt"
        " that is used to instruct the AI model on the desired format or structure of the output."
        " This can include details about the desired length, style, or content of the response."
        " This format prompt is automatically included with all AI summarization requests in this project.",
    )

    temperature = models.FloatField(_("Summary Temperature"), blank=False, default=0.1)
    top_p = models.FloatField(_("Summary Top-P"), blank=False, default=0.9)
    repetition_penalty = models.FloatField(_("Summary Repetition Penalty"), blank=False, default=0.9)

    documents = models.ManyToManyField(TeamDocumentCollection, related_name="projects", blank=True)
    projects = models.ManyToManyField("TeamProject", related_name="+", blank=True)
    access_teams = models.ManyToManyField(Team, related_name="project_access", blank=True)

    def __str__(self):
        return f"{self.name} @ {self.team}"

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
                "projects": [str(id) for id in self.projects.values_list("id", flat=True)],
                "access_teams": [str(id) for id in self.access_teams.values_list("id", flat=True)],
            },
        )
        if operation != "delete":
            self.save()


@receiver(post_delete, sender=TeamProject)
def delete_project_hook(sender, instance, using, **kwargs):
    instance.create_event("delete")
