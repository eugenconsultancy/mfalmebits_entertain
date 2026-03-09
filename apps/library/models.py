from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from taggit.managers import TaggableManager
from ckeditor.fields import RichTextField
from utils.seo import SEOMetaGenerator
from utils.slug_utils import generate_seo_slug
from decimal import Decimal
import os

class ProductCategory(models.Model):
    """Categories for digital products"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    icon = models.CharField(max_length=50, help_text="FontAwesome icon class")
    image = models.ImageField(upload_to='library/categories/', blank=True, null=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    # SEO Fields
    seo_title = models.CharField(max_length=60, blank=True)
    seo_description = models.CharField(max_length=160, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Product categories"
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_seo_slug(self.name, ProductCategory)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('library:category', args=[self.slug])
    
    def get_product_count(self):
        return self.digitalproduct_set.filter(is_active=True).count()

class DigitalProduct(models.Model):
    """Digital products for sale"""
    FORMAT_CHOICES = (
        ('pdf', 'PDF'),
        ('epub', 'EPUB'),
        ('mobi', 'MOBI'),
        ('mp3', 'MP3 Audio'),
        ('mp4', 'MP4 Video'),
        ('zip', 'ZIP Archive'),
        ('online', 'Online Course'),
    )
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=250)
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)
    
    # Content
    description = RichTextField()
    short_description = models.CharField(max_length=300)
    
    # Media
    cover_image = models.ImageField(upload_to='library/products/covers/')
    image_alt = models.CharField(max_length=100, blank=True)
    preview_file = models.FileField(upload_to='library/products/previews/', blank=True, null=True)
    
    # Product Details
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES)
    file_size = models.CharField(max_length=20, blank=True)
    pages = models.IntegerField(blank=True, null=True)
    duration = models.CharField(max_length=50, blank=True, help_text="For audio/video content")
    isbn = models.CharField(max_length=20, blank=True)
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    is_free = models.BooleanField(default=False)
    
    # Inventory
    stock = models.IntegerField(default=-1, help_text="-1 for unlimited")
    download_limit = models.IntegerField(default=5)
    
    # Metadata
    author = models.CharField(max_length=100)
    publisher = models.CharField(max_length=100, blank=True)
    published_date = models.DateField()
    tags = TaggableManager()
    
    # Status
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    views_count = models.IntegerField(default=0)
    purchase_count = models.IntegerField(default=0)
    
    # SEO Fields
    seo_title = models.CharField(max_length=60, blank=True)
    seo_description = models.CharField(max_length=160, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['category', '-created_at']),
            models.Index(fields=['is_featured']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_seo_slug(self.title, DigitalProduct)
        if not self.seo_title:
            self.seo_title = SEOMetaGenerator.generate_title(self)
        if not self.image_alt and self.cover_image:
            self.image_alt = f"{self.title} - MfalmeBits Digital Library"
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('library:detail', args=[self.category.slug, self.slug])
    
    def get_current_price(self):
        """Return sale price if available, otherwise regular price"""
        if self.sale_price and self.sale_price < self.price:
            return self.sale_price
        return self.price
    
    def is_on_sale(self):
        """Check if product is on sale"""
        return self.sale_price and self.sale_price < self.price
    
    def get_discount_percentage(self):
        """Calculate discount percentage"""
        if self.is_on_sale():
            discount = ((self.price - self.sale_price) / self.price) * 100
            return int(discount)
        return 0
    
    def increment_views(self):
        self.views_count += 1
        self.save(update_fields=['views_count'])

class ProductFile(models.Model):
    """Downloadable files for products"""
    product = models.ForeignKey(DigitalProduct, on_delete=models.CASCADE, related_name='files')
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='library/products/files/')
    file_type = models.CharField(max_length=20, choices=DigitalProduct.FORMAT_CHOICES)
    file_size = models.CharField(max_length=20)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.product.title} - {self.title}"

class Purchase(models.Model):
    """Record of product purchases"""
    PURCHASE_STATUS = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )
    
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    product = models.ForeignKey(DigitalProduct, on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=PURCHASE_STATUS, default='pending')
    payment_method = models.CharField(max_length=50)
    
    # Download tracking
    download_count = models.IntegerField(default=0)
    last_download = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    purchase_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-purchase_date']
        indexes = [
            models.Index(fields=['user', '-purchase_date']),
            models.Index(fields=['transaction_id']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.product.title} - {self.purchase_date}"
    
    def can_download(self):
        """Check if user can still download"""
        if self.product.download_limit == -1:
            return True
        return self.download_count < self.product.download_limit

class Review(models.Model):
    """Product reviews"""
    product = models.ForeignKey(DigitalProduct, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    title = models.CharField(max_length=200, blank=True)
    comment = models.TextField()
    
    # Verification
    verified_purchase = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['product', 'user']
    
    def __str__(self):
        return f"{self.user.email} - {self.product.title} - {self.rating} stars"

class Wishlist(models.Model):
    """User wishlists"""
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='wishlist')
    product = models.ForeignKey(DigitalProduct, on_delete=models.CASCADE)
    added_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'product']
        ordering = ['-added_date']
    
    def __str__(self):
        return f"{self.user.email} - {self.product.title}"
