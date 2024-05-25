from .base import *  # noqa
from .base import env

# URLS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#root-urlconf
ROOT_URLCONF = "config.ui_urls"

# MIDDLEWARE
# ------------------------------------------------------------------------------
# https://django-debug-toolbar.readthedocs.io/en/latest/installation.html#middleware
MIDDLEWARE += ["app.global.middleware.user_timezone.TimezoneMiddleware"]  # noqa: F405

# ADMIN
# ------------------------------------------------------------------------------
# Django Admin path regex.
ADMIN_PATH = env("DJANGO_ADMIN_PATH")

# SECURITY
# ------------------------------------------------------------------------------
# django-cors-headers - https://github.com/adamchainz/django-cors-headers#setup
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "https://nexical.ai",
    "https://core.nexical.ai",
    "https://api.core.nexical.ai",
    "https://www.googletagmanager.com",
    "https://salesiq.zohopublic.com",
]
