"""Base settings for AgentSphere project.

This module contains the base Django settings that are shared across
all environments (development, testing, production).
"""

# Standard library imports
import logging
import ssl
from datetime import timedelta
from pathlib import Path
from typing import Any

# Third-party imports
import environ
import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.redis import RedisIntegration

# -----------------------------------------
# Path configuration
# -----------------------------------------

# Set the base directory for the project
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent

# Set the apps directory
APPS_DIR = BASE_DIR / "apps"

# Initialize environment variables
env = environ.Env()

# Read environment variables from .env file if specified
READ_DOT_ENV_FILE = env.bool("DJANGO_READ_DOT_ENV_FILE", default=False)
if READ_DOT_ENV_FILE:
    env.read_env(str(BASE_DIR / ".env"))

# -----------------------------------------
# Core Django settings
# -----------------------------------------

# Debug settings
DEBUG = env.bool("DJANGO_DEBUG", False)

# Secret key for cryptographic signing
SECRET_KEY = env.str("DJANGO_SECRET_KEY")

# Activation link settings
ACTIVATION_SCHEME = env.str("DJANGO_ACTIVATION_SCHEME", default="https")
ACTIVATION_DOMAIN = env.str(
    "DJANGO_ACTIVATION_DOMAIN",
    default="agentsphere.serveo.net",
)

# Allowed hosts for the application
ALLOWED_HOSTS = env.list(
    "DJANGO_ALLOWED_HOSTS",
    default=[
        "agentsphere.serveo.net",
    ],
)

# Allowed cors origins
CORS_ALLOWED_ORIGINS = env.list(
    "DJANGO_CORS_ALLOWED_ORIGINS",
    default=[
        "https://agentsphere.serveo.net",
    ],
)

# Internationalization settings
TIME_ZONE = "Asia/Kolkata"
LANGUAGE_CODE = "en-us"
SITE_ID = 1
USE_I18N = True
USE_TZ = True
LOCALE_PATHS = [str(BASE_DIR / "locale")]

# -----------------------------------------
# Database settings
# -----------------------------------------

# Database configuration
DATABASES: dict[str, dict[str, Any]] = {"default": env.db("DATABASE_URL")}
DATABASES["default"]["ATOMIC_REQUESTS"] = True
DATABASES["default"]["CONN_MAX_AGE"] = env.int("CONN_MAX_AGE", default=60)
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# -----------------------------------------
# URL configuration
# -----------------------------------------

# Root URL configuration
ROOT_URLCONF = "config.urls"

# WSGI application path
WSGI_APPLICATION = "config.wsgi.application"

# -----------------------------------------
# Application definition
# -----------------------------------------

# Django built-in applications
DJANGO_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.admin",
    "django.forms",
]

# Third-party applications
THIRD_PARTY_APPS = [
    "django_celery_beat",
    "rest_framework",
    "corsheaders",
    "drf_spectacular",
    "collectfasta",
    "django_filters",
    "silk",
    "djcelery_email",
    "django_extensions",
    "rest_framework_simplejwt",
    "health_check",
    "health_check.db",
    "health_check.cache",
    "health_check.storage",
    "health_check.contrib.migrations",
    "health_check.contrib.celery",
    "health_check.contrib.redis",
]

# Local applications
LOCAL_APPS = [
    "apps.common",
    "apps.users",
    "apps.organization",
    "apps.agents",
    "apps.tools",
]

# Combined applications list
INSTALLED_APPS = [*DJANGO_APPS, *THIRD_PARTY_APPS, *LOCAL_APPS]

# -----------------------------------------
# Health check settings
# -----------------------------------------

# Health check modules
HEALTH_CHECK = {
    "DISK_USAGE_MAX": 90,
    "MEMORY_MIN": 100,
}

# -----------------------------------------
# Migration settings
# -----------------------------------------

# Custom migration modules
MIGRATION_MODULES = {"sites": "apps.contrib.sites.migrations"}

# -----------------------------------------
# Authentication settings
# -----------------------------------------

# Authentication backends
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]

# User model and login settings
AUTH_USER_MODEL = "users.User"
LOGIN_REDIRECT_URL = "users:redirect"
LOGIN_URL = "account_login"

# -----------------------------------------
# Password settings
# -----------------------------------------

# Password hashers in order of preference
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
]

# Password validation rules
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# -----------------------------------------
# Middleware settings
# -----------------------------------------

# Middleware classes
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "silk.middleware.SilkyMiddleware",
]

# -----------------------------------------
# Static files settings
# -----------------------------------------

# Static files configuration
STATIC_ROOT = str(BASE_DIR / "staticfiles")
STATICFILES_DIRS = []

# Static file finders
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

# -----------------------------------------
# Template settings
# -----------------------------------------

