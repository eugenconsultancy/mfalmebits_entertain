"""
core/settings/base.py
─────────────────────────────────────────────────────────────────────
Shared base settings for MfalmeBits — inherited by all environments.

Updated for VPS Deployment (mfalmebits.africa):
  • Fixed BASE_DIR logic for core/settings/base.py placement
  • Added WhiteNoise for static file serving under Nginx
  • Added secure production settings with SSL support
  • Added database fallback with dj-database-url
  • Added M-Pesa & Email integration settings
  • Added CSRF_TRUSTED_ORIGINS for HTTPS
"""

from pathlib import Path
import os
from decouple import config
import dj_database_url

# ─────────────────────────────────────────────────────────────────────
# BASE DIR — Fixed for core/settings/base.py placement
# ─────────────────────────────────────────────────────────────────────
# With settings in core/settings/base.py, we need to go up three levels:
# core/settings/base.py → core/settings/ → core/ → project root
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# ─────────────────────────────────────────────────────────────────────
# SECURITY — No hardcoded values, all from environment
# ─────────────────────────────────────────────────────────────────────
SECRET_KEY = config("DJANGO_SECRET_KEY", default="")

# DEBUG must be explicitly set to True in development
DEBUG = config("DJANGO_DEBUG", default=False, cast=bool)

ALLOWED_HOSTS = config(
    "DJANGO_ALLOWED_HOSTS",
    default="localhost,127.0.0.1,37.59.191.158,https://mfalmebits.africa,https://www.mfalmebits.africa"
).split(",")

# ─────────────────────────────────────────────────────────────────────
# CSRF TRUSTED ORIGINS — Required for HTTPS and M-Pesa/Stripe
# ─────────────────────────────────────────────────────────────────────
CSRF_TRUSTED_ORIGINS = [f"https://{host}" for host in ALLOWED_HOSTS if host not in ['localhost', '127.0.0.1']]
CSRF_TRUSTED_ORIGINS.extend([f"http://{host}" for host in ALLOWED_HOSTS])

# ─────────────────────────────────────────────────────────────────────
# INSTALLED APPS
# ─────────────────────────────────────────────────────────────────────
DJANGO_APPS = [
    "jazzmin",                          # Must be before django.contrib.admin
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "django.contrib.sites",
    "django.contrib.humanize",
]

THIRD_PARTY_APPS = [
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "taggit",
    "django_ckeditor_5",
    "crispy_forms",
    "crispy_bootstrap5",
    "stripe",
    "django_celery_beat",
    "django_celery_results",
    "compressor",
    "cacheops",
    "rest_framework",
    "corsheaders",
    "storages",
    "import_export",
    "whitenoise.runserver_nostatic",   # For WhiteNoise with runserver
]

LOCAL_APPS = [
    "apps.home",
    "apps.about",
    "apps.accounts",
    "apps.contact",
    "apps.blog",
    "apps.newsletter",
    "apps.archive",
    "apps.library",
    "apps.institutional",
    "apps.collaboration",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

SITE_ID = 1

# ─────────────────────────────────────────────────────────────────────
# MIDDLEWARE — WhiteNoise added early for static files
# ─────────────────────────────────────────────────────────────────────
MIDDLEWARE = [
    "whitenoise.middleware.WhiteNoiseMiddleware", # For static files under Nginx
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = "core.urls"

# ─────────────────────────────────────────────────────────────────────
# TEMPLATES
# ─────────────────────────────────────────────────────────────────────
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.seo_settings",
                "core.context_processors.organization_schema",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"
ASGI_APPLICATION = "core.asgi.application"

# ─────────────────────────────────────────────────────────────────────
# DATABASE — Supports both SQLite (local) and PostgreSQL (VPS)
# ─────────────────────────────────────────────────────────────────────
# Use dj-database-url for easy switching between SQLite and PostgreSQL
# Default to SQLite for local development, override with DATABASE_URL on VPS
DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR}/db.sqlite3",
        conn_max_age=600,
        ssl_require=False
    )
}

# ─────────────────────────────────────────────────────────────────────
# PASSWORD VALIDATION
# ─────────────────────────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ─────────────────────────────────────────────────────────────────────
# INTERNATIONALISATION
# ─────────────────────────────────────────────────────────────────────
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Africa/Nairobi"
USE_I18N = True
USE_TZ = True

