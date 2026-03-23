"""
render.py — Production settings for Render free tier
"""
import os
import dj_database_url
from .base import *
from decouple import config

# ─────────────────────────────────────────────────────────────────────
# CORE SETTINGS
# ─────────────────────────────────────────────────────────────────────
DEBUG = False
SECRET_KEY = config('DJANGO_SECRET_KEY')

# Fixed ALLOWED_HOSTS with exact subdomain
ALLOWED_HOSTS = config(
    'DJANGO_ALLOWED_HOSTS',
    default='mfalmebits.onrender.com,localhost,127.0.0.1'
).split(',')

# Fixed CSRF_TRUSTED_ORIGINS with exact subdomain (no wildcard)
CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in config(
        'CSRF_TRUSTED_ORIGINS',
        default='https://mfalmebits.onrender.com'
    ).split(',')
]

# ─────────────────────────────────────────────────────────────────────
# DATABASE - Force PostgreSQL, fail loudly if missing
# ─────────────────────────────────────────────────────────────────────
_db_url = config('DATABASE_URL', default=None)
if not _db_url:
    raise ValueError(
        "DATABASE_URL is not set in Render environment variables. "
        "Please add it in Render Dashboard > Environment Variables"
    )

DATABASES = {
    'default': dj_database_url.config(
        default=_db_url,
        conn_max_age=60,          # Short connection age for free tier (containers restart)
        ssl_require=True,          # Render requires SSL for PostgreSQL
        conn_health_checks=True,   # Detect stale connections
    )
}

# ─────────────────────────────────────────────────────────────────────
# STATIC & MEDIA FILES
# ─────────────────────────────────────────────────────────────────────
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Disable compressor to avoid MIME type issues
COMPRESS_ENABLED = False
COMPRESS_OFFLINE = False

# ─────────────────────────────────────────────────────────────────────
# HTTPS & PROXY CONFIGURATION - CRITICAL FIX FOR RENDER
# ─────────────────────────────────────────────────────────────────────
# Render terminates SSL at load balancer. Tell Django to trust the proxy's
# X-Forwarded-Proto header so request.is_secure() returns True.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = False  # Render handles HTTPS redirect - avoid redirect loops
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# ─────────────────────────────────────────────────────────────────────
# SESSION & CSRF COOKIES
# ─────────────────────────────────────────────────────────────────────
SESSION_COOKIE_SECURE = True      # HTTPS only
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_AGE = 86400        # 1 day (free tier containers restart anyway)

CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = False      # JavaScript needs to read CSRF token
CSRF_COOKIE_SAMESITE = 'Lax'

# ─────────────────────────────────────────────────────────────────────
# AUTHENTICATION - FIXED FOR BOTH USERNAME AND EMAIL
# ─────────────────────────────────────────────────────────────────────
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Critical fix: Accept both username AND email so superuser can log in
ACCOUNT_AUTHENTICATION_METHOD = 'username_email'  # Changed from 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = True                   # Changed from False
ACCOUNT_EMAIL_VERIFICATION = 'none'                # Changed from 'mandatory' to avoid lockout
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_LOGIN_ON_PASSWORD_RESET = True
ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'

# ─────────────────────────────────────────────────────────────────────
# EMAIL CONFIGURATION
# ─────────────────────────────────────────────────────────────────────
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@mfalmebits.com')

# ─────────────────────────────────────────────────────────────────────
# CACHE
# ─────────────────────────────────────────────────────────────────────
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# ─────────────────────────────────────────────────────────────────────
# STRIPE
# ─────────────────────────────────────────────────────────────────────
STRIPE_PUBLIC_KEY = config('STRIPE_PUBLIC_KEY', default='')
STRIPE_SECRET_KEY = config('STRIPE_SECRET_KEY', default='')

# ─────────────────────────────────────────────────────────────────────
# LOGGING
# ─────────────────────────────────────────────────────────────────────
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}