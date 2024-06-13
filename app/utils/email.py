from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template import Context, Template


class Email:
    def __init__(self, subject_template, body_template, headers=None, tags=None):
        self.subject_template = subject_template
        self.body_template = body_template

        self.headers = headers
        self.tags = tags or []

    def send(self, _email, from_email=None, **context):
        msg = self.render(
            _email,
            from_email=from_email,
            base_ui_url=settings.BASE_UI_URL,
            base_api_url=settings.BASE_API_URL,
            email=_email,
            current_site=get_current_site(None),
            **context,
        )
        msg.send()

    def render(self, _email, from_email=None, **context):
        subject_template = Template(self.subject_template)
        body_template = Template(self.body_template)
        context = Context(context)

        if not from_email:
            from_email = settings.DEFAULT_FROM_EMAIL

        msg = EmailMessage(
            " ".join(subject_template.render(context).splitlines()).strip(),
            body_template.render(context).strip(),
            from_email,
            [_email],
            headers=self.headers,
        )
        msg.tags = self.tags
        return msg
