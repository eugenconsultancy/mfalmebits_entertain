from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from apps.archive.models import ArchiveEntry
from apps.blog.models import Post
from apps.library.models import DigitalProduct

class StaticViewSitemap(Sitemap):
    """Sitemap for static pages"""
    priority = 0.8
    changefreq = 'weekly'
    
    def items(self):
        return [
            'home:home',
            'about:index', 
            'contact:index',
            'archive:index',
            'library:index',
            'blog:index'
        ]
    
    def location(self, item):
        return reverse(item)


class ArchiveSitemap(Sitemap):
    """Sitemap for archive entries"""
    changefreq = 'monthly'
    priority = 0.7
    
    def items(self):
        return ArchiveEntry.objects.filter(is_active=True)
    
    def lastmod(self, obj):
        return obj.updated_at if hasattr(obj, 'updated_at') else obj.created_at
    
    def location(self, obj):
        return obj.get_absolute_url()


class BlogSitemap(Sitemap):
    """Sitemap for blog posts"""
    changefreq = 'weekly'
    priority = 0.6
    
    def items(self):
        return Post.objects.filter(status='published', is_active=True)
    
    def lastmod(self, obj):
        return obj.updated_date if hasattr(obj, 'updated_date') else obj.created_at
    
    def location(self, obj):
        return obj.get_absolute_url()


class LibrarySitemap(Sitemap):
    """Sitemap for digital products"""
    changefreq = 'monthly'
    priority = 0.6
    
    def items(self):
        return DigitalProduct.objects.filter(is_active=True)
    
    def lastmod(self, obj):
        return obj.updated_at
    
    def location(self, obj):
        return obj.get_absolute_url()