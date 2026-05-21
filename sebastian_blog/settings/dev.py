from .base import *
DEBUG = True
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

CSRF_TRUSTED_ORIGINS = [
            "https://sebastian-christoph.de",
                "https://www.sebastian-christoph.de",
                ]

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
