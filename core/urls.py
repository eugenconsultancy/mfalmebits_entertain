"""
Main URL configuration for MfalmeBits project.
"""

from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.views.generic.base import TemplateView, RedirectView

# Import sitemaps
from .sitemaps import (
    StaticViewSitemap, ArchiveSitemap, 
    BlogSitemap, LibrarySitemap
)

sitemaps = {
    'static': StaticViewSitemap,
    'archive': ArchiveSitemap,
    'blog': BlogSitemap,
    'library': LibrarySitemap,
}

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # ===== ADDED: Admin Tools URLs (required for dashboard preferences) =====
    path('admin_tools/', include('admin_tools.urls')),
    
    # SEO URLs
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, 
         name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', TemplateView.as_view(
        template_name='robots.txt', content_type='text/plain')),
    
    # Apps
    path('', include('apps.home.urls')),
    path('archive/', include('apps.archive.urls')),
    path('library/', include('apps.library.urls')),
    path('institutional/', include('apps.institutional.urls')),
    path('collaboration/', include('apps.collaboration.urls')),
    path('blog/', include('apps.blog.urls')),
    path('about/', include('apps.about.urls')),
    path('contact/', include('apps.contact.urls')),
    path('newsletter/', include('apps.newsletter.urls')),
    
    # ===== FIXED: Accounts URLs (only once) =====
    path('accounts/', include('apps.accounts.urls')),
    
    # CKEditor
    path("ckeditor5/", include('django_ckeditor_5.urls')),
    
    # ===== CONVENIENCE REDIRECTS =====
    # Redirect common URLs to accounts
    path('login/', RedirectView.as_view(url='/accounts/login/', permanent=False)),
    path('logout/', RedirectView.as_view(url='/accounts/logout/', permanent=False)),
    path('register/', RedirectView.as_view(url='/accounts/register/', permanent=False)),
    path('signup/', RedirectView.as_view(url='/accounts/register/', permanent=False)),
    path('profile/', RedirectView.as_view(url='/accounts/profile/', permanent=False)),
    path('dashboard/', RedirectView.as_view(url='/accounts/dashboard/', permanent=False)),
]

# Debug toolbar and media files
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)