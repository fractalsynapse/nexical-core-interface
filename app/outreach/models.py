import csv
import json
from datetime import datetime

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from private_storage.fields import PrivateFileField

from app.events.models import Event
from app.users.models import User
from app.utils import fields
from app.utils.models import BaseUUIDModel
from app.utils.python import get_identifier


def campaign_file_path(instance, filename):
    # file will be uploaded to PRIVATE_STORAGE_ROOT/uploads/campaign/<id>/<filename>
    return f"uploads/campaign/{instance.id}/{filename}"


class ContactGroup(BaseUUIDModel):
    name = models.CharField(_("Contact Group Name"), blank=False, max_length=512)
    description = models.TextField(_("Contact Group Description"), blank=True, default="")

    csv_file = PrivateFileField(
        upload_to=campaign_file_path,
        content_types=["text/csv"],
        max_file_size=settings.PRIVATE_STORAGE_MAX_FILE_SIZE,
    )

    organization_name_column = models.CharField(
        _("Organization Name Column (Required)"), default="Company Name for Emails", max_length=256
    )
    organization_link_column = models.CharField(
        _("Organization URL Column (Required)"), default="Website", max_length=256
    )
    organization_employees_column = models.CharField(
        _("Organization Employees Column"), default="# Employees", max_length=256
    )
    organization_industry_column = models.CharField(
        _("Organization Industry Column"), default="Industry", max_length=256
    )
    organization_keywords_column = models.CharField(
        _("Organization Keywords Column"), default="Keywords", max_length=256
    )
    organization_linkedin_column = models.CharField(
        _("Organization LinkedIn Column"), default="Company Linkedin Url", max_length=256
    )
    organization_description_column = models.CharField(
        _("Organization Description Column"), default="SEO Description", max_length=256
    )
    organization_technologies_column = models.CharField(
        _("Organization Technologies Column"), default="Technologies", max_length=256
    )
    organization_revenue_column = models.CharField(
        _("Organization Revenue Column"), default="Annual Revenue", max_length=256
    )
    organization_total_funding_column = models.CharField(
        _("Organization Total Funding Column"), default="Total Funding", max_length=256
    )
    organization_last_funding_stage_column = models.CharField(
        _("Organization Latest Funding Stage Column"), default="Latest Funding", max_length=256
    )
    organization_last_funding_column = models.CharField(
        _("Organization Latest Funding Amount Column"), default="Latest Funding Amount", max_length=256
    )
    organization_last_raised_at_column = models.CharField(
        _("Organization Last Raised At Column"), default="Last Raised At", max_length=256
    )

    contact_first_name_column = models.CharField(
        _("Contact First Name Column (Required)"), default="First Name", max_length=256
    )
    contact_last_name_column = models.CharField(
        _("Contact Last Name Column (Required)"), default="Last Name", max_length=256
    )
    contact_title_column = models.CharField(_("Contact Title Column (Required)"), default="Title", max_length=256)
    contact_departments_column = models.CharField(
        _("Contact Departments Column"), default="Departments", max_length=256
    )
    contact_seniority_column = models.CharField(_("Contact Seniority Column"), default="Seniority", max_length=256)
    contact_email_column = models.CharField(_("Contact Email Column (Required)"), default="Email", max_length=256)
    contact_phone_column = models.CharField(_("Contact Phone Column"), default="First Phone", max_length=256)
    contact_city_column = models.CharField(_("Contact City Column"), default="City", max_length=256)
    contact_province_column = models.CharField(_("Contact Province Column"), default="State", max_length=256)
    contact_country_column = models.CharField(_("Contact Country Column"), default="Country", max_length=256)
    contact_linkedin_column = models.CharField(
        _("Contact LinkedIn Column"), default="Person Linkedin Url", max_length=256
    )

    def __str__(self):
        return f"{self.name}"

    def save(self, *args, **kwargs):
        try:
            existing = ContactGroup.objects.get(id=self.id)
            if existing.csv_file != self.csv_file:
                existing.csv_file.delete(save=False)
        except ContactGroup.DoesNotExist:
            pass

        super().save(*args, **kwargs)
        self._save_contacts()

    def _save_contacts(self):
        contact_data = ""
        handle = None

        try:
            handle = self.csv_file.file.open(mode="r")
            contact_data = handle.read().decode("utf-8")
        except Exception:
            pass
        finally:
            if handle:
                handle.close()

        if contact_data:
            contact_records = list(csv.reader(contact_data.strip().split("\n"), delimiter=","))
            columns = contact_records[0]

            for row in contact_records[1:]:
                field_map = {}
                for index, name in enumerate(columns):
                    field_map[name] = row[index]

                organization_link = field_map.get(self.organization_link_column, None)
                contact_email = field_map.get(self.contact_email_column, None)

                if organization_link and contact_email:
                    organization, created = Organization.objects.get_or_create(link=organization_link)
                    organization.name = field_map.get(self.organization_name_column, None)
                    organization.industry = field_map.get(self.organization_industry_column, None)
                    organization.keywords = [
                        keyword.strip() for keyword in field_map.get(self.organization_keywords_column, "").split(",")
                    ]
                    organization.linkedin = field_map.get(self.organization_linkedin_column, None)
                    organization.description = field_map.get(self.organization_description_column, None)
                    organization.technologies = [
                        technology.strip()
                        for technology in field_map.get(self.organization_technologies_column, "").split(",")
                    ]

                    employees = field_map.get(self.organization_employees_column, None)
                    if employees:
                        organization.employees = int(employees)

                    revenue = field_map.get(self.organization_revenue_column, None)
                    if revenue:
                        organization.revenue = float(revenue)

                    total_funding = field_map.get(self.organization_total_funding_column, None)
                    if total_funding:
                        organization.total_funding = float(total_funding)

                    last_funding = field_map.get(self.organization_last_funding_column, None)
                    if last_funding:
                        organization.last_funding = float(last_funding)

                    organization.last_funding_stage = field_map.get(self.organization_last_funding_stage_column, None)

                    last_raised_at = field_map.get(self.organization_last_raised_at_column, None)
                    if last_raised_at:
                        organization.last_raised_at = datetime.strptime(last_raised_at, "%Y-%m-%d").date()

                    organization.save()

                    contact, created = Contact.objects.get_or_create(organization=organization, email=contact_email)
                    contact.phone = field_map.get(self.contact_phone_column, None)
                    contact.first_name = field_map.get(self.contact_first_name_column, None)
                    contact.last_name = field_map.get(self.contact_last_name_column, None)
                    contact.title = field_map.get(self.contact_title_column, None)
                    contact.seniority = field_map.get(self.contact_seniority_column, None)
                    contact.departments = [
                        department.strip()
                        for department in field_map.get(self.contact_departments_column, "").split(",")
                    ]
                    contact.city = field_map.get(self.contact_city_column, None)
                    contact.province = field_map.get(self.contact_province_column, None)
                    contact.country = field_map.get(self.contact_country_column, None)
                    contact.linkedin = field_map.get(self.contact_linkedin_column, None)
                    contact.save()

                    ContactMembership.objects.get_or_create(contact_group=self, contact=contact)

    def delete(self, *args, **kwargs):
        self.csv_file.delete(save=False)
        super().delete(*args, **kwargs)

    def create_event(self, operation="update"):
        organizations = []
        contacts = []

        for contact in Contact.objects.filter(contact_group=self):
            organizations.append(contact.organization.export())
            contacts.append(contact.export())

        Event.objects.create(
            type="outreach_contact_group",
            data={
                "operation": operation,
                "id": str(self.id),
                "name": self.name,
                "description": self.description,
                "hash": get_identifier([str(contact["id"]) for contact in contacts]),
                "organizations": organizations,
                "contacts": contacts,
            },
        )


