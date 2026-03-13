from django.db import models
from django.urls import reverse
from django.core.validators import validate_email
from django.core.mail import send_mail
from django.conf import settings
from django_ckeditor_5.fields import CKEditor5Field
from utils.seo import SEOMetaGenerator
from utils.slug_utils import generate_seo_slug
import uuid

class Subscriber(models.Model):
    """Newsletter subscribers"""
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    
    # Subscription details
    is_active = models.BooleanField(default=True)
    confirmed = models.BooleanField(default=False)
    confirmation_token = models.CharField(max_length=100, blank=True)
    unsubscribe_token = models.CharField(max_length=100, unique=True)
    
    # Preferences
    frequency = models.CharField(max_length=20, default='weekly', choices=[
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ])
    
    # Interests (categories they're interested in)
    interests = models.JSONField(default=list, blank=True)
    
    # Source tracking
    source = models.CharField(max_length=50, default='website')
    source_url = models.URLField(blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    
    # Metadata
    subscribed_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    unsubscribed_at = models.DateTimeField(null=True, blank=True)
    last_sent_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-subscribed_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['is_active', 'confirmed']),
        ]
    
    def __str__(self):
        return self.email
    
    def save(self, *args, **kwargs):
        if not self.unsubscribe_token:
            self.unsubscribe_token = str(uuid.uuid4())
        super().save(*args, **kwargs)
    
    def get_full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        return self.email
    
    def generate_confirmation_token(self):
        """Generate email confirmation token"""
        import hashlib
        import time
        token = hashlib.sha256(f"{self.email}{time.time()}{uuid.uuid4()}".encode()).hexdigest()
        self.confirmation_token = token
        self.save(update_fields=['confirmation_token'])
        return token


