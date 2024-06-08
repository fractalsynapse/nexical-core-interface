from django.core.management.base import BaseCommand

from app.outreach import contacts


class Command(BaseCommand):
    help = "Cleaning expired contact checkouts"

    def handle(self, *args, **options):
        contacts.clean_checkouts()
        self.stdout.write(self.style.SUCCESS("Successfully cleaned expired checkouts"))
