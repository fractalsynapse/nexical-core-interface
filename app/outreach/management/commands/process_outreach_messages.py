from django.core.management.base import BaseCommand

from app.outreach import messages


class Command(BaseCommand):
    help = "Processes campaign messages"

    def handle(self, *args, **options):
        messages.process_messages()
        self.stdout.write(self.style.SUCCESS("Successfully processed messages"))
