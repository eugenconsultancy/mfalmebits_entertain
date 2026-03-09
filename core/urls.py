"""
Main URL configuration for MfalmeBits project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.views.generic.base import TemplateView

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
    path('accounts/', include('apps.accounts.urls')),
    path('newsletter/', include('apps.newsletter.urls')),
    
    # Authentication
    path('accounts/', include('allauth.urls')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
]

# Debug toolbar
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
