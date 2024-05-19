from django.contrib import admin

from . import models


@admin.register(models.TeamProject)
class TeamProjectAdmin(admin.ModelAdmin):
    pass