# Template configuration
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [str(APPS_DIR / "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# Form renderer setting
FORM_RENDERER = "django.forms.renderers.TemplatesSetting"

# -----------------------------------------
# DiceBear Settings
# -----------------------------------------

# DiceBear service URL
DICEBEAR_SERVICE_URL = env.str("DICEBEAR_SERVICE_URL", default="http://localhost:3000")


# -----------------------------------------
# Fixture settings
# -----------------------------------------

# Fixture directories
FIXTURE_DIRS = (str(APPS_DIR / "fixtures"),)

# -----------------------------------------
# Security settings
# -----------------------------------------

# Cookie security settings
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = False
X_FRAME_OPTIONS = "DENY"

# CSRF settings
CSRF_TRUSTED_ORIGINS = env.list(
    "DJANGO_CSRF_TRUSTED_ORIGINS",
    default=[
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ],
)

# CSRF and Session cookie settings
CSRF_COOKIE_SECURE = env.bool("DJANGO_CSRF_COOKIE_SECURE", default=False)
SESSION_COOKIE_SECURE = env.bool("DJANGO_SESSION_COOKIE_SECURE", default=False)
CSRF_COOKIE_SAMESITE = env.str("DJANGO_CSRF_COOKIE_SAMESITE", default="Lax")
SESSION_COOKIE_SAMESITE = env.str("DJANGO_SESSION_COOKIE_SAMESITE", default="Lax")
CSRF_COOKIE_DOMAIN = env.str("DJANGO_CSRF_COOKIE_DOMAIN", default=None)
CSRF_USE_SESSIONS = False
CSRF_COOKIE_PATH = "/"
CSRF_COOKIE_NAME = "csrftoken"
SESSION_COOKIE_NAME = "sessionid"

# SSL and HTTPS settings
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True
SECURE_SSL_REDIRECT = env.bool("DJANGO_SECURE_SSL_REDIRECT", default=True)

# HTTP Strict Transport Security settings
SECURE_HSTS_SECONDS = 60
SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool(
    "DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS",
    default=True,
)
SECURE_HSTS_PRELOAD = env.bool("DJANGO_SECURE_HSTS_PRELOAD", default=True)
SECURE_CONTENT_TYPE_NOSNIFF = env.bool(
    "DJANGO_SECURE_CONTENT_TYPE_NOSNIFF",
    default=True,
)

# -----------------------------------------
# Admin settings
# -----------------------------------------

# Admin URL and user settings
ADMIN_URL = env.str("DJANGO_ADMIN_URL")
ADMINS = [("""Rohit Vilas Ingole""", "datarohit@outlook.com")]
MANAGERS = ADMINS

# -----------------------------------------
# Email settings
# -----------------------------------------

# Email backend configuration
EMAIL_BACKEND = "djcelery_email.backends.CeleryEmailBackend"
EMAIL_HOST = env.str("EMAIL_HOST", default="smtp-mail.outlook.com")
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)
EMAIL_HOST_USER = env.str("EMAIL_HOST_USER", default="datarohit@outlook.com")
EMAIL_HOST_PASSWORD = env.str("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = env.str(
    "DEFAULT_FROM_EMAIL",
    default="AgentSphere <datarohit@outlook.com>",
)
SERVER_EMAIL = env.str("SERVER_EMAIL", default="datarohit@outlook.com")

# -----------------------------------------
# Redis settings
# -----------------------------------------

# Redis connection settings
REDIS_URL = env.str("REDIS_URL", default="redis://redis:6379/0")
REDIS_SSL = REDIS_URL.startswith("rediss://")

# -----------------------------------------
# Cache settings
# -----------------------------------------

# Cache configuration
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "IGNORE_EXCEPTIONS": True,
        },
    },
}

# -----------------------------------------
# Celery settings
# -----------------------------------------

# Celery timezone setting
if USE_TZ:
    CELERY_TIMEZONE = TIME_ZONE

# Celery broker settings
CELERY_BROKER_URL = REDIS_URL
CELERY_BROKER_USE_SSL = {"ssl_cert_reqs": ssl.CERT_NONE} if REDIS_SSL else None

# Celery result backend settings
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_REDIS_BACKEND_USE_SSL = CELERY_BROKER_USE_SSL
CELERY_RESULT_EXTENDED = True
CELERY_RESULT_BACKEND_ALWAYS_RETRY = True
CELERY_RESULT_BACKEND_MAX_RETRIES = 10

# Celery serialization settings
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"

# Celery task execution settings
CELERY_TASK_TIME_LIMIT = 5 * 60
CELERY_TASK_SOFT_TIME_LIMIT = 60
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
CELERY_WORKER_SEND_TASK_EVENTS = True
CELERY_TASK_SEND_SENT_EVENT = True
CELERY_WORKER_HIJACK_ROOT_LOGGER = False

# -----------------------------------------
# Django REST Framework settings
# -----------------------------------------

# REST Framework configuration
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
}

# -----------------------------------------
# Simple JWT settings
# -----------------------------------------

# Simple JWT configuration
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(
        hours=env.int("JWT_ACCESS_TOKEN_LIFETIME_HOURS", default=6),
    ),
    "REFRESH_TOKEN_LIFETIME": timedelta(
        hours=env.int("JWT_REFRESH_TOKEN_LIFETIME_HOURS", default=24),
    ),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": None,
    "AUDIENCE": None,
    "ISSUER": None,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "JTI_CLAIM": "jti",
    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    "SLIDING_TOKEN_LIFETIME": timedelta(
        hours=env.int("JWT_ACCESS_TOKEN_LIFETIME_HOURS", default=6),
    ),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(
        hours=env.int("JWT_REFRESH_TOKEN_LIFETIME_HOURS", default=24),
    ),
}

