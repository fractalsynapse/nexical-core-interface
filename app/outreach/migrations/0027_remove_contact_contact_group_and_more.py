# Generated by Django 4.2.13 on 2024-06-05 14:00

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("outreach", "0026_alter_contactcheckout_time"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="contact",
            name="contact_group",
        ),
        migrations.RemoveField(
            model_name="organization",
            name="contact_group",
        ),
        migrations.CreateModel(
            name="ContactMembership",
            fields=[
                ("created", models.DateTimeField(editable=False)),
                ("updated", models.DateTimeField(editable=False)),
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid1, editable=False, primary_key=True, serialize=False, unique=True
                    ),
                ),
                (
                    "contact",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE, related_name="membership", to="outreach.contact"
                    ),
                ),
                (
                    "contact_group",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="members", to="outreach.contactgroup"
                    ),
                ),
            ],
            options={
                "ordering": ["-created"],
                "abstract": False,
            },
        ),
    ]