import os

from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from rest_framework.authtoken.models import Token

from app.users.models import User


class Command(BaseCommand):
    help = "Initialize administrative superusers"

    def handle(self, *args, **options):
        for user in User.objects.filter(is_superuser=True, is_active=True):
            user.groups.add(Group.objects.get(name="engine"))
            user.groups.add(Group.objects.get(name="team_member"))

            if os.environ.get("DJANGO_SUPERUSER_API_KEY", None) and not Token.objects.filter(user=user).exists():
                Token.objects.create(user=user, key=os.environ["DJANGO_SUPERUSER_API_KEY"])

        self.stdout.write(self.style.SUCCESS("Successfully initialized administrative superusers"))
