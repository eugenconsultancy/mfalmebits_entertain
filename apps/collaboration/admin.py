from django.contrib import admin
from django.utils.html import format_html
from .models import (
    CollaborationCategory, CollaborationProject, 
    CollaborationImage, CollaborationSubmission,
    CollaborationTestimonial, CollaborationFAQ
)

class CollaborationImageInline(admin.TabularInline):
    model = CollaborationImage
    extra = 3


@admin.register(CollaborationCategory)
class CollaborationCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'order', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['order', 'is_active']


@admin.register(CollaborationProject)
class CollaborationProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'creator_name', 'category', 'status', 'views_count', 'created_at']
    list_filter = ['status', 'category', 'created_at']
    search_fields = ['title', 'creator_name', 'creator_email', 'description']
    readonly_fields = ['views_count', 'ip_address', 'created_at', 'updated_at']
    inlines = [CollaborationImageInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'category', 'collaboration_category')
        }),
        ('Creator Information', {
            'fields': ('creator_name', 'creator_bio', 'creator_email', 'creator_phone',
                      'creator_website', 'creator_location')
        }),
        ('Project Details', {
            'fields': ('short_description', 'description', 'goals', 'inspiration')
        }),
        ('Timeline & Budget', {
            'fields': ('proposed_duration', 'proposed_start_date', 'has_budget',
                      'budget_details', 'funding_request')
        }),
        ('Portfolio & Files', {
            'fields': ('portfolio_url', 'proposal_document', 'featured_image')
        }),
        ('Status', {
            'fields': ('status', 'reviewed_by', 'review_notes', 'reviewed_at')
        }),
        ('Metadata', {
            'fields': ('views_count', 'ip_address', 'terms_accepted', 'created_at', 'updated_at')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # New object
            obj.ip_address = request.META.get('REMOTE_ADDR')
        super().save_model(request, obj, form, change)


@admin.register(CollaborationSubmission)
class CollaborationSubmissionAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'creator_type', 'email', 'status', 'created_at']
    list_filter = ['status', 'creator_type', 'created_at']
    search_fields = ['first_name', 'last_name', 'email', 'project_idea']
    readonly_fields = ['ip_address', 'created_at']
    
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    full_name.short_description = "Name"
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'email', 'creator_type')
        }),
        ('Submission', {
            'fields': ('portfolio_link', 'project_idea', 'samples')
        }),
        ('Status', {
            'fields': ('status', 'reviewed_by', 'reviewed_at', 'notes')
        }),
        ('Metadata', {
            'fields': ('ip_address', 'terms_accepted', 'created_at')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # New object
            obj.ip_address = request.META.get('REMOTE_ADDR')
        super().save_model(request, obj, form, change)


@admin.register(CollaborationTestimonial)
class CollaborationTestimonialAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'rating', 'is_featured', 'is_active', 'created_at']
    list_filter = ['rating', 'is_featured', 'is_active']
    search_fields = ['name', 'content']
    list_editable = ['is_featured', 'is_active']


@admin.register(CollaborationFAQ)
class CollaborationFAQAdmin(admin.ModelAdmin):
    list_display = ['question', 'order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['question', 'answer']
    list_editable = ['order', 'is_active']
