from django.utils import timezone

from app.utils.email import Email

from . import models


def process_messages():
    current_time = timezone.now()
    for sequence in models.CampaignSequence.objects.filter(contact__blocked=False, contact__engaged=False):
        email = sequence.campaign.get_next_email(sequence)
        if email and (
            not sequence.last_contact_time or email.wait_days > (current_time - sequence.last_contact_time).days
        ):
            create_message(sequence)


def create_message(sequence):
    email = sequence.campaign.get_email(sequence)
    message = None
    if email:
        message = models.Message.objects.create(sequence=sequence, email_index=sequence.email_index)
    return message


def send_messages():
    for message in models.Message.objects.filter(processed=True, sent=False, skipped=False):
        try:
            email = Email(message.subject, message.body, tags=["outreach", message.sender.email])
            email.send(message.sequence.contact.email, message.sender.email)
            message.sent = True

        except Exception as e:
            message.error = str(e)
            message.failed = True

        message.save()
