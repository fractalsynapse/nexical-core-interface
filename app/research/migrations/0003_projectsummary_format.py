# Generated by Django 4.2.5 on 2024-05-23 06:26

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("research", "0002_remove_projectsummary_format_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="projectsummary",
            name="format",
            field=models.TextField(blank=True, verbose_name="Summary Format"),
        ),
    ]
