from django.db import models
from django.utils.translation import gettext_lazy as _

from app.utils import fields
from app.utils.models import BaseUUIDModel


class Event(BaseUUIDModel):
    type = models.CharField(_("Event Type"), blank=False, max_length=100)
    data = fields.DictionaryField(_("Event Data"))

    def __str__(self):
        return f"{self.id}: {self.type}"
