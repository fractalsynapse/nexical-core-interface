import hashlib
import hmac
import json

import requests
from django.conf import settings


class MailgunError(Exception):
    pass


def verify(token, timestamp, signature):
    hmac_digest = hmac.new(
        key=settings.MAILGUN_WEBHOOK_KEY.encode(), msg=(f"{timestamp}{token}").encode(), digestmod=hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(str(signature), str(hmac_digest))


def get_event(mailgun_response):
    response_data = json.loads(mailgun_response)
    verification = response_data.get("signature", {})

    event_token = verification.get("token", None)
    timestamp = verification.get("timestamp", None)
    signature = verification.get("signature", None)

    if not (event_token and timestamp and signature):
        raise MailgunError("Missing event token, timestamp, and signature from Mailgun")

    if not verify(event_token, timestamp, signature):
        raise MailgunError("Verification of signature from Mailgun failed")

    event_data = response_data.get("event-data", None)
    if not event_data:
        raise MailgunError("Missing Mailgun event data")

    return event_data


class Mailgun:
    def __init__(self):
        self.auth = ("api", settings.MAILGUN_API_KEY)
        self.base_url = f"{settings.MAILGUN_API_URL}/{settings.MAILGUN_DOMAIN}"

    def _post(self, path, data, files=None):
        return requests.post(f"{self.base_url}/{path}", auth=self.auth, data=data, files=files)

    def _get(self, path, params=None):
        return requests.get(f"{self.base_url}/{path}", auth=self.auth, params=params)

    def send(
        self,
        from_email,
        to_email,
        subject,
        text=None,
        html=None,
        cc_emails=None,
        bcc_emails=None,
        reply_to_email=None,
        headers=None,
        inlines=None,
        attachments=None,
        campaign_id=None,
        tags=None,
    ):
        files = []
        data = {
            "from": from_email,
            "to": to_email,
            "cc": cc_emails or [],
            "bcc": bcc_emails or [],
            "subject": subject or "",
            "text": text or "",
            "html": html or "",
        }
        if headers:
            for key, value in headers.items():
                data[f"h:{key}"] = value

        if reply_to_email:
            data["h:Reply-To"] = reply_to_email

        if campaign_id:
            data["o:campaign"] = campaign_id
        if tags:
            data["o:tag"] = tags

        if inlines:
            for filename in inlines:
                files.append(("inline", open(filename)))

        if attachments:
            for filename, content_type, content in attachments:
                files.append(("attachment", (filename, content, content_type)))

        response = self._post("messages", data, files=files)
        return True if response.status_code == 200 else False
