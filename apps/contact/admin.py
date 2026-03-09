from django.contrib import admin
from django.utils.html import format_html
from .models import ContactMessage, FAQ, Office, SupportTicket, SupportReply, ContactSettings

class SupportReplyInline(admin.TabularInline):
    model = SupportReply
    extra = 0
    fields = ['user', 'message', 'attachment', 'is_internal', 'created_at']
    readonly_fields = ['created_at']


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject_type', 'status', 'created_at']
    list_filter = ['subject_type', 'status', 'source']
    search_fields = ['name', 'email', 'subject', 'message']
    readonly_fields = ['ip_address', 'user_agent', 'created_at', 'updated_at']
    list_editable = ['status']
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'email', 'phone')
        }),
        ('Message', {
            'fields': ('subject_type', 'subject', 'message', 'attachment')
        }),
        ('Status', {
            'fields': ('status', 'assigned_to', 'notes')
        }),
        ('Response', {
            'fields': ('response_sent', 'responded_at', 'response_message')
        }),
        ('Source', {
            'fields': ('source', 'ip_address', 'user_agent')
        }),
        ('Newsletter', {
            'fields': ('is_subscribed',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    actions = ['mark_as_read', 'mark_as_replied', 'mark_as_archived']
    
    def mark_as_read(self, request, queryset):
        queryset.update(status='read')
    mark_as_read.short_description = "Mark selected as read"
    
    def mark_as_replied(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='replied', responded_at=timezone.now())
    mark_as_replied.short_description = "Mark selected as replied"
    
    def mark_as_archived(self, request, queryset):
        queryset.update(status='archived')
    mark_as_archived.short_description = "Archive selected"


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ['question', 'category', 'order', 'views_count', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['question', 'answer']
    list_editable = ['order', 'is_active']
    
    fieldsets = (
        ('FAQ', {
            'fields': ('question', 'answer', 'category')
        }),
        ('Settings', {
            'fields': ('order', 'is_active')
        }),
        ('SEO', {
            'fields': ('seo_title', 'seo_description')
        }),
        ('Statistics', {
            'fields': ('views_count',)
        }),
    )


@admin.register(Office)
class OfficeAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'country', 'phone', 'email', 'is_headquarters', 'is_active']
    list_filter = ['country', 'is_headquarters', 'is_active']
    search_fields = ['name', 'city', 'country', 'address']
    list_editable = ['is_headquarters', 'is_active']


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ['ticket_id', 'name', 'email', 'subject', 'priority', 'status', 'created_at']
    list_filter = ['priority', 'status', 'category']
    search_fields = ['ticket_id', 'name', 'email', 'subject', 'description']
    readonly_fields = ['ticket_id', 'ip_address', 'created_at', 'resolved_at']
    inlines = [SupportReplyInline]
    
    fieldsets = (
        ('Ticket Information', {
            'fields': ('ticket_id', 'user', 'name', 'email')
        }),
        ('Details', {
            'fields': ('category', 'priority', 'subject', 'description', 'attachment')
        }),
        ('Status', {
            'fields': ('status', 'assigned_to')
        }),
        ('Metadata', {
            'fields': ('ip_address', 'created_at', 'updated_at', 'resolved_at')
        }),
    )
    
    actions = ['mark_in_progress', 'mark_resolved', 'mark_closed']
    
    def mark_in_progress(self, request, queryset):
        queryset.update(status='in_progress')
    mark_in_progress.short_description = "Mark as in progress"
    
    def mark_resolved(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='resolved', resolved_at=timezone.now())
    mark_resolved.short_description = "Mark as resolved"
    
    def mark_closed(self, request, queryset):
        queryset.update(status='closed')
    mark_closed.short_description = "Mark as closed"


@admin.register(ContactSettings)
class ContactSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Email Settings', {
            'fields': ('contact_email', 'support_email', 'sales_email')
        }),
        ('Phone Numbers', {
            'fields': ('primary_phone', 'secondary_phone')
        }),
        ('Social Media', {
            'fields': ('facebook', 'twitter', 'instagram', 'linkedin', 'youtube')
        }),
        ('Business Information', {
            'fields': ('business_hours', 'general_response_time', 'support_response_time')
        }),
        ('reCAPTCHA', {
            'fields': ('recaptcha_site_key', 'recaptcha_secret_key')
        }),
        ('Auto-Reply', {
            'fields': ('enable_auto_reply', 'auto_reply_subject', 'auto_reply_message')
        }),
    )
    
    def has_add_permission(self, request):
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)
