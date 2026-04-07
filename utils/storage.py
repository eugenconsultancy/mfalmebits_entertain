"""
utils/storage.py
─────────────────────────────────────────────────────────────────────
Unified storage layer for MfalmeBits.

Behaviour
  • Development / local: serves static and media files via WhiteNoise /
    Django's built-in FileSystemStorage.
  • Production with S3: uses django-storages (boto3) for media uploads;
    WhiteNoise still serves collected static assets from the container
    file system (cheaper, no S3 GET costs for CSS/JS).

Toggle via environment variables:
    USE_S3=true           → activates S3 for MEDIA
    AWS_STORAGE_BUCKET_NAME=...
    AWS_ACCESS_KEY_ID=...
    AWS_SECRET_ACCESS_KEY=...
    AWS_S3_REGION_NAME=...        (default: us-east-1)
    AWS_S3_CUSTOM_DOMAIN=...      (optional CDN / CloudFront domain)
    AWS_S3_ENDPOINT_URL=...       (optional, for non-AWS S3-compatible stores
                                   such as Cloudflare R2 or DigitalOcean Spaces)

Usage in settings:
    from utils.storage import configure_storage
    configure_storage(globals())           # mutates the settings dict in-place

Or import individual backend classes directly in Django < 4.2:
    DEFAULT_FILE_STORAGE = 'utils.storage.MediaStorage'
    STATICFILES_STORAGE = 'utils.storage.StaticStorage'
"""

from __future__ import annotations

import logging
import os
from typing import Any

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════
# Storage backend classes
# ═══════════════════════════════════════════════════════════════════

def _s3_available() -> bool:
    """Return True if django-storages[boto3] is installed."""
    try:
        import storages  # noqa: F401
        import boto3     # noqa: F401
        return True
    except ImportError:
        return False


class StaticStorage:
    """
    WhiteNoise compressed static file storage.

    Selected when USE_S3 is falsy *or* when S3 is not configured.
    Static files are collected into STATIC_ROOT during build and served
    directly from disk by WhiteNoise — no S3 needed.
    """
    # Used by Django's STORAGES setting (Django ≥ 4.2) via BACKEND key
    BACKEND = "whitenoise.storage.CompressedManifestStaticFilesStorage"


class MediaStorage:
    """
    Placeholder class whose BACKEND is resolved at configure_storage()
    time based on the USE_S3 flag.
    """
    BACKEND = "django.core.files.storage.FileSystemStorage"


# ── S3 backend (only imported when USE_S3=true) ───────────────────

def _make_s3_static_storage():
    """Return a custom S3Boto3Storage subclass for STATIC files."""
    from storages.backends.s3boto3 import S3Boto3Storage  # type: ignore[import]

    class S3StaticStorage(S3Boto3Storage):
        location = "static"
        default_acl = "public-read"
        querystring_auth = False
        file_overwrite = True

    return S3StaticStorage


def _make_s3_media_storage():
    """Return a custom S3Boto3Storage subclass for MEDIA files."""
    from storages.backends.s3boto3 import S3Boto3Storage  # type: ignore[import]

    class S3MediaStorage(S3Boto3Storage):
        location = "media"
        default_acl = "public-read"
        querystring_auth = False
        file_overwrite = False       # Prevent silent overwrites of user uploads

    return S3MediaStorage


# ═══════════════════════════════════════════════════════════════════
# Main configuration function
# ═══════════════════════════════════════════════════════════════════

def configure_storage(settings: dict[str, Any]) -> None:
    """
    Mutate the Django settings dictionary to configure the correct
    storage backends based on environment variables.

    Call this near the bottom of your settings file:

        # settings/production.py
        from utils.storage import configure_storage
        configure_storage(globals())

    The function sets / overwrites these settings keys:
        STORAGES                    (Django ≥ 4.2)
        DEFAULT_FILE_STORAGE        (Django < 4.2 fallback)
        STATICFILES_STORAGE         (Django < 4.2 fallback)
        MEDIA_URL
        STATIC_URL
        AWS_* keys                  (S3 only)
    """
    use_s3 = os.environ.get("USE_S3", "false").lower() in ("true", "1", "yes")

    if use_s3:
        _configure_s3(settings)
    else:
        _configure_local(settings)


def _configure_local(settings: dict[str, Any]) -> None:
    """
    Local / WhiteNoise storage — default for development and for
    low-cost VPS deployments that keep media on disk.
    """
    logger.info("Storage: using local FileSystem + WhiteNoise.")

    static_backend = "whitenoise.storage.CompressedManifestStaticFilesStorage"
    media_backend = "django.core.files.storage.FileSystemStorage"

    # Django ≥ 4.2
    settings["STORAGES"] = {
        "default": {"BACKEND": media_backend},
        "staticfiles": {"BACKEND": static_backend},
    }
    # Django < 4.2 fallbacks (harmless to set both)
    settings["DEFAULT_FILE_STORAGE"] = media_backend
    settings["STATICFILES_STORAGE"] = static_backend

    settings.setdefault("MEDIA_URL", "/media/")
    settings.setdefault("STATIC_URL", "/static/")


