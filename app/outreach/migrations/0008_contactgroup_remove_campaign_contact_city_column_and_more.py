# Generated by Django 4.2.13 on 2024-06-04 07:12

import app.outreach.models
from django.db import migrations, models
import django.db.models.deletion
import private_storage.fields
import private_storage.storage.files
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("outreach", "0007_campaign_contacts"),
    ]

    operations = [
        migrations.CreateModel(
            name="ContactGroup",
            fields=[
                ("created", models.DateTimeField(editable=False)),
                ("updated", models.DateTimeField(editable=False)),
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid1, editable=False, primary_key=True, serialize=False, unique=True
                    ),
                ),
                ("name", models.CharField(max_length=512, verbose_name="Campaign Name")),
                (
                    "csv_file",
                    private_storage.fields.PrivateFileField(
                        storage=private_storage.storage.files.PrivateFileSystemStorage(),
                        upload_to=app.outreach.models.campaign_file_path,
                    ),
                ),
                (
                    "organization_name_column",
                    models.CharField(
                        default="Company Name for Emails",
                        max_length=256,
                        verbose_name="Organization Name Column (Required)",
                    ),
                ),
                (
                    "organization_link_column",
                    models.CharField(
                        default="Website", max_length=256, verbose_name="Organization URL Column (Required)"
                    ),
                ),
                (
                    "organization_employees_column",
                    models.CharField(
                        default="# Employees", max_length=256, verbose_name="Organization Employees Column"
                    ),
                ),
                (
                    "organization_industry_column",
                    models.CharField(default="Industry", max_length=256, verbose_name="Organization Industry Column"),
                ),
                (
                    "organization_keywords_column",
                    models.CharField(default="Keywords", max_length=256, verbose_name="Organization Keywords Column"),
                ),
                (
                    "organization_linkedin_column",
                    models.CharField(
                        default="Company Linkedin Url", max_length=256, verbose_name="Organization LinkedIn Column"
                    ),
                ),
                (
                    "organization_description_column",
                    models.CharField(
                        default="SEO Description", max_length=256, verbose_name="Organization Description Column"
                    ),
                ),
                (
                    "organization_technologies_column",
                    models.CharField(
                        default="Technologies", max_length=256, verbose_name="Organization Technologies Column"
                    ),
                ),
                (
                    "organization_revenue_column",
                    models.CharField(
                        default="Annual Revenue", max_length=256, verbose_name="Organization Revenue Column"
                    ),
                ),
                (
                    "organization_total_funding_column",
                    models.CharField(
                        default="Total Funding", max_length=256, verbose_name="Organization Total Funding Column"
                    ),
                ),
                (
                    "organization_last_funding_stage_column",
                    models.CharField(
                        default="Latest Funding",
                        max_length=256,
                        verbose_name="Organization Latest Funding Stage Column",
                    ),
                ),
                (
                    "organization_last_funding_column",
                    models.CharField(
                        default="Latest Funding Amount",
                        max_length=256,
                        verbose_name="Organization Latest Funding Amount Column",
                    ),
                ),
                (
                    "organization_last_raised_at_column",
                    models.CharField(
                        default="Last Raised At", max_length=256, verbose_name="Organization Last Raised At Column"
                    ),
                ),
                (
                    "contact_first_name_column",
                    models.CharField(
                        default="First Name", max_length=256, verbose_name="Contact First Name Column (Required)"
                    ),
                ),
                (
                    "contact_last_name_column",
                    models.CharField(
                        default="Last Name", max_length=256, verbose_name="Contact Last Name Column (Required)"
                    ),
                ),
                (
                    "contact_title_column",
                    models.CharField(default="Title", max_length=256, verbose_name="Contact Title Column (Required)"),
                ),
                (
                    "contact_departments_column",
                    models.CharField(default="Departments", max_length=256, verbose_name="Contact Departments Column"),
                ),
                (
                    "contact_seniority_column",
                    models.CharField(default="Seniority", max_length=256, verbose_name="Contact Seniority Column"),
                ),
                (
                    "contact_email_column",
                    models.CharField(default="Email", max_length=256, verbose_name="Contact Email Column (Required)"),
                ),
                (
                    "contact_phone_column",
                    models.CharField(default="First Phone", max_length=256, verbose_name="Contact Phone Column"),
                ),
                (
                    "contact_city_column",
                    models.CharField(default="City", max_length=256, verbose_name="Contact City Column"),
                ),
                (
                    "contact_province_column",
                    models.CharField(default="State", max_length=256, verbose_name="Contact Province Column"),
                ),
                (
                    "contact_country_column",
                    models.CharField(default="Country", max_length=256, verbose_name="Contact Country Column"),
                ),
                (
                    "contact_linkedin_column",
                    models.CharField(
                        default="Person Linkedin Url", max_length=256, verbose_name="Contact LinkedIn Column"
                    ),
                ),
            ],
            options={
                "ordering": ["-created"],
                "abstract": False,
            },
        ),
        migrations.RemoveField(
            model_name="campaign",
            name="contact_city_column",
        ),
        migrations.RemoveField(
            model_name="campaign",
            name="contact_country_column",
        ),
        migrations.RemoveField(
            model_name="campaign",
            name="contact_departments_column",
        ),
        migrations.RemoveField(
            model_name="campaign",
            name="contact_email_column",
        ),
        migrations.RemoveField(
            model_name="campaign",
            name="contact_first_name_column",
        ),
        migrations.RemoveField(
            model_name="campaign",
            name="contact_last_name_column",
        ),
        migrations.RemoveField(
            model_name="campaign",
            name="contact_linkedin_column",
        ),
        migrations.RemoveField(
            model_name="campaign",
            name="contact_phone_column",
        ),
        migrations.RemoveField(
            model_name="campaign",
            name="contact_province_column",
        ),
        migrations.RemoveField(
            model_name="campaign",
            name="contact_seniority_column",
        ),
        migrations.RemoveField(
            model_name="campaign",
            name="contact_title_column",
        ),
        migrations.RemoveField(
            model_name="campaign",
            name="contacts",
        ),
        migrations.RemoveField(
            model_name="campaign",
            name="csv_file",
        ),
        migrations.RemoveField(
            model_name="campaign",
            name="organization_description_column",
        ),
        migrations.RemoveField(
            model_name="campaign",
            name="organization_employees_column",
        ),
        migrations.RemoveField(
            model_name="campaign",
            name="organization_industry_column",
        ),
        migrations.RemoveField(
            model_name="campaign",
            name="organization_keywords_column",
        ),
        migrations.RemoveField(
            model_name="campaign",
            name="organization_last_funding_column",
        ),
        migrations.RemoveField(
            model_name="campaign",
            name="organization_last_funding_stage_column",
        ),
        migrations.RemoveField(
            model_name="campaign",
            name="organization_last_raised_at_column",
        ),
        migrations.RemoveField(
            model_name="campaign",
            name="organization_link_column",
        ),
        migrations.RemoveField(
            model_name="campaign",
            name="organization_linkedin_column",
        ),
        migrations.RemoveField(
            model_name="campaign",
            name="organization_name_column",
        ),
        migrations.RemoveField(
            model_name="campaign",
            name="organization_revenue_column",
        ),
        migrations.RemoveField(
            model_name="campaign",
            name="organization_technologies_column",
        ),
        migrations.RemoveField(
            model_name="campaign",
            name="organization_total_funding_column",
        ),
        migrations.AddField(
            model_name="contact",
            name="contact_group",
            field=models.ForeignKey(
                default="",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="contacts",
                to="outreach.contactgroup",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="organization",
            name="contact_group",
            field=models.ForeignKey(
                default="",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="organizations",
                to="outreach.contactgroup",
            ),
            preserve_default=False,
        ),
    ]