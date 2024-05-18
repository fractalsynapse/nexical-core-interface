from allauth.account.adapter import get_adapter
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.db import models
from django.utils.translation import gettext_lazy as _

from app.users.models import User
from app.utils.models import BaseUUIDModel


class ContactMessage(BaseUUIDModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="contacts", blank=True, null=True)

    name = models.CharField(_("Full Name"), blank=True, null=True, max_length=255)
    email = models.EmailField(_("Email Address"), blank=True, null=True)

    subject = models.CharField(_("Subject"), blank=False, max_length=255)
    message = models.TextField(_("Message"), blank=False)

    def __str__(self):
        return f"{self.name} ({self.email}): {self.subject}"

    def send(self, request):
        get_adapter(request).send_mail(
            "account/email/contact_notification",
            settings.CONTACT_NOTIFICATION_EMAIL,
            {
                "current_site": get_current_site(request),
                "user": request.user if request.user.is_authenticated else None,
                "name": self.name,
                "email": self.email,
                "subject": self.subject,
                "message": self.message,
                "created": self.created.strftime("%Y-%m-%d %H:%M:%S"),
            },
        )
