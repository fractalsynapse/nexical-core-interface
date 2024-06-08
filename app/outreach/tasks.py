from config import celery_app

from . import contacts, messages


@celery_app.task()
def process_messages():
    messages.process_messages()


@celery_app.task()
def send_messages():
    messages.send_messages()


@celery_app.task()
def clean_checkouts():
    contacts.clean_checkouts()
