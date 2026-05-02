import os

from .settings import *  # noqa: F403
from .settings import BASE_DIR, MIDDLEWARE

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# Use a memory backend for email in tests
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
DEFAULT_FROM_EMAIL = "test@example.com"
ADMIN_EMAIL = "admin@example.com"
ENABLE_CHROMA_SYNC = False


# Optionally disable caching middleware for tests
MIDDLEWARE = [
    mw
    for mw in MIDDLEWARE
    if mw
    not in [
        "django.middleware.cache.UpdateCacheMiddleware",
        "django.middleware.cache.FetchFromCacheMiddleware",
    ]
]

if os.environ.get("POSTGRES_DB") and os.environ.get("POSTGRES_USER") and os.environ.get("POSTGRES_PASSWORD"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ["POSTGRES_DB"],
            "USER": os.environ["POSTGRES_USER"],
            "PASSWORD": os.environ["POSTGRES_PASSWORD"],
            "HOST": os.environ.get("POSTGRES_HOST", "localhost"),
            "PORT": os.environ.get("POSTGRES_PORT", "5432"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.path.join(BASE_DIR, "test_db.sqlite3"),
        }
    }
