"""
render.py — Production settings for MfalmeBits Entertainment on Render
Fixed with proper AllAuth middleware configuration
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
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# ─────────────────────────────────────────────────────────────────────
# SESSION & CSRF - CRITICAL FOR LOGIN
# ─────────────────────────────────────────────────────────────────────
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_AGE = 86400
SESSION_SAVE_EVERY_REQUEST = True

CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = 'Lax'

# ─────────────────────────────────────────────────────────────────────
# MIDDLEWARE - AllAuth middleware IS required
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
    'allauth.account.middleware.AccountMiddleware',  # REQUIRED - must be present
]

# ─────────────────────────────────────────────────────────────────────
# AUTHENTICATION - Both backends required for AllAuth
# ─────────────────────────────────────────────────────────────────────
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',  # Django admin auth
    'allauth.account.auth_backends.AuthenticationBackend',  # AllAuth
]

# AllAuth Settings - Configured to work with both username and email
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

ACCOUNT_AUTHENTICATION_METHOD = 'username_email'  # Accept both
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'none'  # Disable email verification for free tier
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_LOGIN_ON_PASSWORD_RESET = True
ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_LOGOUT_REDIRECT_URL = '/'
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_USER_MODEL_USERNAME_FIELD = 'username'
ACCOUNT_USERNAME_MIN_LENGTH = 3
ACCOUNT_PRESERVE_USERNAME_CASING = False
ACCOUNT_UNIQUE_EMAIL = True

# Disable signup if you only want superuser access
ACCOUNT_ADAPTER = 'allauth.account.adapter.DefaultAccountAdapter'
ACCOUNT_SIGNUP_ENABLED = False  # Set to True if you want public signup

# ─────────────────────────────────────────────────────────────────────
# EMAIL - Use console backend for now (no email sending issues)
# ─────────────────────────────────────────────────────────────────────
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
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
# LOGGING - Debug login issues
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
        'allauth': {
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