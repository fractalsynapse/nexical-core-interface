from django.contrib import admin

from . import models


@admin.register(models.ProjectSummary)
class ProjectSummaryAdmin(admin.ModelAdmin):
    pass


@admin.register(models.ProjectNote)
class ProjectNoteAdmin(admin.ModelAdmin):
    pass
