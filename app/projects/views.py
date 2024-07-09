import django_tables2
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import redirect

# from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import format_html
from django.views.generic import CreateView, DeleteView, TemplateView, UpdateView

from app.teams.views import TeamOwnershipMixin

from . import forms, models


class ProjectTable(django_tables2.Table):
    name = django_tables2.Column(orderable=False)
    operations = django_tables2.Column(orderable=False, empty_values=(), verbose_name="")

    class Meta:
        model = models.TeamProject
        fields = ["name", "operations"]

    def render_operations(self, value, record):
        operations = ['<div class="text-right">']

        update_url = reverse("projects:form_update", kwargs={"pk": record.id})
        operations.append(
            f'<a class="btn btn-primary px-4 py-2" title="Edit" href="{update_url}">'
            + '<i class="bx bx-edit"></i>'
            + "</a>"
        )
        remove_url = reverse("projects:remove", kwargs={"pk": record.id})
        operations.append(
            f'<a class="btn btn-primary ms-2 px-4 py-2" title="Remove" href="{remove_url}">'
            + '<i class="bx bx-trash-alt"></i>'
            + "</a>"
        )

        operations.append("</div>")
        return format_html("".join(operations))


class ListView(TeamOwnershipMixin, TemplateView):
    template_name = "project_list.html"
    model = models.TeamProject

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()

        context["project_count"] = kwargs["count"]
        context["projects"] = ProjectTable(queryset)

        # context["help_title"] = "Project Help"
        # context["help_body"] = render_to_string("project_help.html")
        return context

    def dispatch(self, request, *args, **kwargs):
        create_redirect = self._initialize_team(request)
        if create_redirect:
            return create_redirect

        queryset = self.get_queryset()
        kwargs["count"] = queryset.count()
        kwargs["disable_check_team"] = True

        if not kwargs["count"]:
            return redirect("projects:form_create")

        return super().dispatch(request, *args, **kwargs)


class FormMixin(TeamOwnershipMixin):
    template_name = "project_form.html"
    model = models.TeamProject
    form_class = forms.ProjectForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["team"] = self.team
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        queryset = self.get_queryset()
        context["project_count"] = queryset.count()

        # context["help_title"] = "Project Help"
        # context["help_body"] = render_to_string("project_help.html")

        if not self.request.user.is_staff:
            messages.warning(
                self.request,
                "This demo environment only provides our default open source AI foundation model,"
                " Mixtral, for summarization but we have plugin providers for other open source"
                " and proprietary AI models available.",
            )
            messages.warning(
                self.request,
                "This demo environment only allows linking to 10 document collections"
                " but this is not a limitation on production systems",
            )
            messages.success(
                self.request,
                "We can add new AI model integrations on request and work with you "
                "to fine tune AI models to your needs",
            )

        return context

    def form_valid(self, form):
        form.instance.team = self.team

        self.object = form.save()
        self.object.create_event()

        if not models.get_active_project(self.request.user):
            models.set_active_project(self.request.user, self.object.id)

        return super().form_valid(form)

    def get_success_url(self, **kwargs):
        return reverse("projects:list")


class CreateFormView(FormMixin, CreateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["operation"] = "create"
        return context


class ModalCreateFormView(CreateFormView):
    template_name = "modal_project_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["modal"] = True
        return context

    def render_to_response(self, context, **response_kwargs):
        response = super().render_to_response(context, **response_kwargs)
        response["Content-Security-Policy"] = "frame-ancestors 'self'"
        return response

    def get_success_url(self, **kwargs):
        return reverse("projects:modal_form_update", kwargs={"pk": self.object.id})


class UpdateFormView(FormMixin, UpdateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["operation"] = "update"
        return context


class ModalUpdateFormView(UpdateFormView):
    template_name = "modal_project_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["modal"] = True
        return context

    def render_to_response(self, context, **response_kwargs):
        response = super().render_to_response(context, **response_kwargs)
        response["Content-Security-Policy"] = "frame-ancestors 'self'"
        return response

    def get_success_url(self, **kwargs):
        return reverse("projects:modal_form_update", kwargs={"pk": self.object.id})


class RemoveView(TeamOwnershipMixin, DeleteView):
    template_name = "project_confirm_delete.html"
    model = models.TeamProject

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.delete()
        return HttpResponseRedirect(success_url)

    def get_success_url(self, **kwargs):
        return reverse("projects:list")
