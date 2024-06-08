import random
import string

from allauth.account.models import EmailAddress
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from timezone_field import TimeZoneField

from app.users.managers import UserManager
from app.utils import fields
from app.utils.models import BaseUUIDModel, BaseUUIDModelMixin


def get_user_by_email(email):
    user = User.objects.filter(email=email)
    return user[0] if user else None


def check_verified_email(email):
    addresses = EmailAddress.objects.filter(email=email, verified=True)
    return addresses[0].user if addresses else None


def generate_random_code():
    code = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    try:
        UserInvite.objects.get(code=code)
    except UserInvite.DoesNotExist:
        pass
    return code


class User(BaseUUIDModelMixin, AbstractUser):
    username = None  # type: ignore
    email = models.EmailField(_("Email Address"), unique=True)
    timezone = TimeZoneField(_("Timezone"), choices_display="WITH_GMT_OFFSET", default="US/Eastern")

    first_name = models.CharField(_("First Name"), blank=False, max_length=255)
    last_name = models.CharField(_("Last Name"), blank=False, max_length=255)

    settings = fields.DictionaryField(_("User Settings"))

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = UserManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

    def check_member(self, *groups):
        return self.groups.filter(name__in=groups).exists()

    @property
    def emails(self):
        return list(EmailAddress.objects.filter(user=self).values_list("email", flat=True))

    @property
    def verified_emails(self):
        return list(EmailAddress.objects.filter(user=self, verified=True).values_list("email", flat=True))

    def export(self):
        return {
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "timezone": str(self.timezone),
        }


class UserInvite(BaseUUIDModel):
    email = models.EmailField(_("Email Address"), unique=True)
    code = models.CharField(_("Invite Code"), blank=True, editable=False, default=generate_random_code)

    def __str__(self):
        return f"{self.email} [ {self.code} ]"
