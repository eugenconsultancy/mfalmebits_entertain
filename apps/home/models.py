from django.db import models
from django.utils.text import slugify
from utils.seo import SEOMetaGenerator

class HomeSection(models.Model):
    """Dynamic sections for homepage"""
    SECTION_TYPES = (
        ('hero', 'Hero Section'),
        ('featured', 'Featured Content'),
        ('categories', 'Categories Grid'),
        ('testimonials', 'Testimonials'),
        ('cta', 'Call to Action'),
        ('partners', 'Partners'),
    )
    
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300, blank=True)
    section_type = models.CharField(max_length=20, choices=SECTION_TYPES)
    content = models.TextField(blank=True)
    background_image = models.ImageField(upload_to='home/sections/', blank=True, null=True)
    background_color = models.CharField(max_length=20, blank=True, help_text="Hex color code")
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    # SEO Fields
    seo_title = models.CharField(max_length=60, blank=True)
    seo_description = models.CharField(max_length=160, blank=True)
    
    # Animation Settings
    animation_type = models.CharField(max_length=50, default='fade-up')
    animation_delay = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', '-created_at']
    
    def __str__(self):
        return f"{self.get_section_type_display()}: {self.title}"
    
    def save(self, *args, **kwargs):
        if not self.seo_title:
            self.seo_title = SEOMetaGenerator.generate_title(self)
        super().save(*args, **kwargs)

class HeroSlide(models.Model):
    """Carousel slides for hero section"""
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='home/hero/')
    image_alt = models.CharField(max_length=100)
    button_text = models.CharField(max_length=50, blank=True)
    button_url = models.CharField(max_length=200, blank=True)
    button_style = models.CharField(max_length=50, default='primary')
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    # Animation
    animation_duration = models.IntegerField(default=5000)  # milliseconds
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.title

class FeaturedItem(models.Model):
    """Featured content items"""
    ITEM_TYPES = (
        ('archive', 'Archive Entry'),
        ('product', 'Digital Product'),
        ('blog', 'Blog Post'),
        ('external', 'External Link'),
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='home/featured/')
    image_alt = models.CharField(max_length=100)
    item_type = models.CharField(max_length=20, choices=ITEM_TYPES)
    content_id = models.IntegerField(help_text="ID of the content item", null=True, blank=True)
    external_url = models.URLField(blank=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        if self.item_type == 'archive' and self.content_id:
            from apps.archive.models import ArchiveEntry
            try:
                entry = ArchiveEntry.objects.get(id=self.content_id)
                return entry.get_absolute_url()
            except ArchiveEntry.DoesNotExist:
                return '#'
        elif self.item_type == 'product' and self.content_id:
            from apps.library.models import DigitalProduct
            try:
                product = DigitalProduct.objects.get(id=self.content_id)
                return product.get_absolute_url()
            except DigitalProduct.DoesNotExist:
                return '#'
        elif self.item_type == 'blog' and self.content_id:
            from apps.blog.models import Post
            try:
                post = Post.objects.get(id=self.content_id)
                return post.get_absolute_url()
            except Post.DoesNotExist:
                return '#'
        elif self.external_url:
            return self.external_url
        return '#'

class Testimonial(models.Model):
    """Customer testimonials"""
    name = models.CharField(max_length=100)
    title = models.CharField(max_length=100, blank=True)
    company = models.CharField(max_length=100, blank=True)
    avatar = models.ImageField(upload_to='home/testimonials/', blank=True, null=True)
    content = models.TextField()
    rating = models.IntegerField(default=5, choices=[(i, i) for i in range(1, 6)])
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.name} - {self.rating} stars"

class Partner(models.Model):
    """Partner organizations"""
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='home/partners/')
    website_url = models.URLField()
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.name

class CTASection(models.Model):
    """Call to Action sections"""
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300, blank=True)
    description = models.TextField(blank=True)
    background_image = models.ImageField(upload_to='home/cta/', blank=True, null=True)
    background_color = models.CharField(max_length=20, blank=True)
    button_text = models.CharField(max_length=50)
    button_url = models.CharField(max_length=200)
    button_style = models.CharField(max_length=50, default='primary')
    secondary_button_text = models.CharField(max_length=50, blank=True)
    secondary_button_url = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
