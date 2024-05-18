from allauth.account import app_settings
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string
from django.utils.encoding import force_str


class Notification:
    def __init__(self, emails, headers=None, tags=None):
        self.emails = emails
        self.headers = headers
        self.tags = tags or []

    def send(self, template_prefix, **context):
        current_site = get_current_site(None)

        for email in self.emails:
            msg = self._render_mail(
                template_prefix,
                email,
                {
                    "base_ui_url": settings.BASE_UI_URL,
                    "base_api_url": settings.BASE_API_URL,
                    "email": email,
                    "current_site": current_site,
                    **context,
                },
            )
            msg.send()

    def _format_email_subject(self, subject):
        prefix = settings.EMAIL_SUBJECT_PREFIX
        if prefix is None:
            site = get_current_site(None)
            prefix = f"[{site.name}] "
        return prefix + force_str(subject)

    def _get_from_email(self):
        return settings.DEFAULT_FROM_EMAIL

    def _render_mail(self, template_prefix, email, context):
        to = [email] if isinstance(email, str) else email
        subject = render_to_string(f"{template_prefix}_subject.txt", context)
        subject = " ".join(subject.splitlines()).strip()
        subject = self._format_email_subject(subject)

        from_email = self._get_from_email()

        bodies = {}
        html_ext = app_settings.TEMPLATE_EXTENSION
        for ext in [html_ext, "txt"]:
            try:
                template_name = f"{template_prefix}_message.{ext}"
                bodies[ext] = render_to_string(template_name, context).strip()
            except TemplateDoesNotExist:
                if ext == "txt" and not bodies:
                    raise
        if "txt" in bodies:
            msg = EmailMultiAlternatives(subject, bodies["txt"], from_email, to, headers=self.headers)
            if html_ext in bodies:
                msg.attach_alternative(bodies[html_ext], "text/html")
        else:
            msg = EmailMessage(subject, bodies[html_ext], from_email, to, headers=self.headers)
            msg.content_subtype = "html"

        msg.tags = self.tags
        return msg
