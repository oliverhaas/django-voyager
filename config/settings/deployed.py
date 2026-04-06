import os

from .base import *

DEBUG = False

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "local-deployed-testing-key-not-for-production")

# Security (relaxed for local testing, strict in real deployment)
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
_local_deploy = bool(os.environ.get("LOCAL_DEPLOY"))
SESSION_COOKIE_SECURE = not _local_deploy
CSRF_COOKIE_SECURE = not _local_deploy
SECURE_SSL_REDIRECT = not _local_deploy
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
