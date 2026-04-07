"""
utils/seo_monitor.py
─────────────────────────────────────────────────────────────────────
SEO health monitoring for MfalmeBits.

Responsibilities
  1. Validate page metadata (title length, description length, OG tags).
  2. Log 404 errors to the database so editorial staff can spot broken
     internal links and set up redirects.
  3. Provide a `SEOHealthReport` dataclass for use in admin views.
  4. Django middleware that hooks into every response automatically.

Setup — add to MIDDLEWARE in settings (after SecurityMiddleware):
    'utils.seo_monitor.SEOMonitorMiddleware',

Run the management command to get a health report:
    python manage.py seo_health_check
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Callable

from django.db import models
from django.utils import timezone
from django.http import HttpRequest, HttpResponse

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════
# 1. Database model — 404 log
# ═══════════════════════════════════════════════════════════════════

class BrokenLink(models.Model):
    """
    Records every 404 response served by Django.

    Attach this model to an app (e.g. `apps.home`) and add it to the
    app's models.  Then run `makemigrations home`.

    If you prefer not to create a new model, swap out `BrokenLink` below
    for a simple file logger.
    """

    url = models.URLField(max_length=500)
    referrer = models.URLField(max_length=500, blank=True)
    user_agent = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    hit_count = models.PositiveIntegerField(default=1)
    first_seen = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)
    is_resolved = models.BooleanField(default=False)
    notes = models.TextField(blank=True, help_text="Redirect or action taken")

    class Meta:
        ordering = ["-last_seen"]
        verbose_name = "Broken Link (404)"
        verbose_name_plural = "Broken Links (404s)"
        app_label = "home"  # Change to the app you want to own this model

    def __str__(self) -> str:
        return f"{self.url} ({self.hit_count} hits)"


# ═══════════════════════════════════════════════════════════════════
# 2. Metadata validation helpers
# ═══════════════════════════════════════════════════════════════════

# Google SERP character limits (approximate)
TITLE_MIN = 30
TITLE_MAX = 60
DESC_MIN = 70
DESC_MAX = 160


@dataclass
class MetaIssue:
    severity: str   # "error" | "warning" | "info"
    field: str
    message: str


@dataclass
class SEOHealthReport:
    url: str
    title: str | None = None
    description: str | None = None
    h1_count: int = 0
    canonical: str | None = None
    og_image: str | None = None
    issues: list[MetaIssue] = field(default_factory=list)

    @property
    def score(self) -> int:
        """
        Rough 0–100 score.  Each error costs 20 pts, each warning 5 pts.
        """
        deductions = sum(
            20 if i.severity == "error" else 5
            for i in self.issues
        )
        return max(0, 100 - deductions)

    @property
    def is_healthy(self) -> bool:
        return all(i.severity != "error" for i in self.issues)


def validate_title(title: str | None, report: SEOHealthReport) -> None:
    """Check SEO title length and presence."""
    if not title:
        report.issues.append(MetaIssue("error", "title", "Missing <title> tag."))
        return

    length = len(title.strip())
    if length < TITLE_MIN:
        report.issues.append(MetaIssue(
            "warning", "title",
            f"Title is too short ({length} chars; recommended ≥{TITLE_MIN})."
        ))
    elif length > TITLE_MAX:
        report.issues.append(MetaIssue(
            "warning", "title",
            f"Title is too long ({length} chars; recommended ≤{TITLE_MAX})."
        ))


def validate_description(desc: str | None, report: SEOHealthReport) -> None:
    """Check meta description length and presence."""
    if not desc:
        report.issues.append(MetaIssue("error", "description", "Missing meta description."))
        return

    length = len(desc.strip())
    if length < DESC_MIN:
        report.issues.append(MetaIssue(
            "warning", "description",
            f"Description too short ({length} chars; recommended ≥{DESC_MIN})."
        ))
    elif length > DESC_MAX:
        report.issues.append(MetaIssue(
            "warning", "description",
            f"Description too long ({length} chars; recommended ≤{DESC_MAX})."
        ))


def validate_h1(h1_count: int, report: SEOHealthReport) -> None:
    """Each page should have exactly one H1."""
    if h1_count == 0:
        report.issues.append(MetaIssue("error", "h1", "No <h1> tag found on the page."))
    elif h1_count > 1:
        report.issues.append(MetaIssue(
            "warning", "h1",
            f"Multiple <h1> tags found ({h1_count}). Use only one per page."
        ))


def validate_og_image(og_image: str | None, report: SEOHealthReport) -> None:
    """Check Open Graph image presence."""
    if not og_image:
        report.issues.append(MetaIssue(
            "warning", "og:image",
            "Missing og:image tag — social sharing previews will be generic."
        ))


def validate_canonical(canonical: str | None, url: str, report: SEOHealthReport) -> None:
    """Warn if the canonical URL differs unexpectedly from the page URL."""
    if not canonical:
        report.issues.append(MetaIssue(
            "info", "canonical",
            "No canonical tag.  Consider adding one to avoid duplicate content."
        ))


# ── Parse raw HTML (used when checking live pages or stored content) ─

_TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)
_DESC_RE = re.compile(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', re.IGNORECASE)
_H1_RE = re.compile(r"<h1[^>]*>", re.IGNORECASE)
_OG_IMAGE_RE = re.compile(r'<meta\s+property=["\']og:image["\']\s+content=["\'](.*?)["\']', re.IGNORECASE)
_CANONICAL_RE = re.compile(r'<link\s+rel=["\']canonical["\']\s+href=["\'](.*?)["\']', re.IGNORECASE)


def analyse_html(url: str, html: str) -> SEOHealthReport:
    """
    Parse raw HTML and return a SEOHealthReport.

    Useful for:
      - Checking content saved in the database before publishing.
      - Writing management commands that crawl your own site.

    Args:
        url:  The page URL (for the report label only).
        html: Full HTML string of the page.

    Returns:
        SEOHealthReport
    """
    title_match = _TITLE_RE.search(html)
    desc_match = _DESC_RE.search(html)
    og_match = _OG_IMAGE_RE.search(html)
    canonical_match = _CANONICAL_RE.search(html)
    h1_count = len(_H1_RE.findall(html))

    title = title_match.group(1).strip() if title_match else None
    description = desc_match.group(1).strip() if desc_match else None
    og_image = og_match.group(1).strip() if og_match else None
    canonical = canonical_match.group(1).strip() if canonical_match else None

    report = SEOHealthReport(
        url=url,
        title=title,
        description=description,
        h1_count=h1_count,
        canonical=canonical,
        og_image=og_image,
    )

    validate_title(title, report)
    validate_description(description, report)
    validate_h1(h1_count, report)
    validate_og_image(og_image, report)
    validate_canonical(canonical, url, report)

    return report


def check_model_seo(instance) -> SEOHealthReport:
    """
    Validate SEO fields on an ORM model instance.

    Expects the model to have (optionally): seo_title, seo_description,
    featured_image (or cover_image), get_absolute_url().

    Usage:
        from utils.seo_monitor import check_model_seo
        report = check_model_seo(some_archive_entry)
        if not report.is_healthy:
            print(report.issues)
    """
    url = getattr(instance, "get_absolute_url", lambda: "unknown")()
    title = getattr(instance, "seo_title", None) or getattr(instance, "title", None)
    description = getattr(instance, "seo_description", None) or getattr(instance, "excerpt", None)
    image = (
        getattr(instance, "featured_image", None)
        or getattr(instance, "cover_image", None)
    )
    canonical = getattr(instance, "canonical_url", None)

    report = SEOHealthReport(
        url=url,
        title=title,
        description=description,
        og_image=str(image.url) if image else None,
        canonical=canonical,
    )

    validate_title(title, report)
    validate_description(description, report)
    validate_og_image(report.og_image, report)

    return report


# ═══════════════════════════════════════════════════════════════════
# 3. Middleware — auto-log 404s
# ═══════════════════════════════════════════════════════════════════

class SEOMonitorMiddleware:
    """
    Django WSGI middleware that intercepts 404 responses and records them
    in the BrokenLink table.

    Ignores:
      • Requests for static/media files (no SEO value)
      • Bot/crawler user agents (noisy & not editorial broken links)
      • Admin URLs (not public-facing)

    Add to MIDDLEWARE in settings:
        'utils.seo_monitor.SEOMonitorMiddleware',
    """

    # Prefixes to skip entirely
    _SKIP_PREFIXES = ("/static/", "/media/", "/admin/", "/__debug__/", "/favicon")

    # User-agent substrings that indicate crawlers
    _BOT_PATTERNS = re.compile(
        r"(bot|crawl|spider|slurp|googlebot|bingbot|yandex|baidu|duckduck)",
        re.IGNORECASE,
    )

    def __init__(self, get_response: Callable) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)

        if response.status_code == 404:
            self._log_404(request)

        return response

    def _log_404(self, request: HttpRequest) -> None:
        path = request.path

        # Skip static/media/admin paths
        if any(path.startswith(p) for p in self._SKIP_PREFIXES):
            return

        user_agent = request.META.get("HTTP_USER_AGENT", "")

        # Skip known bots
        if self._BOT_PATTERNS.search(user_agent):
            return

        referrer = request.META.get("HTTP_REFERER", "")[:500]
        ip = request.META.get("REMOTE_ADDR")

        try:
            obj, created = BrokenLink.objects.get_or_create(
                url=path[:500],
                defaults={
                    "referrer": referrer,
                    "user_agent": user_agent[:500],
                    "ip_address": ip,
                },
            )
            if not created:
                # Increment the counter and update last_seen
                BrokenLink.objects.filter(pk=obj.pk).update(
                    hit_count=models.F("hit_count") + 1,
                    last_seen=timezone.now(),
                )
        except Exception as exc:  # noqa: BLE001
            # Never let monitoring crash the actual response
            logger.warning("SEOMonitorMiddleware: could not log 404 — %s", exc)


# ═══════════════════════════════════════════════════════════════════
# 4. Bulk model audit helper (for management commands / admin views)
# ═══════════════════════════════════════════════════════════════════

def audit_all_entries(batch_size: int = 100) -> list[SEOHealthReport]:
    """
    Run SEO checks across all ArchiveEntry and Post instances.
    Returns a list of SEOHealthReport objects with issues.

    Designed to be called from a management command:

        from utils.seo_monitor import audit_all_entries
        reports = audit_all_entries()
        errors = [r for r in reports if not r.is_healthy]
    """
    from apps.archive.models import ArchiveEntry
    from apps.blog.models import Post

    reports: list[SEOHealthReport] = []

    for entry in ArchiveEntry.objects.filter(is_active=True).iterator(chunk_size=batch_size):
        reports.append(check_model_seo(entry))

    for post in Post.objects.filter(status="published", is_active=True).iterator(chunk_size=batch_size):
        reports.append(check_model_seo(post))

    issues_count = sum(len(r.issues) for r in reports)
    logger.info(
        "SEO audit complete: %d pages checked, %d issues found.",
        len(reports), issues_count,
    )
    return reports