# ─────────────────────────────────────────────────────────────────────
# STATIC & MEDIA — Absolute paths for Nginx
# ─────────────────────────────────────────────────────────────────────
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"      # Nginx serves from here

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"              # User-uploaded files

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "compressor.finders.CompressorFinder",
]

# WhiteNoise configuration for static file serving under Nginx
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
WHITENOISE_KEEP_ONLY_HASHED_FILES = True
WHITENOISE_USE_FINDERS = True

COMPRESS_ENABLED = True
COMPRESS_OFFLINE = False

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ─────────────────────────────────────────────────────────────────────
# CRISPY FORMS
# ─────────────────────────────────────────────────────────────────────
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# ─────────────────────────────────────────────────────────────────────
# AUTHENTICATION
# ─────────────────────────────────────────────────────────────────────
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/accounts/dashboard/"
LOGOUT_REDIRECT_URL = "/"

ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = "username_email"
ACCOUNT_EMAIL_VERIFICATION = "optional"   # Override to "mandatory" in production
ACCOUNT_LOGIN_REDIRECT_URL = "/accounts/dashboard/"
ACCOUNT_LOGOUT_REDIRECT_URL = "/"
ACCOUNT_SESSION_REMEMBER = True

# ─────────────────────────────────────────────────────────────────────
# EMAIL — Console in base; override in production with SMTP
# ─────────────────────────────────────────────────────────────────────
EMAIL_BACKEND = config(
    "EMAIL_BACKEND",
    default="django.core.mail.backends.console.EmailBackend"
)
EMAIL_HOST = config("EMAIL_HOST", default="")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = config(
    "DEFAULT_FROM_EMAIL",
    default="MfalmeBits <noreply@mfalmebits.africa>"
)

# ─────────────────────────────────────────────────────────────────────
# CACHE — Local memory in base; override with Redis in production
# ─────────────────────────────────────────────────────────────────────
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "mfalmebits-cache",
    }
}

# ─────────────────────────────────────────────────────────────────────
# SECURE PRODUCTION SETTINGS (Conditional)
# ─────────────────────────────────────────────────────────────────────
if not DEBUG:
    # HTTPS Settings for VPS with SSL
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=True, cast=bool)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    X_FRAME_OPTIONS = "DENY"
    
    # CSRF settings for HTTPS
    CSRF_TRUSTED_ORIGINS = [f"https://{host}" for host in ALLOWED_HOSTS if host not in ['localhost', '127.0.0.1']]
    CSRF_TRUSTED_ORIGINS.extend([f"https://www.{host}" for host in ALLOWED_HOSTS if host not in ['localhost', '127.0.0.1']])

# ─────────────────────────────────────────────────────────────────────
# DEBUG TOOLBAR — Only localhost
# ─────────────────────────────────────────────────────────────────────
INTERNAL_IPS = ["127.0.0.1", "::1"]

# ─────────────────────────────────────────────────────────────────────
# CORS SETTINGS
# ─────────────────────────────────────────────────────────────────────
CORS_ALLOWED_ORIGINS = [
    "https://mfalmebits.africa",
    "https://www.mfalmebits.africa",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]
CORS_ALLOW_CREDENTIALS = True

# ─────────────────────────────────────────────────────────────────────
# STRIPE PAYMENT INTEGRATION
# ─────────────────────────────────────────────────────────────────────
STRIPE_PUBLIC_KEY = config("STRIPE_PUBLIC_KEY", default="")
STRIPE_SECRET_KEY = config("STRIPE_SECRET_KEY", default="")
STRIPE_WEBHOOK_SECRET = config("STRIPE_WEBHOOK_SECRET", default="")

# ─────────────────────────────────────────────────────────────────────
# M-PESA DARAJA INTEGRATION (Safaricom API)
# ─────────────────────────────────────────────────────────────────────
MPESA_ENVIRONMENT = config("MPESA_ENVIRONMENT", default="sandbox")  # sandbox or production
MPESA_CONSUMER_KEY = config("MPESA_CONSUMER_KEY", default="")
MPESA_CONSUMER_SECRET = config("MPESA_CONSUMER_SECRET", default="")
MPESA_SHORTCODE = config("MPESA_SHORTCODE", default="174379")
MPESA_PASSKEY = config("MPESA_PASSKEY", default="")
MPESA_CALLBACK_URL = config("MPESA_CALLBACK_URL", default="")
MPESA_INITIATOR_NAME = config("MPESA_INITIATOR_NAME", default="")
MPESA_SECURITY_CREDENTIAL = config("MPESA_SECURITY_CREDENTIAL", default="")

