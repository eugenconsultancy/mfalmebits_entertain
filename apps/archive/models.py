from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from taggit.managers import TaggableManager
from ckeditor.fields import RichTextField
from utils.seo import SEOMetaGenerator
from utils.slug_utils import generate_seo_slug
from utils.image_optimizer import optimize_uploaded_image
import os

class Theme(models.Model):
    """Knowledge themes/categories"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    icon = models.CharField(max_length=50, help_text="FontAwesome icon class")
    color = models.CharField(max_length=20, help_text="Theme color in hex", default="#8B4513")
    featured_image = models.ImageField(upload_to='archive/themes/', blank=True, null=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    # SEO Fields
    seo_title = models.CharField(max_length=60, blank=True)
    seo_description = models.CharField(max_length=160, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_seo_slug(self.name, Theme)
        if not self.seo_title:
            self.seo_title = SEOMetaGenerator.generate_title(self)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('archive:by_theme', args=[self.slug])
    
    def get_entry_count(self):
        return self.archiveentry_set.filter(is_active=True).count()

class ArchiveEntry(models.Model):
    """Individual archive entries"""
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=250)
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE)
    
    # Content
    content = RichTextField()
    excerpt = models.TextField(max_length=300, help_text="Short summary for listings")
    
    # Media
    featured_image = models.ImageField(upload_to='archive/entries/')
    image_alt = models.CharField(max_length=100, blank=True)
    document = models.FileField(upload_to='archive/documents/', blank=True, null=True)
    document_type = models.CharField(max_length=20, blank=True, choices=[
        ('pdf', 'PDF'),
        ('epub', 'EPUB'),
        ('doc', 'Word Document'),
        ('txt', 'Text File'),
        ('audio', 'Audio'),
        ('video', 'Video'),
    ])
    
    # Metadata
    author = models.CharField(max_length=100)
    author_bio = models.TextField(blank=True)
    published_date = models.DateTimeField()
    updated_date = models.DateTimeField(auto_now=True)
    
    # Categorization
    tags = TaggableManager()
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    views_count = models.IntegerField(default=0)
    download_count = models.IntegerField(default=0)
    
    # SEO Fields
    seo_title = models.CharField(max_length=60, blank=True)
    seo_description = models.CharField(max_length=160, blank=True)
    canonical_url = models.URLField(blank=True, help_text="Override default canonical URL")
    
    # References
    references = models.TextField(blank=True, help_text="Sources and references")
    citation_text = models.TextField(blank=True, help_text="How to cite this entry")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Archive entries"
        ordering = ['-published_date']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['theme', '-published_date']),
            models.Index(fields=['is_featured']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_seo_slug(self.title, ArchiveEntry)
        if not self.seo_title:
            self.seo_title = SEOMetaGenerator.generate_title(self)
        if not self.image_alt and self.featured_image:
            self.image_alt = f"{self.title} - MfalmeBits Archive"
        
        # Optimize images on save
        if self.featured_image and not self.featured_image.name.endswith('.webp'):
            try:
                optimize_uploaded_image(self.featured_image)
            except Exception as e:
                print(f"Image optimization failed: {e}")
        
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('archive:detail', args=[self.theme.slug, self.slug])
    
    def get_canonical_url(self):
        return self.canonical_url or self.get_absolute_url()
    
    def increment_views(self):
        self.views_count += 1
        self.save(update_fields=['views_count'])
    
    def get_reading_time(self):
        """Calculate estimated reading time in minutes"""
        word_count = len(self.content.split())
        minutes = max(1, round(word_count / 200))  # 200 words per minute
        return minutes
    
    def get_citation(self, format='apa'):
        """Generate citation in specified format"""
        if self.citation_text:
            return self.citation_text
        
        if format == 'apa':
            return f"{self.author}. ({self.published_date.year}). {self.title}. MfalmeBits Knowledge Archive."
        elif format == 'mla':
            return f"{self.author}. \"{self.title}.\" MfalmeBits Knowledge Archive, {self.published_date.year}."
        elif format == 'chicago':
            return f"{self.author}. \"{self.title}.\" MfalmeBits Knowledge Archive. Accessed {self.published_date.strftime('%B %d, %Y')}."
        
        return self.citation_text

class ArchiveImage(models.Model):
    """Additional images for archive entries"""
    entry = models.ForeignKey(ArchiveEntry, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='archive/entries/gallery/')
    caption = models.CharField(max_length=200, blank=True)
    alt_text = models.CharField(max_length=100)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"Image for {self.entry.title}"
    
    def save(self, *args, **kwargs):
        if not self.alt_text and self.caption:
            self.alt_text = self.caption
        super().save(*args, **kwargs)

class ArchiveDownload(models.Model):
    """Track document downloads"""
    entry = models.ForeignKey(ArchiveEntry, on_delete=models.CASCADE)
    user = models.ForeignKey('auth.User', null=True, blank=True, on_delete=models.SET_NULL)
    ip_address = models.GenericIPAddressField()
    downloaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-downloaded_at']
    
    def __str__(self):
        return f"Download of {self.entry.title} at {self.downloaded_at}"
