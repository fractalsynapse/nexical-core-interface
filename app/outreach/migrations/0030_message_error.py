# Generated by Django 4.2.13 on 2024-06-07 23:08

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("outreach", "0029_contact_engaged"),
    ]

    operations = [
        migrations.AddField(
            model_name="message",
            name="error",
            field=models.CharField(blank=True, max_length=1024, null=True, verbose_name="Message Error"),
        ),
    ]