# ─────────────────────────────────────────────────────────────────────
# APP-SPECIFIC EMAIL ADDRESSES
# ─────────────────────────────────────────────────────────────────────
CONTACT_EMAIL = config("CONTACT_EMAIL", default="contact@mfalmebits.africa")
SUPPORT_EMAIL = config("SUPPORT_EMAIL", default="support@mfalmebits.africa")
COLLABORATION_EMAIL = config("COLLABORATION_EMAIL", default="collab@mfalmebits.africa")
INSTITUTIONAL_EMAIL = config("INSTITUTIONAL_EMAIL", default="institutional@mfalmebits.africa")
COMMENT_NOTIFICATION_EMAIL = config("COMMENT_NOTIFICATION_EMAIL", default="notifications@mfalmebits.africa")

# ─────────────────────────────────────────────────────────────────────
# LOGGING
# ─────────────────────────────────────────────────────────────────────
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
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "logs" / "django.log",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "apps": {
            "handlers": ["console", "file"],
            "level": "DEBUG" if DEBUG else "INFO",
            "propagate": False,
        },
    },
}

# Create logs directory if it doesn't exist
LOGS_DIR = BASE_DIR / "logs"
if not LOGS_DIR.exists():
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

# ─────────────────────────────────────────────────────────────────────
# CKEDITOR 5 CONFIGURATION
# ─────────────────────────────────────────────────────────────────────
CKEDITOR_5_UPLOAD_FILE_VIEW_NAME = "ckeditor_5_upload_file"
CKEDITOR_5_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"

CKEDITOR_5_CONFIGS = {
    "default": {
        "toolbar": [
            "heading", "|", "bold", "italic", "link",
            "bulletedList", "numberedList", "blockQuote",
            "imageUpload", "mediaEmbed", "insertTable", "undo", "redo",
        ],
    },
    "extends": {
        "blockToolbar": [
            "paragraph", "heading1", "heading2", "heading3",
            "|", "bulletedList", "numberedList", "|", "blockQuote",
        ],
        "toolbar": [
            "heading", "|", "outdent", "indent", "|",
            "bold", "italic", "link", "underline", "strikethrough",
            "code", "subscript", "superscript", "highlight", "|",
            "bulletedList", "numberedList", "todoList", "|",
            "blockQuote", "imageUpload", "mediaEmbed", "insertTable",
            "sourceEditing", "undo", "redo",
        ],
        "image": {
            "toolbar": [
                "imageTextAlternative", "|",
                "imageStyle:alignLeft", "imageStyle:alignCenter", "imageStyle:alignRight",
                "|", "imageStyle:full", "imageStyle:side",
            ],
            "styles": ["full", "side", "alignLeft", "alignCenter", "alignRight"],
        },
        "table": {
            "contentToolbar": [
                "tableColumn", "tableRow", "mergeTableCells",
                "tableProperties", "tableCellProperties",
            ],
        },
        "heading": {
            "options": [
                {"model": "paragraph", "title": "Paragraph", "class": "ck-heading_paragraph"},
                {"model": "heading1", "view": "h1", "title": "Heading 1", "class": "ck-heading_heading1"},
                {"model": "heading2", "view": "h2", "title": "Heading 2", "class": "ck-heading_heading2"},
                {"model": "heading3", "view": "h3", "title": "Heading 3", "class": "ck-heading_heading3"},
            ],
        },
    },
}

CKEDITOR_5_CUSTOM_CSS = "admin/css/mfalmebits_admin.css"

