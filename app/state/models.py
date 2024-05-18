from django.db import models
from django.utils.translation import gettext_lazy as _

from app.utils import fields
from app.utils.models import BaseModel


class State(BaseModel):
    name = models.CharField(_("Name"), primary_key=True, max_length=255)
    value = fields.DictionaryField(_("Value"))

    def __str__(self):
        return self.name
