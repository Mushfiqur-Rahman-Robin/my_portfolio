import os

from .settings import *  # noqa: F403
from .settings import MIDDLEWARE

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# Use a memory backend for email in tests
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
DEFAULT_FROM_EMAIL = "test@example.com"
ADMIN_EMAIL = "admin@example.com"


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

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB", "${{ secrets.DB_TEST_NAME }}"),
        "USER": os.environ.get("POSTGRES_USER", "${{ secrets.DB_TEST_USER }}"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "${{ secrets.DB_TEST_PASSWORD }}"),
        "HOST": "localhost",
        "PORT": "5432",
    }
}
