from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
from taggit.managers import TaggableManager
from ckeditor.fields import RichTextField
from utils.seo import SEOMetaGenerator
from utils.slug_utils import generate_seo_slug
import uuid

class Category(models.Model):
    """Blog post categories"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='blog/categories/', blank=True, null=True)
    color = models.CharField(max_length=20, default='#8B4513', help_text="Hex color code")
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    # SEO Fields
    seo_title = models.CharField(max_length=60, blank=True)
    seo_description = models.CharField(max_length=160, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_seo_slug(self.name, Category)
        if not self.seo_title:
            self.seo_title = SEOMetaGenerator.generate_title(self)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('blog:category', args=[self.slug])
    
    def get_post_count(self):
        return self.post_set.filter(is_active=True).count()


class Post(models.Model):
    """Blog posts"""
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    )
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=250)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Content
    content = RichTextField()
    excerpt = models.TextField(max_length=300, help_text="Short summary for listings")
    
    # Media
    featured_image = models.ImageField(upload_to='blog/posts/')
    image_alt = models.CharField(max_length=100, blank=True)
    image_caption = models.CharField(max_length=200, blank=True)
    
    # Video (optional)
    video_url = models.URLField(blank=True, help_text="YouTube or Vimeo URL")
    
    # Metadata
    tags = TaggableManager()
    views_count = models.IntegerField(default=0)
    reading_time = models.IntegerField(default=0, help_text="Reading time in minutes")
    
    # Dates
    published_date = models.DateTimeField(default=timezone.now)
    updated_date = models.DateTimeField(auto_now=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    allow_comments = models.BooleanField(default=True)
    
    # SEO Fields
    seo_title = models.CharField(max_length=60, blank=True)
    seo_description = models.CharField(max_length=160, blank=True)
    canonical_url = models.URLField(blank=True, help_text="Override default canonical URL")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-published_date']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['-published_date', 'status']),
            models.Index(fields=['author', '-published_date']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_seo_slug(self.title, Post)
        if not self.seo_title:
            self.seo_title = SEOMetaGenerator.generate_title(self)
        if not self.image_alt and self.featured_image:
            self.image_alt = f"{self.title} - MfalmeBits Blog"
        
        # Calculate reading time if not set
        if not self.reading_time:
            word_count = len(self.content.split())
            self.reading_time = max(1, round(word_count / 200))  # 200 words per minute
        
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('blog:detail', args=[
            self.published_date.year,
            self.published_date.strftime('%m'),
            self.slug
        ])
    
    def get_canonical_url(self):
        return self.canonical_url or self.get_absolute_url()
    
    def increment_views(self):
        self.views_count += 1
        self.save(update_fields=['views_count'])
    
    def get_previous_post(self):
        return Post.objects.filter(
            published_date__lt=self.published_date,
            status='published',
            is_active=True
        ).order_by('-published_date').first()
    
    def get_next_post(self):
        return Post.objects.filter(
            published_date__gt=self.published_date,
            status='published',
            is_active=True
        ).order_by('published_date').first()


class Comment(models.Model):
    """Blog comments"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    # Commenter info
    name = models.CharField(max_length=100)
    email = models.EmailField()
    website = models.URLField(blank=True)
    
    # Comment content
    content = models.TextField()
    
    # Moderation
    is_approved = models.BooleanField(default=False)
    is_spam = models.BooleanField(default=False)
    
    # Metadata
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['post', '-created_at']),
            models.Index(fields=['is_approved', '-created_at']),
        ]
    
    def __str__(self):
        return f"Comment by {self.name} on {self.post.title}"
    
    def get_replies(self):
        return self.replies.filter(is_approved=True)


class Series(models.Model):
    """Blog post series"""
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = RichTextField()
    image = models.ImageField(upload_to='blog/series/', blank=True, null=True)
    posts = models.ManyToManyField(Post, related_name='series', blank=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Series"
        ordering = ['order', 'title']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_seo_slug(self.title, Series)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('blog:series', args=[self.slug])


class NewsletterSubscription(models.Model):
    """Blog newsletter subscribers"""
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    unsubscribed_at = models.DateTimeField(null=True, blank=True)
    
    # Source tracking
    source = models.CharField(max_length=50, default='blog')
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    
    class Meta:
        ordering = ['-subscribed_at']
    
    def __str__(self):
        return self.email


class Author(models.Model):
    """Extended author information"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = RichTextField(blank=True)
    avatar = models.ImageField(upload_to='blog/authors/', blank=True, null=True)
    position = models.CharField(max_length=100, blank=True)
    
    # Social media
    twitter = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    website = models.URLField(blank=True)
    
    # Settings
    show_on_about = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'user__first_name']
    
    def __str__(self):
        return self.user.get_full_name() or self.user.username
    
    def get_absolute_url(self):
        return reverse('blog:author', args=[self.user.username])


class BlogSettings(models.Model):
    """Global blog settings"""
    posts_per_page = models.IntegerField(default=10)
    comments_per_page = models.IntegerField(default=20)
    moderate_comments = models.BooleanField(default=True)
    allow_guest_comments = models.BooleanField(default=True)
    notify_on_comments = models.BooleanField(default=True)
    comment_notification_email = models.EmailField(blank=True)
    
    # Social sharing
    twitter_handle = models.CharField(max_length=50, blank=True)
    facebook_page = models.URLField(blank=True)
    instagram_handle = models.CharField(max_length=50, blank=True)
    
    # SEO
    blog_title = models.CharField(max_length=200, default="MfalmeBits Blog")
    blog_description = models.CharField(max_length=300, default="News, updates, and insights from MfalmeBits")
    blog_keywords = models.CharField(max_length=300, blank=True)
    
    class Meta:
        verbose_name_plural = "Blog settings"
    
    def __str__(self):
        return "Blog Settings"
    
    def save(self, *args, **kwargs):
        # Ensure only one settings instance exists
        if not self.pk and BlogSettings.objects.exists():
            return
        super().save(*args, **kwargs)
