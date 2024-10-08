# Generated by Django 4.2.5 on 2024-05-22 07:49

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("projects", "0005_teamproject_documents_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="teamproject",
            name="repetition_penalty",
            field=models.FloatField(default=0.9, verbose_name="Summary Repetition Penalty"),
        ),
        migrations.AddField(
            model_name="teamproject",
            name="temperature",
            field=models.FloatField(default=0.1, verbose_name="Summary Temperature"),
        ),
        migrations.AddField(
            model_name="teamproject",
            name="top_p",
            field=models.FloatField(default=0.9, verbose_name="Summary Top-P"),
        ),
    ]
