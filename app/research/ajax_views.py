from django.http import JsonResponse
from django.views import View
from django.views.generic import TemplateView
from rest_framework import status

from app.documents.models import TeamDocument
from app.projects.models import TeamProject
from app.teams.models import TeamTag, get_active_team
from app.utils.auth import BusinessTeamAccessMixin

from .models import ProjectNote, ProjectResearchBase, ProjectSummary
from .note import get_note, save_note
from .summary import summarize


class BaseAjaxSummaryView(BusinessTeamAccessMixin, View):
    def _validate_team(self, team):
        if not team:
            return JsonResponse(
                {"error": "Requesting user is not a member of a team"}, status=status.HTTP_400_BAD_REQUEST
            )
        return None


def get_summary_references(summary):
    references = []
    total_score = sum(summary.references.all().values_list("score", flat=True))

    for reference in summary.references.all().order_by("-score"):
        information = {"type": reference.type, "score": round((reference.score / total_score) * 100, 0)}
        try:
            document = TeamDocument.objects.get(id=reference.document_id)
            information["name"] = document.file.path.split("/")[-1]
            information["link"] = document.file.url

        except TeamDocument.DoesNotExist:
            pass

        references.append(information)
    return references


class SummaryView(BaseAjaxSummaryView):
    def get(self, request, *args, **kwargs):
        team = get_active_team(request.user)
        error = self._validate_team(team)
        if error:
            return error

        try:
            summary = ProjectSummary.objects.get(project__team=team, id=self.kwargs["pk"])
        except ProjectSummary.DoesNotExist:
            return JsonResponse({"error": "Summary not found in active team"}, status=status.HTTP_400_BAD_REQUEST)

        tags = list(summary.tags.values_list("name", flat=True))
        tag_options = []

        for tag in TeamTag.objects.filter(team=team):
            tag_options.append({"name": tag.name, "active": tag.name in tags})

        return JsonResponse(
            {
                "project_id": str(summary.project.id),
                "id": summary.id,
                "prompt": summary.prompt,
                "summary": summary.summary,
                "tags": tag_options,
                "processed_time": summary.processed_time,
                "references": get_summary_references(summary),
            },
            status=status.HTTP_200_OK,
        )


class SummarySaveView(BaseAjaxSummaryView):
    def validate_params(self, project_id, prompt):
        if not project_id or not prompt:
            return JsonResponse(
                {"error": "Parameters 'project_id' and 'prompt' are required for summarization"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return None

    def post(self, request, *args, **kwargs):
        team = get_active_team(request.user)
        project_id = request.POST.get("project_id", None)
        prompt = request.POST.get("prompt", None)

        tags = request.POST.get("tags", [])
        if isinstance(tags, str):
            tags = tags.split(",") if tags else []

        error = self._validate_team(team)
        if error:
            return error

        error = self.validate_params(project_id, prompt)
        if error:
            return error

        try:
            project = TeamProject.objects.get(team=team, pk=project_id)
        except TeamProject.DoesNotExist:
            return JsonResponse({"error": "Project not found in active team"}, status=status.HTTP_400_BAD_REQUEST)

        summary = summarize(
            project,
            tags=tags,
            prompt=prompt,
            format="{}. Generate the response in HTML format.".format(project.format_prompt.strip().removesuffix(".")),
            endings=["</html>", "</div>", "</p>"],
            persona=project.summary_persona,
            temperature=project.temperature,
            top_p=project.top_p,
            repetition_penalty=project.repetition_penalty,
        )
        if not summary:
            return JsonResponse({"error": "Error creating summary"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return JsonResponse(
            {
                "project_id": str(summary.project.id),
                "id": summary.id,
                "prompt": summary.prompt,
                "summary": summary.summary,
                "tags": list(summary.tags.values_list("name", flat=True)),
                "references": get_summary_references(summary),
            },
            status=status.HTTP_200_OK,
        )


class SummaryRemoveView(BaseAjaxSummaryView):
    def get(self, request, *args, **kwargs):
        team = get_active_team(request.user)
        error = self._validate_team(team)
        if error:
            return error

        ProjectSummary.objects.filter(project__team=team, id=self.kwargs["pk"]).delete()
        return JsonResponse({}, status=status.HTTP_204_NO_CONTENT)


class BaseAjaxNoteView(BusinessTeamAccessMixin, View):
    def _validate_team(self, team):
        if not team:
            return JsonResponse(
                {"error": "Requesting user is not a member of a team"}, status=status.HTTP_400_BAD_REQUEST
            )
        return None


class NoteView(BaseAjaxNoteView):
    def get(self, request, *args, **kwargs):
        team = get_active_team(request.user)
        error = self._validate_team(team)
        if error:
            return error

        return get_note(JsonResponse, team, self.kwargs["pk"])


class NoteSaveView(BaseAjaxNoteView):
    def validate_params(self, project_id, message):
        if not project_id or not message:
            return JsonResponse(
                {"error": "Parameters 'project_id' and 'message' are required for notes"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return None

    def post(self, request, *args, **kwargs):
        team = get_active_team(request.user)
        note_id = request.POST.get("note_id", None)
        project_id = request.POST.get("project_id", None)
        message = request.POST.get("message", None)

        tags = request.POST.get("tags", [])
        if isinstance(tags, str):
            tags = tags.split(",") if tags else []

        error = self._validate_team(team)
        if error:
            return error

        error = self.validate_params(project_id, message)
        if error:
            return error

        try:
            project = TeamProject.objects.get(team=team, pk=project_id)
        except TeamProject.DoesNotExist:
            return JsonResponse({"error": "Project not found in active team"}, status=status.HTTP_400_BAD_REQUEST)

        return save_note(JsonResponse, project, note_id, message, tags)


class NoteRemoveView(BaseAjaxNoteView):
    def get(self, request, *args, **kwargs):
        team = get_active_team(request.user)
        error = self._validate_team(team)
        if error:
            return error

        ProjectNote.objects.filter(project__team=team, id=self.kwargs["pk"]).delete()
        return JsonResponse({}, status=status.HTTP_204_NO_CONTENT)


class TimelineListView(BusinessTeamAccessMixin, TemplateView):
    template_name = "components/timeline.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        team = get_active_team(self.request.user)
        try:
            project = TeamProject.objects.get(team=team, pk=self.kwargs["pk"])
        except TeamProject.DoesNotExist:
            return JsonResponse({"error": "Project not found in active team"}, status=status.HTTP_400_BAD_REQUEST)

        context["project"] = project
        context["tags"] = TeamTag.objects.filter(team=team).order_by("name")

        if self.request.GET.get("tag", None) and self.request.GET["tag"]:
            context["active_tag"] = self.request.GET["tag"]
            timeline = ProjectResearchBase.objects.filter(
                project=project, tags__name=self.request.GET["tag"]
            ).order_by("-updated")
        else:
            context["active_tag"] = ""
            timeline = ProjectResearchBase.objects.filter(project=project).order_by("-updated")

        context["timeline"] = []
        for instance in timeline:
            instance_data = None

            if getattr(instance, "projectnote", None):
                instance_data = {"type": "note", "model": instance.projectnote}
            elif getattr(instance, "projectsummary", None):
                instance_data = {"type": "summary", "model": instance.projectsummary}

            if instance_data:
                context["timeline"].append(instance_data)

        return context

    def render_to_response(self, context, **response_kwargs):
        response = super().render_to_response(context, **response_kwargs)
        response["Content-Security-Policy"] = "frame-ancestors 'self'"
        return response
