"""
render.py — Production settings for MfalmeBits Entertainment on Render
Fixed to prevent login loops and authentication issues
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

ALLOWED_HOSTS = config(
    'DJANGO_ALLOWED_HOSTS',
    default='mfalmebits-entertain.onrender.com,localhost,127.0.0.1'
).split(',')

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in config(
        'CSRF_TRUSTED_ORIGINS',
        default='https://mfalmebits-entertain.onrender.com'
    ).split(',')
]

# ─────────────────────────────────────────────────────────────────────
# DATABASE
# ─────────────────────────────────────────────────────────────────────
_db_url = config('DATABASE_URL', default=None)
if not _db_url:
    raise ValueError("DATABASE_URL is not set")

DATABASES = {
    'default': dj_database_url.config(
        default=_db_url,
        conn_max_age=60,
        ssl_require=True,
        conn_health_checks=True,
    )
}

# ─────────────────────────────────────────────────────────────────────
# STATIC & MEDIA
# ─────────────────────────────────────────────────────────────────────
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

COMPRESS_ENABLED = False
COMPRESS_OFFLINE = False

# ─────────────────────────────────────────────────────────────────────
# SECURITY & SSL
# ─────────────────────────────────────────────────────────────────────
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = False  # Render handles SSL
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# ─────────────────────────────────────────────────────────────────────
# SESSION & CSRF - CRITICAL FOR LOGIN
# ─────────────────────────────────────────────────────────────────────
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_AGE = 86400
SESSION_SAVE_EVERY_REQUEST = True  # Important for session persistence

CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_USE_SESSIONS = False  # Don't store CSRF in session to avoid conflicts

# ─────────────────────────────────────────────────────────────────────
# AUTHENTICATION - PREVENT LOGIN LOOP
# ─────────────────────────────────────────────────────────────────────
# Simple login redirects - avoid complex chains
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Disable AllAuth for admin to prevent conflicts
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',  # Default Django auth
    # 'allauth.account.auth_backends.AuthenticationBackend',  # Comment out if causing issues
]

# If you need AllAuth, use these settings:
ACCOUNT_AUTHENTICATION_METHOD = 'username_email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'none'
ACCOUNT_LOGIN_ATTEMPTS_LIMIT = 5
ACCOUNT_LOGIN_ATTEMPTS_TIMEOUT = 300
ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_LOGOUT_REDIRECT_URL = '/'
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_USER_MODEL_USERNAME_FIELD = 'username'
ACCOUNT_USERNAME_MIN_LENGTH = 3

# ─────────────────────────────────────────────────────────────────────
# MIDDLEWARE ORDER - Important for login
# ─────────────────────────────────────────────────────────────────────
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'allauth.account.middleware.AccountMiddleware',  # Temporarily disable if causing loop
]

# ─────────────────────────────────────────────────────────────────────
# EMAIL (optional)
# ─────────────────────────────────────────────────────────────────────
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # Use console for now

# ─────────────────────────────────────────────────────────────────────
# CACHE
# ─────────────────────────────────────────────────────────────────────
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# ─────────────────────────────────────────────────────────────────────
# LOGGING - Helps debug login issues
# ─────────────────────────────────────────────────────────────────────
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {asctime} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.security': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

# Stripe (if needed)
STRIPE_PUBLIC_KEY = config('STRIPE_PUBLIC_KEY', default='')
STRIPE_SECRET_KEY = config('STRIPE_SECRET_KEY', default='')