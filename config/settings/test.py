from .base import *

# Faster password hashing for tests
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Use locmem cache in tests (no Valkey dependency)
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    },
}

# Disable cachalot in tests to avoid cache interference
CACHALOT_ENABLED = False