# -----------------------------------------
# CORS settings
# -----------------------------------------

# CORS URL pattern
CORS_URLS_REGEX = r"^/api/v1/.*$"

# CORS settings
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = env.list(
    "DJANGO_CORS_ALLOWED_ORIGINS",
    default=[
        "https://agentsphere.serveo.net",
    ],
)
CORS_ALLOWED_ORIGIN_REGEXES = env.list(
    "DJANGO_CORS_ALLOWED_ORIGIN_REGEXES",
    default=[],
)
CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]
CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]

# -----------------------------------------
# DRF Spectacular settings
# -----------------------------------------

# API documentation settings
SPECTACULAR_SETTINGS = {
    "TITLE": "AgentSphere API",
    "DESCRIPTION": "Documentation of API endpoints of AgentSphere",
    "VERSION": "0.1.0",
    "SERVE_PERMISSIONS": ["rest_framework.permissions.AllowAny"],
    "SCHEMA_PATH_PREFIX": "/api/v1/",
    "SERVERS": [],
    "POSTPROCESSING_HOOKS": [
        "config.openapi.preprocess_exclude_schema_endpoint",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES_FILTER": "config.openapi.filter_authentication",
    "AUTHENTICATION_WHITELIST": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
}

# -----------------------------------------
# AWS S3 settings
# -----------------------------------------

# AWS credentials
AWS_ACCESS_KEY_ID = env.str("DJANGO_AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = env.str("DJANGO_AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = env.str("DJANGO_AWS_STORAGE_BUCKET_NAME")
AWS_QUERYSTRING_AUTH = False

# AWS cache control
_AWS_EXPIRY = 60 * 60 * 24 * 7
AWS_S3_OBJECT_PARAMETERS = {
    "CacheControl": f"max-age={_AWS_EXPIRY}, s-maxage={_AWS_EXPIRY}, must-revalidate",
}

# AWS S3 configuration
AWS_S3_MAX_MEMORY_SIZE = env.int(
    "DJANGO_AWS_S3_MAX_MEMORY_SIZE",
    default=100_000_000,
)
AWS_S3_REGION_NAME = env.str("DJANGO_AWS_S3_REGION_NAME", default=None)
AWS_S3_CUSTOM_DOMAIN = env.str("DJANGO_AWS_S3_CUSTOM_DOMAIN", default=None)
AWS_S3_ENDPOINT_URL = env.str("DJANGO_AWS_S3_ENDPOINT_URL", default=None)
AWS_S3_USE_SSL = env.bool("DJANGO_AWS_S3_USE_SSL", default=True)
AWS_S3_URL_PROTOCOL = env.str("DJANGO_AWS_S3_URL_PROTOCOL", default="https:")
aws_s3_domain = AWS_S3_CUSTOM_DOMAIN or f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"

# Media and static URLs
MEDIA_URL = f"{AWS_S3_URL_PROTOCOL}//{aws_s3_domain}/media/"
STATIC_URL = f"{AWS_S3_URL_PROTOCOL}//{aws_s3_domain}/static/"
COLLECTFASTA_STRATEGY = "collectfasta.strategies.boto3.Boto3Strategy"

# -----------------------------------------
# Storage settings
# -----------------------------------------

# Storage backends configuration
STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "location": "media",
            "file_overwrite": False,
        },
    },
    "staticfiles": {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "location": "static",
            "default_acl": "public-read",
            "file_overwrite": True,
        },
    },
    "media": {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "location": "media",
            "default_acl": "public-read",
            "file_overwrite": True,
        },
    },
}

# -----------------------------------------
# Logging settings
# -----------------------------------------

# Logging configuration
LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {"level": "INFO", "handlers": ["console"]},
    "loggers": {
        "django.db.backends": {
            "level": "ERROR",
            "handlers": ["console"],
            "propagate": False,
        },
        "sentry_sdk": {"level": "ERROR", "handlers": ["console"], "propagate": False},
        "django.security.DisallowedHost": {
            "level": "ERROR",
            "handlers": ["console"],
            "propagate": False,
        },
    },
}

# -----------------------------------------
# Sentry settings
# -----------------------------------------

# Sentry configuration
SENTRY_DSN = env.str("SENTRY_DSN")
SENTRY_LOG_LEVEL = env.str("DJANGO_SENTRY_LOG_LEVEL", logging.INFO)

# Sentry integrations
sentry_logging = LoggingIntegration(
    level=SENTRY_LOG_LEVEL,
    event_level=logging.ERROR,
)
integrations = [
    sentry_logging,
    DjangoIntegration(),
    CeleryIntegration(),
    RedisIntegration(),
]

# Initialize Sentry SDK
sentry_sdk.init(
    dsn=SENTRY_DSN,
    integrations=integrations,
    environment=env.str("SENTRY_ENVIRONMENT", default="production"),
    traces_sample_rate=env.float("SENTRY_TRACES_SAMPLE_RATE", default=0.0),
)
