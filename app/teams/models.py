from allauth.account.adapter import get_adapter
from allauth.utils import build_absolute_uri
from django.contrib.sites.shortcuts import get_current_site
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from app.events.models import Event
from app.users.models import User
from app.utils import fields
from app.utils.models import BaseUUIDModel


class TeamAccessError(Exception):
    pass


def get_active_team(user, id_only=False):
    try:
        team_id = user.settings.get("active_team", None)
        if team_id:
            return Team.objects.get(id=team_id) if not id_only else team_id
    except Team.DoesNotExist:
        pass
    return None


def get_active_team_membership(user):
    team = get_active_team(user)
    return user.membership.get(team__id=team.id)


def get_team_settings(user):
    membership = get_active_team_membership(user)
    return membership.settings


def update_team_settings(user, **settings):
    membership = get_active_team_membership(user)
    for key, value in settings.items():
        membership.settings[key] = value
    membership.save()


def set_active_team(user, team_id):
    user.settings["active_team"] = str(team_id)
    user.save()


def clear_active_team(user):
    user.settings.pop("active_team")
    user.save()


def get_team_instance(
    team,
    model_class,
    instance_id,
    team_field="team",
    id_field="id",
    share_model_class=None,
    share_model_team_field="team_id",
):
    if not team:
        raise TeamAccessError("Team not found")
    if not share_model_class:
        share_model_class = model_class
    try:
        access_teams = list(
            share_model_class.objects.filter(access_teams__id=team.id)
            .distinct()
            .values_list(share_model_team_field, flat=True)
        )

        return model_class.objects.get(**{f"{team_field}__in": [team] + access_teams, id_field: instance_id})
    except model_class.DoesNotExist:
        raise TeamAccessError("Team instance not found")


def team_file_access(private_file):
    from app.documents.models import TeamDocumentCollection

    user = private_file.request.user
    if user.is_authenticated:
        try:
            name_components = private_file.relative_name.split("/")
            # instance_type = name_components[1]
            instance_id = name_components[2]
        except Exception:
            return False

        team = get_active_team(user)
        if not team:
            return False
        try:
            get_team_instance(team, TeamDocumentCollection, instance_id)
            return True
        except TeamAccessError:
            pass

    return False


class Team(BaseUUIDModel):
    name = models.CharField(_("Team Name"), blank=False, max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ownership")

    def __str__(self):
        return f"{self.name} <{self.owner.email}>"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.owner:
            (membership, created) = TeamMembership.objects.get_or_create(user=self.owner, team=self)
            self.members.add(membership)

    def create_event(self, operation="update"):
        Event.objects.create(
            type="team",
            data={
                "operation": operation,
                "id": str(self.id),
                "name": self.name,
                "owner": str(self.owner.id),
            },
        )


@receiver(post_delete, sender=Team)
def delete_team_hook(sender, instance, using, **kwargs):
    instance.create_event("delete")


class TeamMembership(BaseUUIDModel):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="members")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="membership")
    settings = fields.DictionaryField(_("User Settings"))

    class Meta:
        unique_together = ["team", "user"]


class TeamInvite(BaseUUIDModel):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="invites")
    email = models.EmailField(max_length=255)

    class Meta:
        unique_together = ["team", "email"]

    def send(self, request):
        url = reverse("teams:invite_confirm", kwargs={"pk": self.id})
        get_adapter(request).send_mail(
            "account/email/team_invite",
            self.email,
            {
                "team": self.team,
                "email": self.email,
                "request": request,
                "user": request.user,
                "current_site": get_current_site(request),
                "activate_url": build_absolute_uri(request, url),
            },
        )


class TeamTag(BaseUUIDModel):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="tags")
    name = models.CharField(_("Team Tags"), blank=False, max_length=255)
