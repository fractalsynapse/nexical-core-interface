# Generated by Django 4.2.5 on 2024-05-21 03:42

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("projects", "0002_alter_teamproject_format_prompt_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="teamproject",
            name="summary_model",
            field=models.CharField(
                choices=[("mixtral-8x7b", "Mixtral 8x7b (Default)")],
                default="mixtral-8x7b",
                max_length=60,
                verbose_name="Summarization Model",
            ),
        ),
    ]
