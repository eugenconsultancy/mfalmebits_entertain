from django.db import models
from django.urls import reverse
from django_ckeditor_5.fields import CKEditor5Field
from utils.seo import SEOMetaGenerator
from utils.slug_utils import generate_seo_slug

class AboutSection(models.Model):
    """Dynamic about page sections"""
    SECTION_TYPES = (
        ('hero', 'Hero Section'),
        ('mission', 'Mission & Vision'),
        ('story', 'Our Story'),
        ('values', 'Core Values'),
        ('team', 'Team'),
        ('timeline', 'Timeline'),
        ('achievements', 'Achievements'),
    )
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    section_type = models.CharField(max_length=20, choices=SECTION_TYPES)
    
    # Updated to CKEditor5Field
    content = CKEditor5Field('Content', config_name='extends')
    
    image = models.ImageField(upload_to='about/sections/', blank=True, null=True)
    image_alt = models.CharField(max_length=100, blank=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    # SEO Fields
    seo_title = models.CharField(max_length=60, blank=True)
    seo_description = models.CharField(max_length=160, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'section_type']
    
    def __str__(self):
        return f"{self.get_section_type_display()}: {self.title}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            # Note: Ensure generate_seo_slug is imported
            self.slug = generate_seo_slug(self.title, AboutSection)
        if not self.seo_title:
            # Note: Ensure SEOMetaGenerator is imported
            self.seo_title = SEOMetaGenerator.generate_title(self)
        super().save(*args, **kwargs)


class TeamMember(models.Model):
    """Team members"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    position = models.CharField(max_length=100)
    
    # Updated to CKEditor5Field
    bio = CKEditor5Field('Bio', config_name='extends')
    
    # Image
    photo = models.ImageField(upload_to='about/team/', blank=True, null=True)
    photo_alt = models.CharField(max_length=100, blank=True)
    
    # Social Media
    email = models.EmailField(blank=True)
    twitter = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    github = models.URLField(blank=True)
    website = models.URLField(blank=True)
    
    # Order
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_leadership = models.BooleanField(default=False)
    is_founder = models.BooleanField(default=False)
    
    # Metadata
    joined_date = models.DateField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_founder', '-is_leadership', 'order', 'name']
    
    def __str__(self):
        return f"{self.name} - {self.position}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_seo_slug(self.name, TeamMember)
        if not self.photo_alt and self.photo:
            self.photo_alt = f"{self.name} - {self.position}"
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('about:team_detail', args=[self.slug])


class Timeline(models.Model):
    """Company timeline/ history"""
    year = models.CharField(max_length=20)
    title = models.CharField(max_length=200)
    
    # Updated to CKEditor5Field
    description = CKEditor5Field('Description', config_name='extends')
    
    image = models.ImageField(upload_to='about/timeline/', blank=True, null=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'year']
    
    def __str__(self):
        return f"{self.year}: {self.title}"


class Achievement(models.Model):
    """Company achievements and milestones"""
    title = models.CharField(max_length=200)
    value = models.CharField(max_length=100, help_text="e.g., '50,000+', '100+'")
    description = models.TextField()
    icon = models.CharField(max_length=50, help_text="FontAwesome icon class")
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.title


class Value(models.Model):
    """Core values"""
    title = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50, help_text="FontAwesome icon class")
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.title


class Partner(models.Model):
    """Partners and collaborators"""
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='about/partners/')
    website = models.URLField()
    description = models.TextField(blank=True)
    partner_type = models.CharField(max_length=50, choices=[
        ('cultural', 'Cultural Institution'),
        ('academic', 'Academic Institution'),
        ('corporate', 'Corporate Partner'),
        ('ngo', 'Non-Profit'),
        ('media', 'Media Partner'),
    ])
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name


class Testimonial(models.Model):
    """About page testimonials"""
    author_name = models.CharField(max_length=100)
    author_title = models.CharField(max_length=100, blank=True)
    author_organization = models.CharField(max_length=100, blank=True)
    author_image = models.ImageField(upload_to='about/testimonials/', blank=True, null=True)
    content = models.TextField()
    rating = models.IntegerField(default=5, choices=[(i, i) for i in range(1, 6)])
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', '-created_at']
    
    def __str__(self):
        return f"Testimonial from {self.author_name}"


class AboutSettings(models.Model):
    """Global about page settings"""
    company_name = models.CharField(max_length=200, default="MfalmeBits")
    tagline = models.CharField(max_length=200, blank=True)
    founded_year = models.IntegerField(null=True, blank=True)
    headquarters = models.CharField(max_length=200, blank=True)
    
    # Contact
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    
    # Social Media
    facebook = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    youtube = models.URLField(blank=True)
    
    # SEO
    meta_title = models.CharField(max_length=60, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)
    meta_keywords = models.CharField(max_length=200, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "About settings"
    
    def __str__(self):
        return "About Settings"
    
    def save(self, *args, **kwargs):
        if not self.pk and AboutSettings.objects.exists():
            return
        super().save(*args, **kwargs)