@receiver(post_delete, sender=ContactGroup)
def delete_contact_group_hook(sender, instance, using, **kwargs):
    instance.create_event("delete")


class Organization(BaseUUIDModel):
    link = models.URLField(_("Organization URL"), blank=False, max_length=1024, unique=True)
    name = models.CharField(_("Organization Name"), blank=False, max_length=512)
    linkedin = models.URLField(_("Organization LinkedIn"), blank=True, null=True, max_length=1024)

    description = models.CharField(_("Organization Description"), blank=False, max_length=512)
    technologies = fields.ListField(_("Organization Technologies"))

    employees = models.IntegerField(_("Organization Employees"), blank=True, null=True)
    industry = models.CharField(_("Organization Industry"), blank=True, null=True, max_length=512)
    keywords = fields.ListField(_("Organization Keywords"))

    revenue = models.FloatField(_("Organization Revenue"), blank=True, null=True)
    total_funding = models.FloatField(_("Organization Total Funding"), blank=True, null=True)
    last_funding_stage = models.CharField(
        _("Organization Latest Funding Stage"), blank=True, null=True, max_length=256
    )
    last_funding = models.FloatField(_("Organization Latest Funding Amount"), blank=True, null=True)
    last_raised_at = models.DateField(_("Organization Last Raised At"), blank=True, null=True)

    def __str__(self):
        return f"{self.name}: {self.link}"

    def export(self):
        contacts = []
        for contact in self.contacts.all():
            contacts.append(contact.export())

        return {
            "name": self.name,
            "link": self.link,
            "employees": self.employees,
            "industry": self.industry,
            "keywords": self.keywords,
            "linkedin": self.linkedin,
            "description": self.description,
            "technologies": self.technologies,
            "revenue": self.revenue,
            "total_funding": self.total_funding,
            "last_funding_stage": self.last_funding_stage,
            "last_funding": self.last_funding,
            "last_raised_at": self.last_raised_at.strftime("%Y-%m-%d") if self.last_raised_at else None,
            "contacts": contacts,
        }


