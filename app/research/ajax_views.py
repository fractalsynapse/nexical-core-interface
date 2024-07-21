import math
import re

from django.http import JsonResponse
from django.urls import reverse
from django.utils.html import format_html
from django.views import View
from django.views.generic import TemplateView
from rest_framework import status

from app.documents.models import TeamBookmark, TeamDocument
from app.projects.models import TeamProject
from app.teams.models import TeamAccessError, TeamTag, get_active_team, get_team_instance, update_team_settings
from app.utils.auth import TeamAccessMixin

from .models import ProjectNote, ProjectResearchBase, ProjectSummary
from .note import save_note
from .summary import summarize


class BaseAjaxSummaryView(TeamAccessMixin, View):
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
        if reference.type in ["team_document", "file"]:
            try:
                document = TeamDocument.objects.get(id=reference.document_id)
                name = document.file.path.split("/")[-1]

                information["id"] = document.id
                information["type"] = f"File @ {document.collection.team}"
                information["link"] = format_html(f'<a href="{document.file.url}" target="_blank">{name}</a>')
            except TeamDocument.DoesNotExist:
                information = None

        elif reference.type == "bookmark":
            try:
                bookmark = TeamBookmark.objects.get(id=reference.document_id)

                information["id"] = bookmark.id
                information["type"] = f"Bookmark @ {bookmark.collection.team}"
                information["link"] = format_html(
                    f'<a href="{bookmark.url}" class="bookmark-ref-link" target="_blank">{bookmark.url}</a>'
                )

            except TeamBookmark.DoesNotExist:
                information = None

        elif reference.type == "note":
            try:
                note = ProjectNote.objects.get(id=reference.document_id)
                link = reverse("research:note", kwargs={"pk": note.id})

                information["id"] = note.id
                information["type"] = f"Note @ {note.project.team}"
                information["link"] = format_html(f'<a href="{link}" class="note-ref-link">{note.name}</a>')

            except ProjectNote.DoesNotExist:
                information = None

        elif reference.type == "summary":
            try:
                summary = ProjectSummary.objects.get(id=reference.document_id)
                text = re.sub(r"<.*?>", "", summary.summary)
                name = summary.name if summary.name else ((text[:50] + "...") if len(text) > 50 else text)
                link = reverse("research:summary", kwargs={"pk": summary.id})

                information["id"] = summary.id
                information["type"] = f"Summary @ {summary.project.team}"
                information["link"] = format_html(f'<a href="{link}" class="summary-ref-link">{name}</a>')

            except ProjectSummary.DoesNotExist:
                information = None

        if information:
            references.append(information)

    return references


class SummaryView(BaseAjaxSummaryView):
    def get(self, request, *args, **kwargs):
        team = get_active_team(request.user)
        try:
            summary = get_team_instance(
                team, ProjectSummary, self.kwargs["pk"], team_field="project__team", share_model_class=TeamProject
            )
        except TeamAccessError as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        tags = list(summary.tags.values_list("name", flat=True))
        tag_options = []

        for tag in TeamTag.objects.filter(team=team):
            tag_options.append({"name": tag.name, "active": tag.name in tags})

        summary_text = summary.summary

        return JsonResponse(
            {
                "project_id": str(summary.project.id),
                "id": summary.id,
                "name": summary.name,
                "prompt": summary.prompt,
                "use_format": summary.use_default_format,
                "depth": math.floor(summary.sentence_limit / (20 * 5)),
                "summary": summary_text,
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
        name = request.POST.get("name", None)
        prompt = request.POST.get("prompt", None)
        use_format = request.POST.get("use_format", True)
        if isinstance(use_format, str):
            use_format = True if use_format.lower() == "true" else False

        depth = int(request.POST.get("depth", 5))
        max_sections = depth * 5
        sentence_limit = max_sections * 20

        update_team_settings(request.user, default_summary_depth=depth)

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
            request.user,
            project,
            tags=tags,
            name=name,
            prompt=prompt,
            format="Generate the response in HTML format.",
            use_default_format=use_format,
            endings=["</html>", "</div>", "</p>", ".", "!", "?"],
            max_sections=max_sections,
            sentence_limit=sentence_limit,
            persona=project.summary_persona,
            temperature=project.temperature,
            top_p=project.top_p,
            repetition_penalty=project.repetition_penalty,
        )
        if not summary:
            return JsonResponse({"error": "Error creating summary"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        summary_text = summary.summary

        return JsonResponse(
            {
                "project_id": str(summary.project.id),
                "id": summary.id,
                "name": summary.name,
                "prompt": summary.prompt,
                "use_format": summary.use_default_format,
                "depth": depth,
                "summary": summary_text,
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


class BaseAjaxNoteView(TeamAccessMixin, View):
    def _validate_team(self, team):
        if not team:
            return JsonResponse(
                {"error": "Requesting user is not a member of a team"}, status=status.HTTP_400_BAD_REQUEST
            )
        return None


class NoteView(BaseAjaxNoteView):
    def get(self, request, *args, **kwargs):
        team = get_active_team(request.user)
        try:
            note = get_team_instance(
                team, ProjectNote, self.kwargs["pk"], team_field="project__team", share_model_class=TeamProject
            )
        except TeamAccessError as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        tags = list(note.tags.values_list("name", flat=True))
        tag_options = []

        for tag in TeamTag.objects.filter(team=team):
            tag_options.append({"name": tag.name, "active": tag.name in tags})

        return JsonResponse(
            {"id": note.id, "name": note.name, "message": note.message, "tags": tag_options}, status=status.HTTP_200_OK
        )


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
        name = request.POST.get("name", None)
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

        if note_id:
            try:
                note = ProjectNote.objects.get(pk=note_id)
            except ProjectNote.DoesNotExist:
                return JsonResponse({"error": "Project note not found"}, status=status.HTTP_400_BAD_REQUEST)

            if project.team.id != note.project.team.id:
                note_id = None

        return save_note(JsonResponse, project, note_id, name, message, tags)


class NoteRemoveView(BaseAjaxNoteView):
    def get(self, request, *args, **kwargs):
        team = get_active_team(request.user)
        error = self._validate_team(team)
        if error:
            return error

        ProjectNote.objects.filter(project__team=team, id=self.kwargs["pk"]).delete()
        return JsonResponse({}, status=status.HTTP_204_NO_CONTENT)


class TimelineListView(TeamAccessMixin, TemplateView):
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
