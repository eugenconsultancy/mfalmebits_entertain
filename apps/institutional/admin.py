from django.contrib import admin
from django.utils.html import format_html
from .models import LicensingPlan, InstitutionalInquiry, InstitutionLicense, ResourceAccess, InstitutionalBrochure

@admin.register(LicensingPlan)
class LicensingPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'plan_type', 'price_per_year', 'min_users', 'max_users', 'is_featured', 'is_active', 'order']
    list_filter = ['plan_type', 'is_featured', 'is_active', 'support_level']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['order', 'is_featured', 'is_active']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'plan_type', 'short_description', 'description')
        }),
        ('Pricing', {
            'fields': ('price_per_year', 'setup_fee', 'min_users', 'max_users')
        }),
        ('Features', {
            'fields': ('features', 'max_downloads', 'max_searches', 'api_access', 'api_rate_limit')
        }),
        ('Support', {
            'fields': ('support_level', 'support_hours', 'response_time')
        }),
        ('Training & Reporting', {
            'fields': ('training_included', 'training_hours', 'webinar_access', 
                      'custom_reports', 'analytics_dashboard', 'usage_statistics')
        }),
        ('Branding', {
            'fields': ('white_label', 'custom_branding')
        }),
        ('SEO', {
            'fields': ('seo_title', 'seo_description')
        }),
        ('Status', {
            'fields': ('is_featured', 'is_active', 'order')
        }),
    )


@admin.register(InstitutionalInquiry)
class InstitutionalInquiryAdmin(admin.ModelAdmin):
    list_display = ['institution_name', 'contact_person', 'email', 'plan', 'number_of_users', 'status', 'created_at']
    list_filter = ['status', 'institution_type', 'source', 'created_at']
    search_fields = ['institution_name', 'contact_person', 'email', 'message']
    readonly_fields = ['ip_address', 'user_agent', 'utm_source', 'utm_medium', 'utm_campaign', 'created_at', 'updated_at']
    fieldsets = (
        ('Institution Information', {
            'fields': ('institution_name', 'institution_type', 'website', 'country', 'city', 'address')
        }),
        ('Contact Information', {
            'fields': ('contact_person', 'job_title', 'email', 'phone')
        }),
        ('Inquiry Details', {
            'fields': ('plan', 'number_of_users', 'content_types', 'message', 'additional_requirements')
        }),
        ('Timeline & Budget', {
            'fields': ('start_date', 'budget_range')
        }),
        ('Files', {
            'fields': ('attachment',)
        }),
        ('Tracking', {
            'fields': ('status', 'assigned_to', 'notes')
        }),
        ('Source Information', {
            'fields': ('source', 'utm_source', 'utm_medium', 'utm_campaign', 'ip_address', 'user_agent')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # New object
            obj.source = 'admin'
        super().save_model(request, obj, form, change)


@admin.register(InstitutionLicense)
class InstitutionLicenseAdmin(admin.ModelAdmin):
    list_display = ['institution', 'plan', 'license_key', 'start_date', 'end_date', 'status']
    list_filter = ['status', 'plan', 'start_date', 'end_date']
    search_fields = ['institution__institution_name', 'license_key']
    readonly_fields = ['license_key', 'total_downloads', 'total_searches', 'last_access']
    fieldsets = (
        ('Institution Information', {
            'fields': ('institution', 'plan', 'license_key')
        }),
        ('License Details', {
            'fields': ('start_date', 'end_date', 'number_of_users', 'status')
        }),
        ('Access Control', {
            'fields': ('ip_restrictions', 'domain_restrictions')
        }),
        ('Usage Statistics', {
            'fields': ('total_downloads', 'total_searches', 'last_access')
        }),
        ('Billing Information', {
            'fields': ('amount_paid', 'invoice_number', 'payment_status')
        }),
    )


@admin.register(ResourceAccess)
class ResourceAccessAdmin(admin.ModelAdmin):
    list_display = ['license', 'resource_type', 'resource_id', 'accessed_by', 'ip_address', 'accessed_at']
    list_filter = ['resource_type', 'accessed_at']
    search_fields = ['license__license_key', 'accessed_by', 'ip_address']
    readonly_fields = ['accessed_at']


@admin.register(InstitutionalBrochure)
class InstitutionalBrochureAdmin(admin.ModelAdmin):
    list_display = ['title', 'language', 'download_count', 'is_active', 'created_at']
    list_filter = ['language', 'is_active']
    search_fields = ['title', 'description']
    readonly_fields = ['download_count']
    fieldsets = (
        ('Brochure Information', {
            'fields': ('title', 'description', 'language')
        }),
        ('Files', {
            'fields': ('file', 'cover_image')
        }),
        ('Status', {
            'fields': ('is_active', 'download_count')
        }),
    )
    
    def response_change(self, request, obj):
        if "_preview" in request.POST:
            return format_html('<script>window.open("{}", "_blank");</script>', obj.file.url)
        return super().response_change(request, obj)
