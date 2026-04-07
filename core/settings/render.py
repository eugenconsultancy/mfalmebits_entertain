"""
core/settings/render.py
─────────────────────────────────────────────────────────────────────
Production settings for MfalmeBits on Render.com (or any Linux VPS).

Key changes from development.py
  • DEBUG = False, ALLOWED_HOSTS from env
  • PostgreSQL via DATABASE_URL
  • SMTP email (Mailgun / SendGrid / SMTP2Go)
  • Session & CSRF hardening for HTTPS
  • Correct AllAuth configuration for a live signup flow
  • WhiteNoise for static files; optional S3 for media
  • Celery + Redis config (low-RAM 2 GB profile)
  • Removed robots package (Python 2 incompatible); uses template view
  • Removed debug_toolbar (not safe or useful in production)
"""

import os
import dj_database_url
from decouple import config, Csv

from .base import *  # noqa: F401,F403  — inherits all base settings


# ═══════════════════════════════════════════════════════════════════
# 1. Core
# ═══════════════════════════════════════════════════════════════════

DEBUG = False

SECRET_KEY = config("DJANGO_SECRET_KEY")  # Must be set — no default!

ALLOWED_HOSTS = config(
    "DJANGO_ALLOWED_HOSTS",
    default="localhost",
    cast=Csv(),
)

# Render injects this; your custom domain goes here too
CSRF_TRUSTED_ORIGINS = config(
    "CSRF_TRUSTED_ORIGINS",
    default="https://mfalmebits-entertain.onrender.com",
    cast=Csv(),
)


# ═══════════════════════════════════════════════════════════════════
# 2. Installed apps — remove dev-only packages
# ═══════════════════════════════════════════════════════════════════

# Pull in base INSTALLED_APPS and remove packages unsafe in production
_REMOVE_IN_PROD = {"debug_toolbar", "django_extensions", "robots"}
INSTALLED_APPS = [  # type: ignore[assignment]
    app for app in INSTALLED_APPS  # noqa: F405
    if app not in _REMOVE_IN_PROD
]


# ═══════════════════════════════════════════════════════════════════
# 3. Middleware — no debug_toolbar, AllAuth middleware kept
# ═══════════════════════════════════════════════════════════════════

MIDDLEWARE = [  # type: ignore[assignment]
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",         # Must be 2nd
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",       # Required by AllAuth 0.56+
    # Uncomment when BrokenLink model is migrated:
    # "utils.seo_monitor.SEOMonitorMiddleware",
]


# ═══════════════════════════════════════════════════════════════════
# 4. Database — PostgreSQL
# ═══════════════════════════════════════════════════════════════════

_db_url = config("DATABASE_URL", default=None)
if not _db_url:
    raise ValueError(
        "DATABASE_URL environment variable is not set.  "
        "Add it in your Render dashboard → Environment → Add Environment Variable."
    )

DATABASES = {  # type: ignore[assignment]
    "default": dj_database_url.config(
        default=_db_url,
        conn_max_age=60,           # Keep connections alive for 60 s (connection pooling lite)
        conn_health_checks=True,   # Drop stale connections automatically
        ssl_require=True,          # Render Postgres enforces TLS
    )
}


# ═══════════════════════════════════════════════════════════════════
# 5. Static & Media files
# ═══════════════════════════════════════════════════════════════════

# Static files — served by WhiteNoise directly from the container FS.
# The Jazzmin admin CSS/JS lives here after `collectstatic`.
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")  # type: ignore[name-defined]
STATICFILES_DIRS = [BASE_DIR / "static"]              # type: ignore[name-defined]

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

# CompressedManifestStaticFilesStorage adds a content hash to every
# filename → solves browser cache-busting automatically.
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Media files (user uploads)
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")  # type: ignore[name-defined]

# ── Optional S3 for media ────────────────────────────────────────────
# Set USE_S3=true in Render env to activate.
# Static files remain on disk (WhiteNoise) for zero egress cost.
_use_s3 = config("USE_S3", default="false").lower() in ("true", "1", "yes")
if _use_s3:
    from utils.storage import configure_storage
    configure_storage(globals())

