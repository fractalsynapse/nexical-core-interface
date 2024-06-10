import json

import django_tables2
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.template import Context, Template
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html
from django.views.generic import CreateView, DeleteView, ListView, TemplateView, UpdateView

from app.outreach.messages import create_message
from app.utils.auth import OutreachAccessMixin

from . import forms, models


class ContactGroupTable(django_tables2.Table):
    name = django_tables2.Column(orderable=True)
    description = django_tables2.Column(orderable=False)
    contacts = django_tables2.Column(orderable=True, empty_values=(), verbose_name="Contacts")
    organizations = django_tables2.Column(orderable=True, empty_values=(), verbose_name="Organizations")
    operations = django_tables2.Column(orderable=False, empty_values=(), verbose_name="")

    class Meta:
        model = models.ContactGroup
        fields = ["name", "description", "contacts", "organizations", "operations"]

    def render_description(self, value, record):
        return format_html(f'<div class="text-wrap">{value}</div>')

    def render_contacts(self, value, record):
        contact_count = models.Contact.objects.filter(membership__contact_group__id=record.id).distinct().count()
        return format_html(f'<div class="text-right">{contact_count}</div>')

    def render_organizations(self, value, record):
        organization_count = (
            models.Organization.objects.filter(contacts__membership__contact_group__id=record.id).distinct().count()
        )
        return format_html(f'<div class="text-right">{organization_count}</div>')

    def render_operations(self, value, record):
        operations = ['<div class="text-end">']

        update_url = reverse("outreach:form_contact_group_update", kwargs={"pk": record.id})
        operations.append(
            f'<a class="btn btn-outline-primary ms-2" title="Edit" href="{update_url}">'
            + '<i class="bx bx-edit"></i>'
            + "</a>"
        )
        remove_url = reverse("outreach:contact_group_remove", kwargs={"pk": record.id})
        operations.append(
            f'<a class="btn btn-outline-primary ms-2" title="Remove" href="{remove_url}">'
            + '<i class="bx bx-trash-alt"></i>'
            + "</a>"
        )

        operations.append("</div>")
        return format_html("".join(operations))


class CampaignTable(django_tables2.Table):
    name = django_tables2.Column(orderable=False)
    owner = django_tables2.Column(orderable=False)
    description = django_tables2.Column(orderable=False)
    operations = django_tables2.Column(orderable=False, empty_values=(), verbose_name="")

    class Meta:
        model = models.Campaign
        fields = ["name", "owner", "description", "operations"]

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def render_description(self, value, record):
        return format_html(f'<div class="text-wrap">{value}</div>')

    def render_owner(self, value, record):
        return f"{value.first_name} {value.last_name} ({value.email})"

    def render_operations(self, value, record):
        operations = ['<div class="text-end">']

        if self.user == record.owner:
            process_url = reverse("outreach:campaign_process", kwargs={"pk": record.id})
            operations.append(
                f'<a class="btn btn-outline-primary " title="Process" href="{process_url}">'
                + '<i class="bx bx-mail-send"></i>'
                + "</a>"
            )
        update_url = reverse("outreach:form_campaign_update", kwargs={"pk": record.id})
        operations.append(
            f'<a class="btn btn-outline-primary ms-2" title="Edit" href="{update_url}">'
            + '<i class="bx bx-edit"></i>'
            + "</a>"
        )
        remove_url = reverse("outreach:campaign_remove", kwargs={"pk": record.id})
        operations.append(
            f'<a class="btn btn-outline-primary ms-2" title="Remove" href="{remove_url}">'
            + '<i class="bx bx-trash-alt"></i>'
            + "</a>"
        )

        operations.append("</div>")
        return format_html("".join(operations))


