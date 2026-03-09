from django.db import models
from django.urls import reverse
from django.core.validators import RegexValidator
from ckeditor.fields import RichTextField

class ContactMessage(models.Model):
    """Contact form submissions"""
    SUBJECT_CHOICES = (
        ('general', 'General Inquiry'),
        ('support', 'Technical Support'),
        ('sales', 'Sales Question'),
        ('partnership', 'Partnership Opportunity'),
        ('press', 'Press Inquiry'),
        ('feedback', 'Feedback'),
        ('other', 'Other'),
    )
    
    STATUS_CHOICES = (
        ('new', 'New'),
        ('read', 'Read'),
        ('replied', 'Replied'),
        ('archived', 'Archived'),
    )
    
    # Contact Information
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(
        max_length=20, 
        blank=True,
        validators=[RegexValidator(r'^\+?[\d\s-]+$', 'Enter a valid phone number.')]
    )
    
    # Message
    subject_type = models.CharField(max_length=20, choices=SUBJECT_CHOICES, default='general')
    subject = models.CharField(max_length=200)
    message = models.TextField()
    
    # Files
    attachment = models.FileField(
        upload_to='contact/attachments/',
        blank=True,
        null=True,
        help_text="Max 10MB. Allowed: PDF, DOC, DOCX, JPG, PNG"
    )
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    assigned_to = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True, help_text="Internal notes")
    
    # Response tracking
    responded_at = models.DateTimeField(null=True, blank=True)
    response_sent = models.BooleanField(default=False)
    response_message = models.TextField(blank=True)
    
    # Source tracking
    source = models.CharField(max_length=50, default='website')
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    
    # Metadata
    is_subscribed = models.BooleanField(default=False, help_text="Subscribe to newsletter")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['email']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.get_subject_type_display()}: {self.subject[:50]}"
    
    def get_absolute_url(self):
        return reverse('admin:contact_contactmessage_change', args=[self.id])


class FAQ(models.Model):
    """Frequently Asked Questions"""
    CATEGORY_CHOICES = (
        ('general', 'General'),
        ('account', 'Account'),
        ('archive', 'Knowledge Archive'),
        ('library', 'Digital Library'),
        ('institutional', 'Institutional'),
        ('collaboration', 'Collaboration'),
        ('technical', 'Technical'),
    )
    
    question = models.CharField(max_length=200)
    answer = RichTextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general')
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    views_count = models.IntegerField(default=0)
    
    # SEO
    seo_title = models.CharField(max_length=60, blank=True)
    seo_description = models.CharField(max_length=160, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['category', 'order', 'question']
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"
    
    def __str__(self):
        return self.question
    
    def increment_views(self):
        self.views_count += 1
        self.save(update_fields=['views_count'])


class Office(models.Model):
    """Office locations"""
    name = models.CharField(max_length=100, help_text="e.g., Headquarters, Regional Office")
    address = models.TextField()
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20, blank=True)
    
    # Contact
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    
    # Map
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    map_embed_url = models.URLField(blank=True, help_text="Google Maps embed URL")
    
    # Hours
    hours = models.TextField(blank=True, help_text="Business hours")
    
    # Order
    is_headquarters = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-is_headquarters', 'order', 'country', 'city']
    
    def __str__(self):
        return f"{self.name} - {self.city}, {self.country}"


class SupportTicket(models.Model):
    """Customer support tickets"""
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    )
    
    STATUS_CHOICES = (
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('waiting', 'Waiting for Customer'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    )
    
    ticket_id = models.CharField(max_length=20, unique=True)
    user = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Contact info (if not logged in)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    
    # Ticket details
    subject = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=ContactMessage.SUBJECT_CHOICES)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    
    # Attachments
    attachment = models.FileField(upload_to='support/attachments/', blank=True, null=True)
    
    # Assignment
    assigned_to = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tickets')
    
    # Metadata
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-priority', '-created_at']
    
    def __str__(self):
        return f"{self.ticket_id}: {self.subject}"
    
    def save(self, *args, **kwargs):
        if not self.ticket_id:
            # Generate ticket ID: TICKET-YYYYMMDD-XXXX
            import random
            import string
            from django.utils import timezone
            
            date_str = timezone.now().strftime('%Y%m%d')
            random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
            self.ticket_id = f"TKT-{date_str}-{random_str}"
        
        if self.status == 'resolved' and not self.resolved_at:
            from django.utils import timezone
            self.resolved_at = timezone.now()
        
        super().save(*args, **kwargs)


class SupportReply(models.Model):
    """Replies to support tickets"""
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name='replies')
    user = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Reply content
    message = models.TextField()
    attachment = models.FileField(upload_to='support/replies/', blank=True, null=True)
    
    # Internal note (not visible to customer)
    is_internal = models.BooleanField(default=False)
    
    # Metadata
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Reply to {self.ticket.ticket_id} by {self.user or 'System'}"


class ContactSettings(models.Model):
    """Global contact settings"""
    # Email settings
    contact_email = models.EmailField(default='contact@mfalmebits.com')
    support_email = models.EmailField(default='support@mfalmebits.com')
    sales_email = models.EmailField(default='sales@mfalmebits.com')
    
    # Phone numbers
    primary_phone = models.CharField(max_length=20)
    secondary_phone = models.CharField(max_length=20, blank=True)
    
    # Social media
    facebook = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    youtube = models.URLField(blank=True)
    
    # Business hours
    business_hours = models.TextField(blank=True)
    
    # Response times
    general_response_time = models.CharField(max_length=100, default='Within 24 hours')
    support_response_time = models.CharField(max_length=100, default='Within 4 hours')
    
    # reCAPTCHA
    recaptcha_site_key = models.CharField(max_length=100, blank=True)
    recaptcha_secret_key = models.CharField(max_length=100, blank=True)
    
    # Auto-responses
    enable_auto_reply = models.BooleanField(default=True)
    auto_reply_subject = models.CharField(max_length=200, default='Thank you for contacting MfalmeBits')
    auto_reply_message = RichTextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Contact settings"
    
    def __str__(self):
        return "Contact Settings"
    
    def save(self, *args, **kwargs):
        # Ensure only one settings instance exists
        if not self.pk and ContactSettings.objects.exists():
            return
        super().save(*args, **kwargs)
