from .base import *

DEBUG = True

ALLOWED_HOSTS = ["*"]

# Mailpit for local email testing
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "localhost"
EMAIL_PORT = 1025

# Disable cachalot locally to avoid stale cache issues during development
CACHALOT_ENABLED = False
