from django.contrib import admin

from . import models


class TeamDocumentInline(admin.TabularInline):
    model = models.TeamDocument
    extra = 1


@admin.register(models.TeamDocumentCollection)
class TeamDocumentCollectionAdmin(admin.ModelAdmin):
    inlines = [TeamDocumentInline]
