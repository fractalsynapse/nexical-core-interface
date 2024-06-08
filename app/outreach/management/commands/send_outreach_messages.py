from django.core.management.base import BaseCommand

from app.outreach import messages


class Command(BaseCommand):
    help = "Sends queued campaign messages"

    def handle(self, *args, **options):
        messages.send_messages()
        self.stdout.write(self.style.SUCCESS("Successfully sent messages"))
