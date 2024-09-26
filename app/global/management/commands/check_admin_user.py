import sys

from django.core.management.base import BaseCommand

from app.users.models import User


class Command(BaseCommand):
    help = "Check existence of administrative superuser"

    def handle(self, *args, **options):
        users = User.objects.filter(is_superuser=True)
        if users:
            sys.exit()
        sys.exit(1)