# Disable django-compressor in production (WhiteNoise handles compression)
COMPRESS_ENABLED = False
COMPRESS_OFFLINE = False


# ═══════════════════════════════════════════════════════════════════
# 6. Security hardening
# ═══════════════════════════════════════════════════════════════════

# Tell Django it's behind an SSL-terminating proxy (Render / Nginx)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Do NOT redirect in Django — Render/Nginx/Cloudflare handle HTTP→HTTPS
SECURE_SSL_REDIRECT = False

SECURE_HSTS_SECONDS = 31_536_000        # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

# Cookies
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_AGE = 1_209_600          # 2 weeks
SESSION_SAVE_EVERY_REQUEST = False      # Reduces DB writes

CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = False            # JS needs to read CSRF for AJAX
CSRF_COOKIE_SAMESITE = "Lax"


# ═══════════════════════════════════════════════════════════════════
# 7. Authentication — AllAuth (live SMTP flow)
# ═══════════════════════════════════════════════════════════════════

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/accounts/dashboard/"
LOGOUT_REDIRECT_URL = "/"
ACCOUNT_LOGOUT_REDIRECT_URL = "/"

# Accept username OR email at the login prompt
ACCOUNT_AUTHENTICATION_METHOD = "username_email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_USERNAME_MIN_LENGTH = 3
ACCOUNT_PRESERVE_USERNAME_CASING = False
ACCOUNT_UNIQUE_EMAIL = True

# Enable email verification only when your SMTP is working.
# Switch to "mandatory" once you have confirmed mail delivery.
ACCOUNT_EMAIL_VERIFICATION = config(
    "ACCOUNT_EMAIL_VERIFICATION", default="optional"
)

ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_LOGIN_ON_PASSWORD_RESET = True
ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_SESSION_REMEMBER = True

# Set False to prevent strangers from creating accounts on the live site
ACCOUNT_SIGNUP_ENABLED = config("ACCOUNT_SIGNUP_ENABLED", default=True, cast=bool)

# Use our custom forms so AllAuth views inherit MfalmeBits styling
ACCOUNT_FORMS = {
    "login": "apps.accounts.forms.UserLoginForm",
    "signup": "apps.accounts.forms.UserRegistrationForm",
}


# ═══════════════════════════════════════════════════════════════════
# 8. Email — SMTP (switch from console backend)
# ═══════════════════════════════════════════════════════════════════

# Set EMAIL_BACKEND=smtp in your Render environment to send real mail.
_email_backend = config("EMAIL_BACKEND", default="console")

if _email_backend == "smtp":
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = config("EMAIL_HOST", default="smtp.mailgun.org")
    EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
    EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
    EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
    EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
    DEFAULT_FROM_EMAIL = config(
        "DEFAULT_FROM_EMAIL", default="MfalmeBits <noreply@mfalmebits.com>"
    )
    SERVER_EMAIL = DEFAULT_FROM_EMAIL
else:
    # Logs emails to stdout — safe for early production while SMTP is not yet set
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
    DEFAULT_FROM_EMAIL = config(
        "DEFAULT_FROM_EMAIL", default="MfalmeBits <noreply@mfalmebits.com>"
    )


# ═══════════════════════════════════════════════════════════════════
# 9. Cache — Redis (falls back to local memory on 2 GB RAM boxes)
# ═══════════════════════════════════════════════════════════════════

_redis_url = config("REDIS_URL", default=None)

if _redis_url:
    CACHES = {  # type: ignore[assignment]
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": _redis_url,
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                # Pool settings tuned for 2 GB RAM host
                "CONNECTION_POOL_KWARGS": {
                    "max_connections": 10,  # Keep pool small; 2 GB hosts have tight FD limits
                },
                "SOCKET_CONNECT_TIMEOUT": 5,
                "SOCKET_TIMEOUT": 5,
                "IGNORE_EXCEPTIONS": True,  # Degrade gracefully if Redis is down
            },
            "KEY_PREFIX": "mfalmebits",
            "TIMEOUT": 300,
        }
    }
    SESSION_ENGINE = "django.contrib.sessions.backends.cache"
    SESSION_CACHE_ALIAS = "default"