class Contact(BaseUUIDModel):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="contacts")

    email = models.EmailField(_("Contact Email"), blank=False, max_length=512, unique=True)
    phone = models.CharField(_("Contact Phone"), blank=False, max_length=256)
    first_name = models.CharField(_("Contact First Name"), blank=False, max_length=256)
    last_name = models.CharField(_("Contact Last Name"), blank=False, max_length=256)

    seniority = models.CharField(_("Contact Seniority"), blank=False, max_length=256)
    title = models.CharField(_("Contact Title"), blank=False, max_length=512)
    departments = models.CharField(_("Contact Departments"), blank=False)

    city = models.CharField(_("Contact City"), blank=False, max_length=256)
    province = models.CharField(_("Contact Province"), blank=False, max_length=256)
    country = models.CharField(_("Contact Country"), blank=False, max_length=256)
    linkedin = models.URLField(_("Contact LinkedIn"), blank=False, max_length=1024)

    engaged = models.BooleanField(_("Contact Engaged"), default=False)
    blocked = models.BooleanField(_("Contact Blocked"), default=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

    def export(self):
        return {
            "organization": str(self.organization.id),
            "email": self.email,
            "phone": self.phone,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "seniority": self.seniority,
            "title": self.title,
            "departments": json.loads(self.departments.replace("'", '"')) if self.departments else [],
            "city": self.city,
            "province": self.province,
            "country": self.country,
            "linkedin": self.linkedin,
            "blocked": self.blocked,
        }


class ContactMembership(BaseUUIDModel):
    contact_group = models.ForeignKey(ContactGroup, on_delete=models.CASCADE, related_name="members")
    contact = models.OneToOneField(Contact, on_delete=models.CASCADE, related_name="membership")


class ContactCheckout(BaseUUIDModel):
    contact = models.OneToOneField(Contact, on_delete=models.CASCADE, related_name="checkout")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="contact_checkouts")
    time = models.DateTimeField(_("Contact Checkout Time"), blank=True, null=True)


