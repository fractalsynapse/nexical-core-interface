from django.db import models
from django.utils.translation import gettext_lazy as _

from app.users.models import User
from app.utils.models import BaseUUIDModel


class Feedback(BaseUUIDModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="feedback")
    path = models.CharField(_("Page Path"), blank=False, max_length=1024)
    rating = models.IntegerField(_("Feedback Rating"), blank=False)
    message = models.TextField(_("Feedback Message"), blank=False)

    def __str__(self):
        return f"[ {self.user__id} ]: {self.path}"