# ─────────────────────────────────────────────────────────────────────
# JAZZMIN ADMIN THEME — Shared across all environments
# ─────────────────────────────────────────────────────────────────────
JAZZMIN_SETTINGS = {
    "site_title": "MfalmeBits Admin",
    "site_header": "MfalmeBits",
    "site_brand": "MfalmeBits",
    "site_logo": "images/logo.png",
    "site_logo_classes": "img-circle",
    "site_icon": "images/favicon.ico",
    "welcome_sign": "MfalmeBits Management Console",
    "copyright": "MfalmeBits © 2026",
    "search_model": ["auth.user", "blog.Post", "library.DigitalProduct"],
    "user_avatar": None,
    "topmenu_links": [
        {"name": "Dashboard", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "Portals", "dropdown": [
            {"name": "Main Site", "url": "/", "new_window": True},
            {"name": "Digital Archive", "url": "/archive/", "new_window": True},
            {"name": "Resource Library", "url": "/library/", "new_window": True},
        ]},
        {"model": "contact.ContactMessage", "name": "Support Inbox"},
        {"model": "auth.User", "name": "Team Members"},
    ],
    "usermenu_links": [
        {"name": "Public Site", "url": "/", "new_window": True},
        {"model": "auth.user"},
    ],
    "show_sidebar": True,
    "navigation_expanded": False,
    "hide_apps": [],
    "hide_models": [],
    "order_with_respect_to": [
        "home", "blog", "archive", "library", "newsletter",
        "contact", "collaboration", "institutional", "accounts", "auth",
    ],
    "icons": {
        "auth": "fas fa-shield-alt",
        "auth.user": "fas fa-user-shield",
        "auth.Group": "fas fa-users",
        "home": "fas fa-desktop",
        "home.HeroSlide": "fas fa-images",
        "blog": "fas fa-pen-fancy",
        "blog.Post": "fas fa-newspaper",
        "archive": "fas fa-archive",
        "archive.ArchiveEntry": "fas fa-scroll",
        "archive.Theme": "fas fa-tags",
        "library": "fas fa-book",
        "library.DigitalProduct": "fas fa-book-open",
        "newsletter": "fas fa-paper-plane",
        "newsletter.Subscriber": "fas fa-envelope",
        "contact": "fas fa-envelope-open-text",
        "contact.ContactMessage": "fas fa-comments",
        "institutional": "fas fa-university",
        "collaboration": "fas fa-project-diagram",
        "accounts": "fas fa-id-card",
        "sites.Site": "fas fa-globe-africa",
    },
    "default_icon_parents": "fas fa-folder-plus",
    "default_icon_children": "fas fa-caret-right",
    "related_modal_active": True,
    "use_google_fonts_cdn": True,
    "show_ui_builder": False,
    "changeform_format": "horizontal_tabs",
}

JAZZMIN_UI_TWEAKS = {
    "theme": "lumen",
    "dark_mode_theme": None,
    "navbar_fixed": True,
    "sidebar_fixed": True,
    "footer_fixed": False,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_flat_style": True,
    "navbar": "navbar-dark",
    "brand_colour": "navbar-primary",
    "no_navbar_border": True,
    "button_classes": {
        "primary": "btn-primary shadow-sm",
        "secondary": "btn-outline-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success",
    },
    "actions_sticky_top": True,
}

# ─────────────────────────────────────────────────────────────────────
# CELERY CONFIGURATION (for background tasks)
# ─────────────────────────────────────────────────────────────────────
CELERY_BROKER_URL = config("CELERY_BROKER_URL", default="redis://localhost:6379/0")
CELERY_RESULT_BACKEND = "django-db"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE

# ─────────────────────────────────────────────────────────────────────
# SESSION & SECURITY
# ─────────────────────────────────────────────────────────────────────
SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_COOKIE_AGE = 1209600  # 2 weeks
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"

# ─────────────────────────────────────────────────────────────────────
# DJANGO-CACHOPS (for query caching)
# ─────────────────────────────────────────────────────────────────────
CACHEOPS_REDIS = config("CACHEOPS_REDIS", default="redis://localhost:6379/1")
CACHEOPS_DEFAULTS = {"timeout": 60 * 15}  # 15 minutes
CACHEOPS = {
    "auth.user": {"ops": "get", "timeout": 60 * 10},
    "blog.post": {"ops": "all", "timeout": 60 * 30},
    "archive.archiverentry": {"ops": "all", "timeout": 60 * 60},
    "library.digitalproduct": {"ops": "all", "timeout": 60 * 30},
}