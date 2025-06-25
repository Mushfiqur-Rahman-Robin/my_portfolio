from .settings import MIDDLEWARE

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

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