class NewsletterTemplate(models.Model):
    """Email templates for newsletters"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    
    # Template content
    subject = models.CharField(max_length=200)
    html_content = models.TextField(help_text="HTML email template")
    text_content = models.TextField(blank=True, help_text="Plain text version")
    
    # Preview
    preview_image = models.ImageField(upload_to='newsletter/templates/previews/', blank=True, null=True)
    
    # Settings
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_seo_slug(self.name, NewsletterTemplate)
        super().save(*args, **kwargs)


class NewsletterCampaign(models.Model):
    """Newsletter campaigns"""
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('sending', 'Sending'),
        ('sent', 'Sent'),
        ('cancelled', 'Cancelled'),
    )
    
    FREQUENCY_CHOICES = (
        ('one-time', 'One Time'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    )
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    
    # Content
    subject = models.CharField(max_length=200)
    preview_text = models.CharField(max_length=200, blank=True, help_text="Preview text shown in inbox")
    template = models.ForeignKey(NewsletterTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    html_content = CKEditor5Field('HTML Content', config_name='extends')
    text_content = models.TextField(blank=True)
    
    # Targeting
    target_all_subscribers = models.BooleanField(default=True)
    target_frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, blank=True)
    target_interests = models.JSONField(default=list, blank=True)
    
    # Schedule
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='one-time')
    scheduled_for = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Tracking
    total_recipients = models.IntegerField(default=0)
    sent_count = models.IntegerField(default=0)
    opens_count = models.IntegerField(default=0)
    clicks_count = models.IntegerField(default=0)
    unsubscribes_count = models.IntegerField(default=0)
    bounces_count = models.IntegerField(default=0)
    
    # SEO Fields
    seo_title = models.CharField(max_length=60, blank=True)
    seo_description = models.CharField(max_length=160, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_seo_slug(self.title, NewsletterCampaign)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('newsletter:campaign_detail', args=[self.slug])
    
    def get_recipients(self):
        """Get subscribers for this campaign"""
        subscribers = Subscriber.objects.filter(is_active=True, confirmed=True)
        
        if not self.target_all_subscribers:
            if self.target_frequency:
                subscribers = subscribers.filter(frequency=self.target_frequency)
            if self.target_interests:
                # This is a simplified version - you might want more complex logic
                from django.db.models import Q
                interest_query = Q()
                for interest in self.target_interests:
                    interest_query |= Q(interests__contains=interest)
                subscribers = subscribers.filter(interest_query)
        
        return subscribers
    
    def get_open_rate(self):
        """Calculate open rate percentage"""
        if self.total_recipients > 0:
            return (self.opens_count / self.total_recipients) * 100
        return 0
    
    def get_click_rate(self):
        """Calculate click rate percentage"""
        if self.opens_count > 0:
            return (self.clicks_count / self.opens_count) * 100
        return 0


class NewsletterIssue(models.Model):
    """Individual newsletter issues (sent emails)"""
    campaign = models.ForeignKey(NewsletterCampaign, on_delete=models.CASCADE, related_name='issues')
    issue_number = models.IntegerField()
    subject = models.CharField(max_length=200)
    html_content = models.TextField()
    text_content = models.TextField()
    
    # Recipients
    recipient_count = models.IntegerField(default=0)
    
    # Tracking
    sent_at = models.DateTimeField(auto_now_add=True)
    opens = models.IntegerField(default=0)
    clicks = models.IntegerField(default=0)
    unsubscribes = models.IntegerField(default=0)
    bounces = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-issue_number']
        unique_together = ['campaign', 'issue_number']
    
    def __str__(self):
        return f"{self.campaign.title} - Issue #{self.issue_number}"


class NewsletterLink(models.Model):
    """Track links in newsletters"""
    issue = models.ForeignKey(NewsletterIssue, on_delete=models.CASCADE, related_name='links')
    url = models.URLField()
    text = models.CharField(max_length=200, blank=True)
    click_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-click_count']
    
    def __str__(self):
        return f"{self.url} - {self.click_count} clicks"


class NewsletterTracking(models.Model):
    """Individual tracking events"""
    EVENT_TYPES = (
        ('sent', 'Sent'),
        ('open', 'Opened'),
        ('click', 'Clicked'),
        ('unsubscribe', 'Unsubscribed'),
        ('bounce', 'Bounced'),
    )
    
    issue = models.ForeignKey(NewsletterIssue, on_delete=models.CASCADE, related_name='tracking_events')
    subscriber = models.ForeignKey(Subscriber, on_delete=models.CASCADE)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    
    # For click events
    link = models.ForeignKey(NewsletterLink, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Metadata
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['issue', 'event_type']),
            models.Index(fields=['subscriber', 'event_type']),
        ]
    
    def __str__(self):
        return f"{self.subscriber.email} - {self.event_type} - {self.created_at}"


class NewsletterCategory(models.Model):
    """Categories for newsletter content"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=20, default='#8B4513')
    icon = models.CharField(max_length=50, blank=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name_plural = "Newsletter categories"
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_seo_slug(self.name, NewsletterCategory)
        super().save(*args, **kwargs)


class NewsletterArticle(models.Model):
    """Articles to include in newsletters"""
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(NewsletterCategory, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Content
    excerpt = models.TextField(max_length=300)
    content = CKEditor5Field('Content', config_name='extends')
    
    # Media
    featured_image = models.ImageField(upload_to='newsletter/articles/')
    image_alt = models.CharField(max_length=100, blank=True)
    
    # Metadata
    author = models.CharField(max_length=100, blank=True)
    source_url = models.URLField(blank=True)
    source_name = models.CharField(max_length=100, blank=True)
    
    # Status
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    # Tracking
    views_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_seo_slug(self.title, NewsletterArticle)
        if not self.image_alt and self.featured_image:
            self.image_alt = self.title
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('newsletter:article_detail', args=[self.slug])


class NewsletterSettings(models.Model):
    """Global newsletter settings"""
    # Sender information
    sender_name = models.CharField(max_length=100, default='MfalmeBits Newsletter')
    sender_email = models.EmailField(default='newsletter@mfalmebits.com')
    reply_to = models.EmailField(default='noreply@mfalmebits.com')
    
    # 3. Subscription Settings Model
    # Subscription settings
    require_confirmation = models.BooleanField(default=True)
    double_opt_in = models.BooleanField(default=True)
    welcome_email_subject = models.CharField(max_length=200, default='Welcome to MfalmeBits Newsletter')
    welcome_email_content = CKEditor5Field('Welcome Email Content', config_name='extends', blank=True) # Updated
    
    # Unsubscribe settings
    unsubscribe_landing_page = models.TextField(blank=True)
    
    # API settings
    mailchimp_api_key = models.CharField(max_length=100, blank=True)
    mailchimp_list_id = models.CharField(max_length=100, blank=True)
    sendgrid_api_key = models.CharField(max_length=100, blank=True)
    
    # Rate limiting
    max_emails_per_hour = models.IntegerField(default=100)
    max_emails_per_day = models.IntegerField(default=1000)
    
    # Footer
    footer_text = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Newsletter settings"
    
    def __str__(self):
        return "Newsletter Settings"
    
    def save(self, *args, **kwargs):
        if not self.pk and NewsletterSettings.objects.exists():
            return
        super().save(*args, **kwargs)
