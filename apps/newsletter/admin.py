from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Subscriber, NewsletterTemplate, NewsletterCampaign,
    NewsletterIssue, NewsletterLink, NewsletterTracking,
    NewsletterCategory, NewsletterArticle, NewsletterSettings
)

class NewsletterLinkInline(admin.TabularInline):
    model = NewsletterLink
    extra = 0
    readonly_fields = ['url', 'text', 'click_count']


class NewsletterTrackingInline(admin.TabularInline):
    model = NewsletterTracking
    extra = 0
    readonly_fields = ['subscriber', 'event_type', 'link', 'ip_address', 'created_at']
    can_delete = False


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ['email', 'first_name', 'last_name', 'frequency', 'is_active', 'confirmed', 'subscribed_at']
    list_filter = ['is_active', 'confirmed', 'frequency', 'source']
    search_fields = ['email', 'first_name', 'last_name']
    readonly_fields = ['confirmation_token', 'unsubscribe_token', 'ip_address', 'subscribed_at', 'confirmed_at', 'unsubscribed_at', 'last_sent_at']
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('email', 'first_name', 'last_name')
        }),
        ('Subscription Details', {
            'fields': ('is_active', 'confirmed', 'frequency', 'interests')
        }),
        ('Tokens', {
            'fields': ('confirmation_token', 'unsubscribe_token')
        }),
        ('Source', {
            'fields': ('source', 'source_url', 'ip_address')
        }),
        ('Timestamps', {
            'fields': ('subscribed_at', 'confirmed_at', 'unsubscribed_at', 'last_sent_at')
        }),
    )
    
    actions = ['send_test_email', 'mark_as_active', 'mark_as_inactive']
    
    def send_test_email(self, request, queryset):
        # This would send a test email
        self.message_user(request, f"Test email would be sent to {queryset.count()} subscribers.")
    send_test_email.short_description = "Send test email"
    
    def mark_as_active(self, request, queryset):
        queryset.update(is_active=True)
    mark_as_active.short_description = "Mark as active"
    
    def mark_as_inactive(self, request, queryset):
        queryset.update(is_active=False)
    mark_as_inactive.short_description = "Mark as inactive"


@admin.register(NewsletterTemplate)
class NewsletterTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_default', 'is_active', 'created_at']
    list_filter = ['is_default', 'is_active']
    search_fields = ['name', 'description', 'subject']
    prepopulated_fields = {'slug': ('name',)}
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description')
        }),
        ('Content', {
            'fields': ('subject', 'html_content', 'text_content')
        }),
        ('Preview', {
            'fields': ('preview_image',)
        }),
        ('Settings', {
            'fields': ('is_default', 'is_active')
        }),
    )


@admin.register(NewsletterCampaign)
class NewsletterCampaignAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'total_recipients', 'sent_count', 'opens_count', 'clicks_count', 'created_at']
    list_filter = ['status', 'frequency', 'created_at']
    search_fields = ['title', 'subject']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['total_recipients', 'sent_count', 'opens_count', 'clicks_count', 'unsubscribes_count', 'bounces_count']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'subject', 'preview_text')
        }),
        ('Content', {
            'fields': ('template', 'html_content', 'text_content')
        }),
        ('Targeting', {
            'fields': ('target_all_subscribers', 'target_frequency', 'target_interests')
        }),
        ('Schedule', {
            'fields': ('frequency', 'scheduled_for', 'sent_at')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Statistics', {
            'fields': ('total_recipients', 'sent_count', 'opens_count', 'clicks_count', 'unsubscribes_count', 'bounces_count')
        }),
        ('SEO', {
            'fields': ('seo_title', 'seo_description')
        }),
    )
    
    actions = ['send_test', 'send_campaign', 'duplicate_campaign']
    
    def send_test(self, request, queryset):
        # This would send a test email
        self.message_user(request, f"Test email would be sent for {queryset.count()} campaigns.")
    send_test.short_description = "Send test email"
    
    def send_campaign(self, request, queryset):
        # This would trigger the campaign to be sent
        queryset.update(status='sending')
        self.message_user(request, f"{queryset.count()} campaigns marked for sending.")
    send_campaign.short_description = "Start sending"
    
    def duplicate_campaign(self, request, queryset):
        for campaign in queryset:
            campaign.pk = None
            campaign.title = f"{campaign.title} (Copy)"
            campaign.status = 'draft'
            campaign.save()
        self.message_user(request, f"{queryset.count()} campaigns duplicated.")
    duplicate_campaign.short_description = "Duplicate campaign"


@admin.register(NewsletterIssue)
class NewsletterIssueAdmin(admin.ModelAdmin):
    list_display = ['campaign', 'issue_number', 'subject', 'recipient_count', 'opens', 'clicks', 'sent_at']
    list_filter = ['campaign', 'sent_at']
    search_fields = ['subject']
    readonly_fields = ['opens', 'clicks', 'unsubscribes', 'bounces']
    inlines = [NewsletterLinkInline, NewsletterTrackingInline]


@admin.register(NewsletterLink)
class NewsletterLinkAdmin(admin.ModelAdmin):
    list_display = ['url', 'text', 'issue', 'click_count', 'created_at']
    list_filter = ['issue__campaign']
    search_fields = ['url', 'text']
    readonly_fields = ['click_count']


@admin.register(NewsletterTracking)
class NewsletterTrackingAdmin(admin.ModelAdmin):
    list_display = ['subscriber', 'issue', 'event_type', 'link', 'ip_address', 'created_at']
    list_filter = ['event_type', 'created_at']
    search_fields = ['subscriber__email', 'ip_address']
    readonly_fields = ['created_at']


@admin.register(NewsletterCategory)
class NewsletterCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['color', 'order', 'is_active']


@admin.register(NewsletterArticle)
class NewsletterArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'author', 'is_featured', 'views_count', 'created_at']
    list_filter = ['category', 'is_featured', 'is_active']
    search_fields = ['title', 'content', 'excerpt']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['views_count']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'category', 'author')
        }),
        ('Content', {
            'fields': ('excerpt', 'content')
        }),
        ('Media', {
            'fields': ('featured_image', 'image_alt')
        }),
        ('Source', {
            'fields': ('source_url', 'source_name')
        }),
        ('Status', {
            'fields': ('is_featured', 'is_active', 'views_count')
        }),
    )


@admin.register(NewsletterSettings)
class NewsletterSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Sender Information', {
            'fields': ('sender_name', 'sender_email', 'reply_to')
        }),
        ('Subscription Settings', {
            'fields': ('require_confirmation', 'double_opt_in', 'welcome_email_subject', 'welcome_email_content')
        }),
        ('Unsubscribe Settings', {
            'fields': ('unsubscribe_landing_page',)
        }),
        ('API Integration', {
            'fields': ('mailchimp_api_key', 'mailchimp_list_id', 'sendgrid_api_key')
        }),
        ('Rate Limiting', {
            'fields': ('max_emails_per_hour', 'max_emails_per_day')
        }),
        ('Footer', {
            'fields': ('footer_text',)
        }),
    )
    
    def has_add_permission(self, request):
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)
