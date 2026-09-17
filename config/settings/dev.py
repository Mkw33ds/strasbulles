from .base import *  # noqa: F403

DEBUG = True
EMAIL_BACKEND = env(  # noqa: F405
    "EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend"
)
