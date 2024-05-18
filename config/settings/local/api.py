from .base import *  # noqa

# URLS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#root-urlconf
ROOT_URLCONF = "config.api_urls"

# django-cors-headers - https://github.com/adamchainz/django-cors-headers#setup
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

X_FRAME_OPTIONS = "ALLOWALL"

# https://docs.djangoproject.com/en/dev/ref/settings/#secure-cross-origin-opener-policy
SECURE_CROSS_ORIGIN_OPENER_POLICY = "unsafe-none"
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-referrer-policy
SECURE_REFERRER_POLICY = "no-referrer"
