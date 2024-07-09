import django_tables2
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import format_html
from django.views.generic import CreateView, DeleteView, TemplateView, UpdateView

from app.teams.views import TeamOwnershipMixin

from . import forms, models


class DocumentCollectionTable(django_tables2.Table):
    processed = django_tables2.Column(orderable=False, empty_values=(), verbose_name="")
    name = django_tables2.Column(orderable=False)
    operations = django_tables2.Column(orderable=False, empty_values=(), verbose_name="")

    class Meta:
        model = models.TeamDocumentCollection
        fields = ["processed", "name", "operations"]

    def render_processed(self, value, record):
        return render_to_string(
            "components/document_progress.html",
            {
                "progress_url": reverse("documents:progress", kwargs={"pk": record.id}),
                "processed_time": record.processed_time,
            },
        )

    def render_operations(self, value, record):
        operations = ['<div class="text-right">']

        update_url = reverse("documents:form_update", kwargs={"pk": record.id})
        operations.append(
            f'<a class="btn btn-primary px-4 py-2" title="Edit" href="{update_url}">'
            + '<i class="bx bx-edit"></i>'
            + "</a>"
        )
        remove_url = reverse("documents:remove", kwargs={"pk": record.id})
        operations.append(
            f'<a class="btn btn-primary ms-2 px-4 py-2" title="Remove" href="{remove_url}">'
            + '<i class="bx bx-trash-alt"></i>'
            + "</a>"
        )

        operations.append("</div>")
        return format_html("".join(operations))


class ListView(TeamOwnershipMixin, TemplateView):
    template_name = "document_list.html"
    model = models.TeamDocumentCollection

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()

        context["collection_count"] = kwargs["count"]
        context["collections"] = DocumentCollectionTable(queryset)

        # context["help_title"] = "Document Collection Help"
        # context["help_body"] = render_to_string("document_help.html")
        return context

    def dispatch(self, request, *args, **kwargs):
        create_redirect = self._initialize_team(request)
        if create_redirect:
            return create_redirect

        queryset = self.get_queryset()
        kwargs["count"] = queryset.count()
        kwargs["disable_check_team"] = True

        if not kwargs["count"]:
            return redirect("documents:form_create")

        return super().dispatch(request, *args, **kwargs)


class FormMixin(TeamOwnershipMixin):
    template_name = "document_form.html"
    model = models.TeamDocumentCollection
    form_class = forms.DocumentCollectionForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["team"] = self.team
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.POST:
            context["files"] = forms.DocumentCollectionFileFormSet(
                self.request.POST, self.request.FILES, instance=self.object, prefix="files"
            )
            context["bookmarks"] = forms.DocumentCollectionBookmarkFormSet(
                self.request.POST, instance=self.object, prefix="bookmarks"
            )
        else:
            context["files"] = forms.DocumentCollectionFileFormSet(instance=self.object, prefix="files")
            context["bookmarks"] = forms.DocumentCollectionBookmarkFormSet(instance=self.object, prefix="bookmarks")

        queryset = self.get_queryset()
        context["collection_count"] = queryset.count()

        # context["help_title"] = "Document Collection Help"
        # context["help_body"] = render_to_string("document_help.html")

        if not self.request.user.is_staff:
            messages.warning(
                self.request,
                "This demo environment limits files in a collection to 10"
                " but production platforms can contain unlimited files",
            )
            messages.warning(self.request, "Files can be added through the website upload forms or via the API")
            messages.success(self.request, "We can add new file parsers and build custom importers on request")

        return context

    def form_valid(self, form):
        context = self.get_context_data()
        files = context["files"]
        bookmarks = context["bookmarks"]

        with transaction.atomic():
            form.instance.team = self.team
            self.object = form.save()

            if files.is_valid() and bookmarks.is_valid():
                files.instance = self.object
                files.save()

                bookmarks.instance = self.object
                bookmarks.save()

                self.object.create_event()
            else:
                return self.render_to_response(context)

        return super().form_valid(form)

    def get_success_url(self, **kwargs):
        return reverse("documents:list")


class CreateFormView(FormMixin, CreateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["operation"] = "create"
        return context


class UpdateFormView(FormMixin, UpdateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["operation"] = "update"
        return context


class RemoveView(TeamOwnershipMixin, DeleteView):
    template_name = "document_confirm_delete.html"
    model = models.TeamDocumentCollection

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.delete()
        return HttpResponseRedirect(success_url)

    def get_success_url(self, **kwargs):
        return reverse("documents:list")
