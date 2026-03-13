from django.db import models
from django.urls import reverse
from django.core.validators import FileExtensionValidator
from django_ckeditor_5.fields import CKEditor5Field
from utils.seo import SEOMetaGenerator
from utils.slug_utils import generate_seo_slug
import uuid

class CollaborationCategory(models.Model):
    """Categories for collaboration"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    icon = models.CharField(max_length=50, help_text="FontAwesome icon class")
    image = models.ImageField(upload_to='collaboration/categories/', blank=True, null=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    # SEO Fields
    seo_title = models.CharField(max_length=60, blank=True)
    seo_description = models.CharField(max_length=160, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name_plural = "Collaboration categories"
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_seo_slug(self.name, CollaborationCategory)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('collaboration:category', args=[self.slug])


class CollaborationProject(models.Model):
    """Collaboration projects"""
    STATUS_CHOICES = (
        ('proposal', 'Proposal'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('published', 'Published'),
        ('rejected', 'Rejected'),
    )
    
    CATEGORY_CHOICES = (
        ('artist', 'Visual Artist'),
        ('designer', 'Designer'),
        ('writer', 'Writer/Author'),
        ('musician', 'Musician/Composer'),
        ('filmmaker', 'Filmmaker'),
        ('scholar', 'Scholar/Researcher'),
        ('educator', 'Educator'),
        ('cultural_practitioner', 'Cultural Practitioner'),
        ('other', 'Other'),
    )
    
    # Basic Information
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=250)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    collaboration_category = models.ForeignKey(
        CollaborationCategory, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    
    # Creator Information
    creator_name = models.CharField(max_length=100)
    creator_bio = models.TextField()
    creator_email = models.EmailField()
    creator_phone = models.CharField(max_length=20, blank=True)
    creator_website = models.URLField(blank=True)
    creator_location = models.CharField(max_length=100, blank=True)
    
    # Project Details
    description = CKEditor5Field('Description', config_name='extends')
    short_description = models.CharField(max_length=300)
    goals = models.TextField(help_text="What do you hope to achieve?")
    inspiration = models.TextField(blank=True, help_text="What inspired this project?")
    
    # Timeline
    proposed_duration = models.CharField(max_length=100, help_text="e.g., 3 months")
    proposed_start_date = models.DateField(null=True, blank=True)
    
    # Budget (if applicable)
    has_budget = models.BooleanField(default=False)
    budget_details = models.TextField(blank=True)
    funding_request = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Portfolio/Samples
    portfolio_url = models.URLField(blank=True)
    
    # Files
    proposal_document = models.FileField(
        upload_to='collaboration/proposals/',
        validators=[FileExtensionValidator(['pdf', 'doc', 'docx'])],
        blank=True,
        null=True
    )
    
    # Images
    featured_image = models.ImageField(upload_to='collaboration/projects/', blank=True, null=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='proposal')
    reviewed_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)
    review_notes = models.TextField(blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    views_count = models.IntegerField(default=0)
    
    # Terms
    terms_accepted = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['category']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.creator_name} ({self.get_status_display()})"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_seo_slug(self.title, CollaborationProject)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('collaboration:project_detail', args=[self.slug])
    
    def increment_views(self):
        self.views_count += 1
        self.save(update_fields=['views_count'])


class CollaborationImage(models.Model):
    """Additional images for collaboration projects"""
    project = models.ForeignKey(CollaborationProject, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='collaboration/projects/gallery/')
    caption = models.CharField(max_length=200, blank=True)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"Image for {self.project.title}"


class CollaborationSubmission(models.Model):
    """Quick submission form for potential collaborators"""
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    creator_type = models.CharField(max_length=50, choices=CollaborationProject.CATEGORY_CHOICES)
    portfolio_link = models.URLField(help_text="Link to your portfolio or work samples")
    project_idea = models.TextField(help_text="Briefly describe your collaboration idea")
    
    # Files
    samples = models.FileField(
        upload_to='collaboration/submissions/',
        validators=[FileExtensionValidator(['pdf', 'doc', 'docx', 'jpg', 'png', 'zip'])],
        help_text="Upload work samples (PDF, DOC, Images, or ZIP)"
    )
    
    # Status
    status = models.CharField(max_length=20, default='pending', choices=[
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
        ('contacted', 'Contacted'),
        ('archived', 'Archived'),
    ])
    
    # Metadata
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)
    
    terms_accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.creator_type}"


class CollaborationTestimonial(models.Model):
    """Testimonials from collaborators"""
    project = models.ForeignKey(CollaborationProject, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='collaboration/testimonials/', blank=True, null=True)
    content = models.TextField()
    rating = models.IntegerField(default=5, choices=[(i, i) for i in range(1, 6)])
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-is_featured', '-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.project.title if self.project else 'General'}"


class CollaborationFAQ(models.Model):
    """Frequently asked questions about collaboration"""
    question = models.CharField(max_length=200)
    
    # Updated to CKEditor5Field
    answer = CKEditor5Field('Answer', config_name='extends')
    
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    
    class Meta:
        ordering = ['order']
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"
    
    def __str__(self):
        return self.question
