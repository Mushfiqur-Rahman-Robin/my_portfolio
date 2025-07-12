import os
from pathlib import Path

import dj_database_url
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config("SECRET_KEY")
DEBUG = config("DEBUG", default=False, cast=bool)

# Load the OpenAI API Key from the .env file
OPENAI_API_KEY = config("OPENAI_API_KEY", default="")

ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS",
    default="127.0.0.1,localhost,0.0.0.0",
    cast=lambda v: [s.strip() for s in v.split(",")],
)

CSRF_TRUSTED_ORIGINS = config(
    "CSRF_TRUSTED_ORIGINS",
    default="",
    cast=lambda v: [s.strip() for s in v.split(",")],
)

USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Your administrative email address to receive contact messages
ADMIN_EMAIL = config("ADMIN_EMAIL", default="your_admin_email@example.com")

if DEBUG:
    ALLOWED_HOSTS = ["*"]

# --- CKEDITOR CONFIGURATION ---
CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_CONFIGS = {
    "default": {
        "toolbar": "full",
        "height": 400,
        "width": "100%",
        # Add the 'codesnippet' plugin and its styles
        "extraPlugins": ",".join(["codesnippet"]),
        "codeSnippet_theme": "monokai_sublime",
    },
}

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "drf_spectacular",
    "api",
    "ckeditor",
    "ckeditor_uploader",
]

# CORRECT MIDDLEWARE ORDER FOR SITE-WIDE CACHING
MIDDLEWARE = [
    "django.middleware.cache.UpdateCacheMiddleware",  # MUST BE FIRST
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.cache.FetchFromCacheMiddleware",  # MUST BE LAST
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    # Global Rate Limiting Configuration (as a baseline for all APIs)
    # These will apply to all views unless explicitly overridden or an Anon/User throttle is replaced
    "DEFAULT_THROTTLE_CLASSES": [
        "api.throttles.CustomAnonRateThrottle",
        "api.throttles.CustomUserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "60/minute",  # General rate for anonymous users across all APIs
        "user": "1000/hour",  # General rate for authenticated users across all APIs
        "contact_form": "5/day",  # Specific rate for contact form submissions (anonymous users)
        "visitor_count": "1/second",  # Specific rate for visitor count endpoint
        "chatbot": "30/day",  # Specific rate for chatbot queries
    },
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Portfolio API",
    "DESCRIPTION": "API for managing portfolio projects, publications, certifications, and achievements",
    "VERSION": "1.0.0",
}

ROOT_URLCONF = "core.urls"
WSGI_APPLICATION = "core.wsgi.application"

DATABASES = {"default": dj_database_url.config(default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}")}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CORS_ALLOWED_ORIGINS = config(
    "CORS_ALLOWED_ORIGINS",
    default="http://localhost:5173,http://127.0.0.1:5173",
    cast=lambda v: [s.strip() for s in v.split(",")],
)

# CACHE configuration for Redis
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": config("REDIS_URL", default="redis://127.0.0.1:6379/1"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
        "KEY_PREFIX": "portfolio_cache",
        "TIMEOUT": 60 * 5,  # 5 minutes default timeout
    }
}

# This setting is required for the caching middleware to work
CACHE_MIDDLEWARE_SECONDS = 60 * 5  # Cache for 5 minutes (300 seconds)

# Email Backend Configuration (for sending contact form notifications)
# For development, you might use 'console.EmailBackend' or 'filebased.EmailBackend'
# For production, use 'django.core.mail.backends.smtp.EmailBackend' with proper settings
EMAIL_BACKEND = config("EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend")
EMAIL_HOST = config("EMAIL_HOST", default="smtp.example.com")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="noreply@yourdomain.com")

# LOGGING configuration for CRITICAL level only and a specific email logger
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": "CRITICAL",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "file": {
            "level": "CRITICAL",
            "class": "logging.FileHandler",
            "filename": os.path.join(BASE_DIR, "logs/critical_errors.log"),
            "formatter": "verbose",
        },
        "email_file": {  # Specific handler for email sending logs
            "level": "ERROR",  # Log email sending errors
            "class": "logging.FileHandler",
            "filename": os.path.join(BASE_DIR, "logs/email_errors.log"),
            "formatter": "verbose",
        },
        "null": {
            "class": "logging.NullHandler",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file"],
            "level": "CRITICAL",
            "propagate": False,
        },
        "api": {
            "handlers": ["console", "file"],
            "level": "CRITICAL",
            "propagate": False,
        },
        "email_sending": {  # New logger specifically for email sending
            "handlers": ["console", "email_file"],
            "level": "INFO",  # Log INFO for successful sends, ERROR for failures
            "propagate": False,
        },
        "": {  # Root logger - catches anything not handled by specific loggers
            "handlers": ["console", "file"],
            "level": "CRITICAL",
            "propagate": False,
        },
    },
}
