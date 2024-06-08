import datetime

from django.utils import timezone

from . import models


def clean_checkouts():
    cutoff_time = timezone.now() - datetime.timedelta(hours=24)
    for checkout in models.ContactCheckout.objects.all():
        if checkout.time and checkout.time < cutoff_time:
            checkout.delete()