else:
    CACHES = {  # type: ignore[assignment]
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "mfalmebits-cache",
        }
    }


# ═══════════════════════════════════════════════════════════════════
# 10. Celery — low-RAM profile
# ═══════════════════════════════════════════════════════════════════

if _redis_url:
    CELERY_BROKER_URL = _redis_url
    CELERY_RESULT_BACKEND = _redis_url
else:
    CELERY_BROKER_URL = "memory://"
    CELERY_RESULT_BACKEND = "django-db"

CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "Africa/Nairobi"

# 2 GB RAM: 2 workers × 2 threads uses ~400 MB; leaves room for DB connections
CELERY_WORKER_CONCURRENCY = config("CELERY_CONCURRENCY", default=2, cast=int)
CELERY_WORKER_MAX_TASKS_PER_CHILD = 200   # Recycle workers to prevent memory leaks
CELERY_WORKER_PREFETCH_MULTIPLIER = 1     # Fair task distribution


# ═══════════════════════════════════════════════════════════════════
# 11. Stripe
# ═══════════════════════════════════════════════════════════════════

STRIPE_PUBLIC_KEY = config("STRIPE_PUBLIC_KEY", default="")
STRIPE_SECRET_KEY = config("STRIPE_SECRET_KEY", default="")
STRIPE_WEBHOOK_SECRET = config("STRIPE_WEBHOOK_SECRET", default="")


# ═══════════════════════════════════════════════════════════════════
# 12. M-Pesa Daraja
# ═══════════════════════════════════════════════════════════════════

MPESA_CONSUMER_KEY = config("MPESA_CONSUMER_KEY", default="")
MPESA_CONSUMER_SECRET = config("MPESA_CONSUMER_SECRET", default="")
MPESA_PASSKEY = config("MPESA_PASSKEY", default="")
MPESA_SHORTCODE = config("MPESA_SHORTCODE", default="")
MPESA_CALLBACK_URL = config("MPESA_CALLBACK_URL", default="")
MPESA_ENVIRONMENT = config("MPESA_ENVIRONMENT", default="production")


# ═══════════════════════════════════════════════════════════════════
# 13. CORS (for any future API / mobile app)
# ═══════════════════════════════════════════════════════════════════

CORS_ALLOWED_ORIGINS = config(
    "CORS_ALLOWED_ORIGINS",
    default="",
    cast=Csv(),
)
CORS_ALLOW_CREDENTIALS = True


# ═══════════════════════════════════════════════════════════════════
# 14. Logging — structured, stdout-friendly for Render log streams
# ═══════════════════════════════════════════════════════════════════

LOGGING = {  # type: ignore[assignment]
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": "logging.Formatter",
            "format": '{"time":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","msg":%(message)r}',
        },
        "verbose": {
            "format": "[%(asctime)s] %(levelname)s %(name)s — %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django": {"handlers": ["console"], "level": "WARNING", "propagate": False},
        "django.security": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "django.request": {"handlers": ["console"], "level": "ERROR", "propagate": False},
        "allauth": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "apps": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "utils": {"handlers": ["console"], "level": "INFO", "propagate": False},
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
}


# ═══════════════════════════════════════════════════════════════════
# 15. Misc app-level settings
# ═══════════════════════════════════════════════════════════════════

# Contact & notification email addresses
COLLABORATION_EMAIL = config("COLLABORATION_EMAIL", default="")
INSTITUTIONAL_EMAIL = config("INSTITUTIONAL_EMAIL", default="")
COMMENT_NOTIFICATION_EMAIL = config("COMMENT_NOTIFICATION_EMAIL", default="")

# Sentry (optional but recommended)
_sentry_dsn = config("SENTRY_DSN", default="")
if _sentry_dsn:
    try:
        import sentry_sdk
        from sentry_sdk.integrations.django import DjangoIntegration
        from sentry_sdk.integrations.celery import CeleryIntegration

        sentry_sdk.init(
            dsn=_sentry_dsn,
            integrations=[DjangoIntegration(), CeleryIntegration()],
            traces_sample_rate=0.1,     # 10 % of requests traced
            send_default_pii=False,
        )
    except ImportError:
        pass  # sentry-sdk not installed — silent fail