"""
core/urls.py
─────────────────────────────────────────────────────────────────────
Main URL configuration for MfalmeBits.

Robots.txt fix
--------------
The `django-robots` package (PyPI: robots) still ships code that uses
Python 2 syntax (`print` statements, `unicode` built-in) and will cause
an ImportError on Python 3.10+.

Fix: Remove `robots` from INSTALLED_APPS entirely and serve robots.txt
via a simple TemplateView.  Place your robots.txt content in:

    templates/robots.txt

Example templates/robots.txt:
    User-agent: *
    Allow: /
    Disallow: /admin/
    Disallow: /accounts/
    Sitemap: https://mfalmebits.com/sitemap.xml
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView

from .sitemaps import (
    StaticViewSitemap,
    ArchiveSitemap,
    BlogSitemap,
    LibrarySitemap,
)

# ── Sitemaps registry ─────────────────────────────────────────────────
sitemaps = {
    "static": StaticViewSitemap,
    "archive": ArchiveSitemap,
    "blog": BlogSitemap,
    "library": LibrarySitemap,
}


# ── Inline robots.txt view (no extra package needed) ─────────────────
def robots_txt(request):
    """
    Serve robots.txt from the template `templates/robots.txt`.

    If you prefer a hardcoded response instead of a template, replace
    the function body with:

        lines = [
            "User-agent: *",
            "Allow: /",
            "Disallow: /admin/",
            f"Sitemap: {request.build_absolute_uri('/sitemap.xml')}",
        ]
        return HttpResponse("\n".join(lines), content_type="text/plain")
    """
    from django.template.loader import render_to_string

    content = render_to_string(
        "robots.txt",
        {
            "sitemap_url": request.build_absolute_uri("/sitemap.xml"),
            "request": request,
        },
    )
    return HttpResponse(content, content_type="text/plain; charset=utf-8")


# ── URL patterns ──────────────────────────────────────────────────────
urlpatterns = [
    # ── Admin ─────────────────────────────────────────────────────────
    path("admin/", admin.site.urls),

    # ── SEO ───────────────────────────────────────────────────────────
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    # robots.txt — no external package needed
    path("robots.txt", robots_txt, name="robots_txt"),

    # ── Core apps ─────────────────────────────────────────────────────
    path("", include("apps.home.urls")),
    path("archive/", include("apps.archive.urls")),
    path("library/", include("apps.library.urls")),
    path("institutional/", include("apps.institutional.urls")),
    path("collaboration/", include("apps.collaboration.urls")),
    path("blog/", include("apps.blog.urls")),
    path("about/", include("apps.about.urls")),
    path("contact/", include("apps.contact.urls")),
    path("newsletter/", include("apps.newsletter.urls")),
    path("accounts/", include("apps.accounts.urls")),

    # ── CKEditor 5 file uploads ────────────────────────────────────────
    path("ckeditor5/", include("django_ckeditor_5.urls")),

    # ── Convenience redirects (keep old bookmark URLs working) ────────
    path("login/", RedirectView.as_view(url="/accounts/login/", permanent=False)),
    path("logout/", RedirectView.as_view(url="/accounts/logout/", permanent=False)),
    path("register/", RedirectView.as_view(url="/accounts/register/", permanent=False)),
    path("signup/", RedirectView.as_view(url="/accounts/register/", permanent=False)),
    path("profile/", RedirectView.as_view(url="/accounts/profile/", permanent=False)),
    path("dashboard/", RedirectView.as_view(url="/accounts/dashboard/", permanent=False)),
]

# ── Development-only extras ───────────────────────────────────────────
if settings.DEBUG:
    try:
        import debug_toolbar
        urlpatterns += [path("__debug__/", include(debug_toolbar.urls))]
    except ImportError:
        pass

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)