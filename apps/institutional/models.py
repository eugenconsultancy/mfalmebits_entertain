from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from django_ckeditor_5.fields import CKEditor5Field
from utils.seo import SEOMetaGenerator
from utils.slug_utils import generate_seo_slug
import uuid

class LicensingPlan(models.Model):
    """Institutional licensing plans"""
    PLAN_TYPES = (
        ('school', 'K-12 School'),
        ('university', 'University/College'),
        ('library', 'Public Library'),
        ('ngo', 'Non-Profit Organization'),
        ('corporate', 'Corporate'),
        ('government', 'Government Agency'),
    )
    
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPES)
    description = CKEditor5Field('Description', config_name='extends')
    short_description = models.CharField(max_length=200)
    
    # Pricing
    price_per_year = models.DecimalField(max_digits=10, decimal_places=2)
    setup_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    min_users = models.IntegerField(default=1)
    max_users = models.IntegerField(default=100, help_text="-1 for unlimited")
    
    # Features (stored as JSON)
    features = models.JSONField(default=dict, help_text="List of included features")
    
    # Limits
    max_downloads = models.IntegerField(default=-1, help_text="-1 for unlimited")
    max_searches = models.IntegerField(default=-1)
    api_access = models.BooleanField(default=False)
    api_rate_limit = models.IntegerField(default=100, help_text="Requests per minute")
    
    # Support
    support_level = models.CharField(max_length=50, choices=[
        ('basic', 'Basic Email Support'),
        ('priority', 'Priority Email Support'),
        ('phone', 'Phone Support'),
        ('dedicated', 'Dedicated Account Manager'),
    ], default='basic')
    support_hours = models.CharField(max_length=100, default="Business Hours")
    response_time = models.CharField(max_length=100, default="Within 48 hours")
    
    # Training
    training_included = models.BooleanField(default=False)
    training_hours = models.IntegerField(default=0)
    webinar_access = models.BooleanField(default=False)
    
    # Reporting
    custom_reports = models.BooleanField(default=False)
    analytics_dashboard = models.BooleanField(default=False)
    usage_statistics = models.BooleanField(default=True)
    
    # Branding
    white_label = models.BooleanField(default=False)
    custom_branding = models.BooleanField(default=False)
    
    # Status
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    
    # SEO Fields
    seo_title = models.CharField(max_length=60, blank=True)
    seo_description = models.CharField(max_length=160, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'plan_type', 'price_per_year']
    
    def __str__(self):
        return f"{self.get_plan_type_display()} - {self.name}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_seo_slug(self.name, LicensingPlan)
        if not self.seo_title:
            self.seo_title = SEOMetaGenerator.generate_title(self)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('institutional:plan_detail', args=[self.slug])
    
    def get_feature_list(self):
        """Return features as a list"""
        return self.features.get('items', [])
    
    def get_user_range(self):
        if self.max_users == -1:
            return f"{self.min_users}+ users"
        return f"{self.min_users} - {self.max_users} users"
    
    def get_yearly_price_display(self):
        if self.price_per_year == 0:
            return "Custom Pricing"
        return f"${self.price_per_year:,.2f}/year"


