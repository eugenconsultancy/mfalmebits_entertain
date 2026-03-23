from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
import uuid


class Profile(models.Model):
    """Extended user profile"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Personal Information
    bio = models.TextField(max_length=500, blank=True)
    avatar = models.ImageField(upload_to='accounts/avatars/', blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    
    # Location
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    address = models.TextField(blank=True)
    
    # Professional Information
    occupation = models.CharField(max_length=100, blank=True)
    organization = models.CharField(max_length=200, blank=True)
    website = models.URLField(blank=True)
    
    # Social Media
    twitter = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    facebook = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    
    # Preferences
    email_notifications = models.BooleanField(default=True)
    newsletter_subscribed = models.BooleanField(default=True)
    language = models.CharField(max_length=10, default='en', choices=[
        ('en', 'English'),
        ('sw', 'Swahili'),
        ('fr', 'French'),
        ('pt', 'Portuguese'),
    ])
    
    # Account Status
    email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=100, blank=True)
    
    # Metadata
    last_active = models.DateTimeField(null=True, blank=True)
    login_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['email_verified']),
        ]
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def get_absolute_url(self):
        return reverse('accounts:profile', args=[self.user.username])
    
    def get_full_name(self):
        return self.user.get_full_name() or self.user.username
    
    def generate_verification_token(self):
        """Generate email verification token"""
        import hashlib
        import time
        token = hashlib.sha256(f"{self.user.email}{time.time()}{uuid.uuid4()}".encode()).hexdigest()
        self.email_verification_token = token
        self.save(update_fields=['email_verification_token'])
        return token


# FIXED: Only ONE signal for profile creation (no duplicate save signal)
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create profile when user is created - ONLY on creation"""
    if created:
        Profile.objects.get_or_create(user=instance)
        print(f"✅ Profile created for user: {instance.username}")


class LoginHistory(models.Model):
    """Track user login history"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_history')
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    device_type = models.CharField(max_length=50, blank=True)
    browser = models.CharField(max_length=100, blank=True)
    os = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=200, blank=True)
    login_successful = models.BooleanField(default=True)
    login_time = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-login_time']
        verbose_name_plural = "Login histories"
    
    def __str__(self):
        return f"{self.user.username} logged in at {self.login_time}"


class SavedItem(models.Model):
    """User's saved/bookmarked items"""
    ITEM_TYPES = (
        ('archive', 'Archive Entry'),
        ('product', 'Digital Product'),
        ('blog', 'Blog Post'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_items')
    item_type = models.CharField(max_length=20, choices=ITEM_TYPES)
    item_id = models.IntegerField()
    
    # Metadata
    notes = models.CharField(max_length=500, blank=True)
    tags = models.CharField(max_length=200, blank=True, help_text="Comma-separated tags")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['user', 'item_type', 'item_id']
    
    def __str__(self):
        return f"{self.user.username} saved {self.item_type} #{self.item_id}"
    
    def get_item(self):
        """Get the actual item based on type"""
        if self.item_type == 'archive':
            from apps.archive.models import ArchiveEntry
            try:
                return ArchiveEntry.objects.get(id=self.item_id)
            except ArchiveEntry.DoesNotExist:
                return None
        elif self.item_type == 'product':
            from apps.library.models import DigitalProduct
            try:
                return DigitalProduct.objects.get(id=self.item_id)
            except DigitalProduct.DoesNotExist:
                return None
        elif self.item_type == 'blog':
            from apps.blog.models import Post
            try:
                return Post.objects.get(id=self.item_id)
            except Post.DoesNotExist:
                return None
        return None


class UserPreference(models.Model):
    """User preferences and settings"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    
    # Display preferences
    theme = models.CharField(max_length=20, default='light', choices=[
        ('light', 'Light'),
        ('dark', 'Dark'),
        ('system', 'System Default'),
    ])
    items_per_page = models.IntegerField(default=25)
    
    # Privacy settings
    profile_visibility = models.CharField(max_length=20, default='public', choices=[
        ('public', 'Public'),
        ('private', 'Private'),
        ('followers', 'Followers Only'),
    ])
    show_email = models.BooleanField(default=False)
    show_saved_items = models.BooleanField(default=False)
    
    # Notification preferences
    email_on_comment = models.BooleanField(default=True)
    email_on_reply = models.BooleanField(default=True)
    email_on_purchase = models.BooleanField(default=True)
    email_on_newsletter = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Preferences"


# FIXED: Only ONE signal for preferences creation (no duplicate)
@receiver(post_save, sender=User)
def create_user_preferences(sender, instance, created, **kwargs):
    """Create preferences when user is created - ONLY on creation"""
    if created:
        UserPreference.objects.get_or_create(user=instance)
        print(f"✅ Preferences created for user: {instance.username}")


class DownloadHistory(models.Model):
    """Track user downloads"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='downloads')
    item_type = models.CharField(max_length=20, choices=SavedItem.ITEM_TYPES)
    item_id = models.IntegerField()
    item_title = models.CharField(max_length=200)
    download_count = models.IntegerField(default=1)
    last_downloaded = models.DateTimeField(auto_now=True)
    first_downloaded = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-last_downloaded']
        unique_together = ['user', 'item_type', 'item_id']
    
    def __str__(self):
        return f"{self.user.username} downloaded {self.item_title}"


class PaymentMethod(models.Model):
    """Saved payment methods for users"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_methods')
    method_type = models.CharField(max_length=20, choices=[
        ('card', 'Credit Card'),
        ('paypal', 'PayPal'),
        ('mpesa', 'M-Pesa'),
    ])
    
    # For cards
    card_last4 = models.CharField(max_length=4, blank=True)
    card_brand = models.CharField(max_length=20, blank=True)
    card_expiry = models.CharField(max_length=7, blank=True)
    
    # For PayPal
    paypal_email = models.EmailField(blank=True)
    
    # For M-Pesa
    mpesa_phone = models.CharField(max_length=20, blank=True)
    
    # Stripe/Payment processor IDs
    payment_method_id = models.CharField(max_length=100, blank=True)
    customer_id = models.CharField(max_length=100, blank=True)
    
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-is_default', '-created_at']
    
    def __str__(self):
        if self.method_type == 'card':
            return f"{self.card_brand} ending in {self.card_last4}"
        elif self.method_type == 'paypal':
            return f"PayPal: {self.paypal_email}"
        elif self.method_type == 'mpesa':
            return f"M-Pesa: {self.mpesa_phone}"
        return f"Payment Method #{self.id}"


class AccountSettings(models.Model):
    """Global account settings"""
    allow_registration = models.BooleanField(default=True)
    require_email_verification = models.BooleanField(default=True)
    allow_social_login = models.BooleanField(default=True)
    
    # Security settings
    password_min_length = models.IntegerField(default=8)
    password_require_uppercase = models.BooleanField(default=True)
    password_require_numbers = models.BooleanField(default=True)
    password_require_special = models.BooleanField(default=True)
    
    # Session settings
    session_timeout = models.IntegerField(default=3600, help_text="Session timeout in seconds")
    max_login_attempts = models.IntegerField(default=5)
    lockout_duration = models.IntegerField(default=300, help_text="Lockout duration in seconds")
    
    # Default user settings
    default_user_group = models.CharField(max_length=50, default='user')
    default_email_notifications = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Account settings"
    
    def __str__(self):
        return "Account Settings"
    
    def save(self, *args, **kwargs):
        if not self.pk and AccountSettings.objects.exists():
            return
        super().save(*args, **kwargs)