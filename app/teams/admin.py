from django.contrib import admin

from . import models


@admin.register(models.Team)
class TeamAdmin(admin.ModelAdmin):
    pass


@admin.register(models.TeamMembership)
class TeamMembershipAdmin(admin.ModelAdmin):
    pass


@admin.register(models.TeamInvite)
class TeamInviteAdmin(admin.ModelAdmin):
    pass


@admin.register(models.TeamTag)
class TeamTagAdmin(admin.ModelAdmin):
    pass