def _configure_s3(settings: dict[str, Any]) -> None:
    """
    S3-compatible storage for media files.

    Static files are still served from disk via WhiteNoise (no extra
    egress costs for CSS/JS which are already compressed).
    """
    if not _s3_available():
        logger.error(
            "USE_S3=true but django-storages[boto3] is not installed. "
            "Falling back to local storage.  Run: pip install django-storages[boto3]"
        )
        _configure_local(settings)
        return

    bucket = os.environ.get("AWS_STORAGE_BUCKET_NAME", "")
    access_key = os.environ.get("AWS_ACCESS_KEY_ID", "")
    secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY", "")
    region = os.environ.get("AWS_S3_REGION_NAME", "us-east-1")
    custom_domain = os.environ.get("AWS_S3_CUSTOM_DOMAIN", "")
    endpoint_url = os.environ.get("AWS_S3_ENDPOINT_URL", "")

    if not all([bucket, access_key, secret_key]):
        logger.error(
            "USE_S3=true but AWS_STORAGE_BUCKET_NAME / AWS_ACCESS_KEY_ID / "
            "AWS_SECRET_ACCESS_KEY are not all set.  Falling back to local storage."
        )
        _configure_local(settings)
        return

    # Populate AWS settings that S3Boto3Storage reads automatically
    settings["AWS_STORAGE_BUCKET_NAME"] = bucket
    settings["AWS_ACCESS_KEY_ID"] = access_key
    settings["AWS_SECRET_ACCESS_KEY"] = secret_key
    settings["AWS_S3_REGION_NAME"] = region
    settings["AWS_S3_OBJECT_PARAMETERS"] = {
        "CacheControl": "max-age=86400",  # 1-day browser cache for uploaded media
    }
    settings["AWS_DEFAULT_ACL"] = "public-read"
    settings["AWS_QUERYSTRING_AUTH"] = False  # Public URLs without auth tokens

    if endpoint_url:
        settings["AWS_S3_ENDPOINT_URL"] = endpoint_url

    if custom_domain:
        settings["AWS_S3_CUSTOM_DOMAIN"] = custom_domain
        media_base_url = f"https://{custom_domain}/media/"
    else:
        media_base_url = (
            f"https://{bucket}.s3.{region}.amazonaws.com/media/"
        )

    # Static files: still WhiteNoise from disk
    static_backend = "whitenoise.storage.CompressedManifestStaticFilesStorage"

    # Media files: S3
    media_backend = "utils.storage.S3MediaStorageShim"

    # Django ≥ 4.2
    settings["STORAGES"] = {
        "default": {"BACKEND": media_backend},
        "staticfiles": {"BACKEND": static_backend},
    }
    # Django < 4.2 fallbacks
    settings["DEFAULT_FILE_STORAGE"] = media_backend
    settings["STATICFILES_STORAGE"] = static_backend

    settings["MEDIA_URL"] = media_base_url
    settings.setdefault("STATIC_URL", "/static/")

    logger.info("Storage: S3 media storage configured (bucket=%s).", bucket)


# ── Concrete shim class (importable string used by STORAGES setting) ─

class S3MediaStorageShim:
    """
    Thin importable shim that defers to _make_s3_media_storage().

    Django resolves the storage class by import path, so this class acts
    as a stable entry point even though the real class is generated
    dynamically to avoid import-time errors when S3 is not configured.
    """

    def __new__(cls, *args, **kwargs):
        RealClass = _make_s3_media_storage()
        return RealClass(*args, **kwargs)


# ═══════════════════════════════════════════════════════════════════
# Standalone helpers
# ═══════════════════════════════════════════════════════════════════

def media_url(path: str) -> str:
    """
    Return the full public URL for a media file path.

    Works regardless of whether storage is local or S3.

    Args:
        path: Relative path as stored in a FileField, e.g. "archive/photo.jpg"

    Returns:
        Full URL string.
    """
    from django.conf import settings as django_settings
    base = django_settings.MEDIA_URL.rstrip("/")
    return f"{base}/{path.lstrip('/')}"


def file_exists(storage_field) -> bool:
    """
    Safely check whether a FileField / ImageField has an associated file.

    Args:
        storage_field: A Django FieldFile instance (e.g. instance.photo).

    Returns:
        True if the field has a file and the file exists in storage.
    """
    if not storage_field:
        return False
    try:
        return bool(storage_field.name and storage_field.storage.exists(storage_field.name))
    except Exception:
        return False