class ContactGroupListView(OutreachAccessMixin, ListView):
    template_name = "contact_group_list.html"
    model = models.ContactGroup

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["contact_groups"] = ContactGroupTable(self.get_queryset())

        # context["help_title"] = "Contact Group Help"
        # context["help_body"] = render_to_string("contact_group_help.html")
        return context

    def dispatch(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        kwargs["count"] = queryset.count()

        if not kwargs["count"]:
            return redirect("outreach:form_contact_group_create")

        return super().dispatch(request, *args, **kwargs)


class ContactGroupFormMixin(OutreachAccessMixin):
    template_name = "contact_group_form.html"
    model = models.ContactGroup
    form_class = forms.ContactGroupForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        queryset = self.get_queryset()
        context["contact_group_count"] = queryset.count()

        # context["help_title"] = "Contact Group Help"
        # context["help_body"] = render_to_string("contact_group_help.html")
        return context

    def get_success_url(self, **kwargs):
        return reverse("outreach:contact_group_list")


class ContactGroupCreateFormView(ContactGroupFormMixin, CreateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["operation"] = "create"
        return context


class ContactGroupUpdateFormView(ContactGroupFormMixin, UpdateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["operation"] = "update"
        return context


class ContactGroupRemoveView(OutreachAccessMixin, DeleteView):
    template_name = "contact_group_confirm_delete.html"
    model = models.ContactGroup

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.delete()
        return HttpResponseRedirect(success_url)

    def get_success_url(self, **kwargs):
        return reverse("outreach:contact_group_list")


class CampaignListView(OutreachAccessMixin, ListView):
    template_name = "campaign_list.html"
    model = models.Campaign

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["campaigns"] = CampaignTable(self.request.user, self.get_queryset())

        # context["help_title"] = "Campaign Help"
        # context["help_body"] = render_to_string("campaign_help.html")
        return context

    def dispatch(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        kwargs["count"] = queryset.count()

        if not kwargs["count"]:
            return redirect("outreach:form_campaign_create")

        return super().dispatch(request, *args, **kwargs)


class CampaignFormMixin(OutreachAccessMixin):
    template_name = "campaign_form.html"
    model = models.Campaign
    form_class = forms.CampaignForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.POST:
            context["emails"] = forms.CampaignEmailFormSet(self.request.POST, instance=self.object, prefix="emails")
        else:
            context["emails"] = forms.CampaignEmailFormSet(instance=self.object, prefix="emails")

        queryset = self.get_queryset()
        context["campaign_count"] = queryset.count()

        message_context = {}
        contact = None

        if self.object:
            contact = models.Contact.objects.filter(
                membership__contact_group__id__in=list(
                    self.object.contact_groups.all().distinct().values_list("id", flat=True)
                ),
                blocked=False,
            ).first()

        if contact:
            for key, value in self.request.user.export().items():
                message_context[f"{{{{user.{key}}}}}"] = value
            for key, value in contact.organization.export().items():
                message_context[f"{{{{organization.{key}}}}}"] = value
            for key, value in contact.export().items():
                message_context[f"{{{{contact.{key}}}}}"] = value

        context["message_context"] = message_context

        # context["help_title"] = "Campaign Help"
        # context["help_body"] = render_to_string("campaign_help.html")
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        emails = context["emails"]

        with transaction.atomic():
            form.set_owner(self.request.user)
            self.object = form.save()

            if emails.is_valid():
                emails.instance = self.object
                emails.save()

                self.object.create_event("update")
            else:
                return self.render_to_response(context)

        return super().form_valid(form)

    def get_success_url(self, **kwargs):
        return reverse("outreach:campaign_list")

    def dispatch(self, request, *args, **kwargs):
        if not models.ContactGroup.objects.all().count():
            return redirect("outreach:form_contact_group_create")

        return super().dispatch(request, *args, **kwargs)


class CampaignCreateFormView(CampaignFormMixin, CreateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["operation"] = "create"
        return context


class CampaignUpdateFormView(CampaignFormMixin, UpdateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["operation"] = "update"
        return context


class CampaignRemoveView(OutreachAccessMixin, DeleteView):
    template_name = "campaign_confirm_delete.html"
    model = models.Campaign

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.delete()
        return HttpResponseRedirect(success_url)

    def get_success_url(self, **kwargs):
        return reverse("outreach:campaign_list")


class ProcessView(OutreachAccessMixin, TemplateView):
    template_name = "outreach_process.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        messages = models.Message.objects.filter(
            sequence__campaign=self.campaign, processed=False, sent=False, skipped=False, failed=False
        ).filter(Q(sequence__contact__checkout__isnull=True) | Q(sequence__contact__checkout__user=self.request.user))

        contacts = models.Contact.objects.filter(
            membership__contact_group__id__in=list(
                self.campaign.contact_groups.all().distinct().values_list("id", flat=True)
            ),
            sequence__messages__isnull=True,
            engaged=False,
            blocked=False,
        )

        message = messages.first()
        if not message:
            contact = contacts.first()
            if contact:
                sequence, created = models.CampaignSequence.objects.get_or_create(
                    campaign=self.campaign, contact=contact
                )
                message = create_message(sequence)

        if message:
            checkout, created = models.ContactCheckout.objects.get_or_create(
                contact=message.sequence.contact, user=self.request.user
            )
            if created:
                checkout.time = timezone.now()
                checkout.save()

        context["message"] = message
        context["message_count"] = messages.count() if message else 0
        context["message_count"] += contacts.count() if contacts else 0

        context["sequence"] = message.sequence if message else None
        context["campaign"] = message.sequence.campaign if message else None
        context["organization"] = message.sequence.contact.organization if message else None
        context["contact"] = message.sequence.contact if message else None
        context["contact_departments"] = (
            json.loads(message.sequence.contact.departments.replace("'", '"')) if message else []
        )

        email_template = message.sequence.campaign.emails.first() if message else None

        if message:
            message_context = Context(
                {
                    "user": self.request.user,
                    "organization": message.sequence.contact.organization.export(),
                    "contact": message.sequence.contact.export(),
                }
            )
            subject_template = Template(email_template.subject_template.strip())
            body_template = Template(email_template.body_template.strip())

            context["subject"] = " ".join(subject_template.render(message_context).splitlines()).strip()
            context["body"] = body_template.render(message_context).strip()
        else:
            context["subject"] = ""
            context["body"] = ""

        return context

    def dispatch(self, request, *args, **kwargs):
        self.campaign = get_object_or_404(models.Campaign, id=self.kwargs["pk"])

        if request.user != self.campaign.owner:
            return redirect("outreach:campaign_list")

        return super().dispatch(request, *args, **kwargs)