class Campaign(BaseUUIDModel):
    name = models.CharField(_("Campaign Name"), blank=False, max_length=512)
    owner = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="campaigns")
    description = models.TextField(_("Campaign Description"), blank=True, default="")

    contact_groups = models.ManyToManyField(ContactGroup, related_name="campaigns", blank=False)

    def __str__(self):
        return f"{self.name}"

    def get_email(self, sequence):
        if sequence.email_index < self.emails.count():
            return self.emails.all()[sequence.email_index]
        return None

    def get_next_email(self, sequence):
        email_index = sequence.email_index + 1
        if email_index < self.emails.count():
            return self.emails.all()[email_index]
        return None

    def create_event(self, operation="update"):
        emails = []
        for email in self.emails.all():
            emails.append(
                {
                    "id": str(email.id),
                    "subject_template": email.subject_template,
                    "body_template": email.body_template,
                    "wait_days": email.wait_days,
                }
            )

        Event.objects.create(
            type="outreach_campaign",
            data={
                "operation": operation,
                "id": str(self.id),
                "name": self.name,
                "owner": str(self.owner.id),
                "description": self.description,
                "contact_groups": [str(id) for id in self.contact_groups.values_list("id", flat=True)],
                "emails": emails,
            },
        )


@receiver(post_delete, sender=Campaign)
def delete_campaign_hook(sender, instance, using, **kwargs):
    instance.create_event("delete")


class CampaignEmail(BaseUUIDModel):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name="emails")
    subject_template = models.CharField(_("Subject template"), blank=False, max_length=512)
    body_template = models.TextField(_("Body template"), blank=False)
    wait_days = models.IntegerField(
        _("Wait in days before sending (0 - 90)"), default=1, validators=[MinValueValidator(0), MaxValueValidator(90)]
    )


class CampaignSequence(BaseUUIDModel):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name="sequence")
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name="sequence")
    email_index = models.IntegerField(_("Email Index"), default=0)
    last_contact_time = models.DateTimeField(_("Last Contact Time"), blank=True, null=True)

    class Meta:
        unique_together = (
            "campaign",
            "contact",
        )


class Message(BaseUUIDModel):
    sequence = models.ForeignKey(CampaignSequence, on_delete=models.CASCADE, related_name="messages")
    email_index = models.IntegerField(_("Email Index"), default=0)

    sender = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="messages")
    subject = models.CharField(_("Email Subject"), blank=True, null=True, max_length=512)
    body = models.TextField(_("Email Body"), blank=True, null=True)

    processed = models.BooleanField(_("Message Processed"), default=False)
    sent = models.BooleanField(_("Message Sent"), default=False)
    skipped = models.BooleanField(_("Message Skipped"), default=False)
    failed = models.BooleanField(_("Message Failed"), default=False)
    error = models.CharField(_("Message Error"), blank=True, null=True, max_length=1024)

    def __str__(self):
        return f"{self.sequence.contact.first_name} {self.sequence.contact.last_name}: {self.sequence.contact.title}"


class MessageEvent(BaseUUIDModel):
    type = models.CharField(_("Event Type"), blank=False, max_length=100)
    email = models.CharField(_("Email"), blank=False, max_length=512)
    payload = fields.DictionaryField(_("Event Payload"))

    def create_event(self, operation="update"):
        Event.objects.create(
            type="outreach_message_event",
            data={
                "operation": operation,
                "id": str(self.id),
                "type": self.type,
                "email": self.email,
                "payload": self.payload,
            },
        )


@receiver(post_delete, sender=MessageEvent)
def delete_message_event_hook(sender, instance, using, **kwargs):
    instance.create_event("delete")
