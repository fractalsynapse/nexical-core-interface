from django.contrib import admin

from . import models


@admin.register(models.ContactGroup)
class ContactGroupAdmin(admin.ModelAdmin):
    pass


class CampaignEmailInline(admin.TabularInline):
    model = models.CampaignEmail
    extra = 1


@admin.register(models.Campaign)
class CampaignAdmin(admin.ModelAdmin):
    inlines = [CampaignEmailInline]


@admin.register(models.Message)
class MessageAdmin(admin.ModelAdmin):
    pass


@admin.register(models.MessageEvent)
class MessageEventAdmin(admin.ModelAdmin):
    pass