class InstitutionalInquiry(models.Model):
    """Institutional inquiries and leads"""
    INQUIRY_STATUS = (
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('proposal_sent', 'Proposal Sent'),
        ('negotiation', 'Negotiation'),
        ('won', 'Won'),
        ('lost', 'Lost'),
    )
    
    INSTITUTION_TYPES = (
        ('school', 'K-12 School'),
        ('university', 'University/College'),
        ('library', 'Public Library'),
        ('ngo', 'Non-Profit Organization'),
        ('corporate', 'Corporate'),
        ('government', 'Government Agency'),
        ('other', 'Other'),
    )
    
    # Institution Info
    institution_name = models.CharField(max_length=200)
    institution_type = models.CharField(max_length=20, choices=INSTITUTION_TYPES)
    website = models.URLField(blank=True)
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    address = models.TextField(blank=True)
    
    # Contact Info
    contact_person = models.CharField(max_length=100)
    job_title = models.CharField(max_length=100, blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    
    # Inquiry Details
    plan = models.ForeignKey(LicensingPlan, on_delete=models.SET_NULL, null=True, blank=True)
    number_of_users = models.IntegerField(validators=[MinValueValidator(1)], default=1)
    content_types = models.CharField(max_length=200, help_text="What content they're interested in")
    message = models.TextField()
    additional_requirements = models.TextField(blank=True)
    
    # Timeline
    start_date = models.DateField(null=True, blank=True)
    budget_range = models.CharField(max_length=100, blank=True)
    
    # Files
    attachment = models.FileField(upload_to='institutional/inquiries/', blank=True, null=True)
    
    # Tracking
    status = models.CharField(max_length=20, choices=INQUIRY_STATUS, default='new')
    assigned_to = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)
    
    # Source
    source = models.CharField(max_length=50, default='website')
    utm_source = models.CharField(max_length=100, blank=True)
    utm_medium = models.CharField(max_length=100, blank=True)
    utm_campaign = models.CharField(max_length=100, blank=True)
    
    # Metadata
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Institutional inquiries"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['email']),
            models.Index(fields=['institution_name']),
        ]
    
    def __str__(self):
        return f"{self.institution_name} - {self.contact_person} ({self.get_status_display()})"
    
    def get_absolute_url(self):
        return reverse('admin:institutional_institutional_inquiry_change', args=[self.id])


class InstitutionLicense(models.Model):
    """Active institutional licenses"""
    LICENSE_STATUS = (
        ('active', 'Active'),
        ('pending', 'Pending Activation'),
        ('suspended', 'Suspended'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    )
    
    institution = models.ForeignKey(InstitutionalInquiry, on_delete=models.CASCADE)
    plan = models.ForeignKey(LicensingPlan, on_delete=models.CASCADE)
    license_key = models.CharField(max_length=100, unique=True, default=uuid.uuid4)
    
    # License Details
    start_date = models.DateField()
    end_date = models.DateField()
    number_of_users = models.IntegerField()
    
    # Access Control
    ip_restrictions = models.TextField(blank=True, help_text="Comma-separated IP ranges")
    domain_restrictions = models.TextField(blank=True, help_text="Comma-separated domains")
    
    # Usage
    total_downloads = models.IntegerField(default=0)
    total_searches = models.IntegerField(default=0)
    last_access = models.DateTimeField(null=True, blank=True)
    
    # Billing
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    invoice_number = models.CharField(max_length=100, blank=True)
    payment_status = models.CharField(max_length=20, default='paid')
    
    # Status
    status = models.CharField(max_length=20, choices=LICENSE_STATUS, default='pending')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.institution.institution_name} - {self.license_key}"
    
    def is_active(self):
        from django.utils import timezone
        return (self.status == 'active' and 
                self.start_date <= timezone.now().date() <= self.end_date)
    
    def days_remaining(self):
        from django.utils import timezone
        if self.end_date > timezone.now().date():
            return (self.end_date - timezone.now().date()).days
        return 0


class ResourceAccess(models.Model):
    """Track institutional resource access"""
    license = models.ForeignKey(InstitutionLicense, on_delete=models.CASCADE)
    resource_type = models.CharField(max_length=50, choices=[
        ('archive', 'Archive Entry'),
        ('product', 'Digital Product'),
    ])
    resource_id = models.IntegerField()
    accessed_by = models.CharField(max_length=100, blank=True, help_text="User identifier")
    ip_address = models.GenericIPAddressField()
    accessed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-accessed_at']
    
    def __str__(self):
        return f"{self.license} - {self.resource_type} - {self.accessed_at}"


class InstitutionalBrochure(models.Model):
    """Downloadable brochures"""
    title = models.CharField(max_length=200)
    description = CKEditor5Field('Description', config_name='extends')
    file = models.FileField(upload_to='institutional/brochures/')
    cover_image = models.ImageField(upload_to='institutional/brochures/covers/')
    language = models.CharField(max_length=50, default='English')
    download_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def increment_download(self):
        self.download_count += 1
        self.save(update_fields=['download_count'])
