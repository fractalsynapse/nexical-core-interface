# Generated by Django 4.2.5 on 2024-05-22 07:49

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("research", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="projectsummary",
            name="format",
        ),
        migrations.RemoveField(
            model_name="projectsummary",
            name="persona",
        ),
        migrations.RemoveField(
            model_name="projectsummary",
            name="repetition_penalty",
        ),
        migrations.RemoveField(
            model_name="projectsummary",
            name="temperature",
        ),
        migrations.RemoveField(
            model_name="projectsummary",
            name="top_p",
        ),
    ]
