from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count
from .models import Theme, ArchiveEntry, ArchiveImage, ArchiveDownload

class ArchiveImageInline(admin.TabularInline):
    """Inline admin for archive images"""
    model = ArchiveImage
    extra = 1
    fields = ['image', 'caption', 'alt_text', 'order']
    readonly_fields = ['image_preview']
    
    def image_preview(self, obj):
        if obj and obj.image:
            return format_html('<img src="{}" width="100" height="auto" style="border-radius: 4px;" />', obj.image.url)
        return "No image"
    image_preview.short_description = "Preview"

@admin.register(Theme)
class ThemeAdmin(admin.ModelAdmin):
    """Admin configuration for Theme model"""
    list_display = ['name', 'slug', 'order', 'entry_count', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['order', 'is_active']
    readonly_fields = ['created_at', 'updated_at', 'entry_count_display']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'icon', 'color', 'featured_image')
        }),
        ('Organization', {
            'fields': ('order', 'is_active')
        }),
        ('SEO', {
            'fields': ('seo_title', 'seo_description'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'entry_count_display'),
            'classes': ('collapse',)
        }),
    )
    
    def entry_count(self, obj):
        return obj.get_entry_count()
    entry_count.short_description = "Entries"
    entry_count.admin_order_field = 'entry_count'
    
    def entry_count_display(self, obj):
        count = obj.get_entry_count()
        url = reverse('admin:archive_archiveentry_changelist') + f'?theme__id__exact={obj.id}'
        return format_html('<a href="{}">{} Entries</a>', url, count)
    entry_count_display.short_description = "Entries Count"
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(entry_count=Count('archiveentry'))
    
    actions = ['activate_themes', 'deactivate_themes']
    
    def activate_themes(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} themes activated successfully.')
    activate_themes.short_description = "Activate selected themes"
    
    def deactivate_themes(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} themes deactivated successfully.')
    deactivate_themes.short_description = "Deactivate selected themes"


@admin.register(ArchiveEntry)
class ArchiveEntryAdmin(admin.ModelAdmin):
    """Admin configuration for ArchiveEntry model"""
    list_display = ['title', 'theme', 'author', 'published_date', 'views_count', 'download_count', 'is_featured', 'is_active']
    list_filter = ['theme', 'is_featured', 'is_active', 'published_date', 'document_type']
    search_fields = ['title', 'content', 'excerpt', 'author']
    prepopulated_fields = {'slug': ('title',)}
    # CORRECTED readonly_fields - only using fields that exist in the model
    readonly_fields = ['views_count', 'download_count', 'created_at', 'featured_image_preview', 'view_on_site_link']
    filter_horizontal = ['tags']
    date_hierarchy = 'published_date'
    list_editable = ['is_featured', 'is_active']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'theme', 'author', 'author_bio')
        }),
        ('Content', {
            'fields': ('excerpt', 'content', 'featured_image', 'featured_image_preview', 'image_alt')
        }),
        ('Document', {
            'fields': ('document', 'document_type'),
            'classes': ('collapse',)
        }),
        ('Categorization', {
            'fields': ('tags', 'is_featured', 'is_active')
        }),
        ('SEO', {
            'fields': ('seo_title', 'seo_description', 'canonical_url'),
            'classes': ('collapse',)
        }),
        ('References', {
            'fields': ('references', 'citation_text'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('views_count', 'download_count', 'published_date', 'updated_date', 'created_at'),
            'classes': ('collapse',)
        }),
        ('URL', {
            'fields': ('view_on_site_link',),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [ArchiveImageInline]
    
    def featured_image_preview(self, obj):
        if obj and obj.featured_image:
            return format_html('<img src="{}" width="200" height="auto" style="border-radius: 8px;" />', obj.featured_image.url)
        return "No image"
    featured_image_preview.short_description = "Preview"
    
    def view_on_site_link(self, obj):
        """Generate a link to view the entry on the site"""
        if obj and obj.pk and obj.is_active:
            try:
                url = obj.get_absolute_url()
                return format_html('<a href="{}" target="_blank">View on site →</a>', url)
            except:
                return "URL not available"
        return "Not available"
    view_on_site_link.short_description = "View on site"
    
    actions = ['feature_entries', 'unfeature_entries', 'activate_entries', 'deactivate_entries', 'export_as_csv']
    
    def feature_entries(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} entries marked as featured.')
    feature_entries.short_description = "Mark as featured"
    
    def unfeature_entries(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} entries unmarked as featured.')
    unfeature_entries.short_description = "Unmark as featured"
    
    def activate_entries(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} entries activated.')
    activate_entries.short_description = "Activate selected entries"
    
    def deactivate_entries(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} entries deactivated.')
    deactivate_entries.short_description = "Deactivate selected entries"
    
    def export_as_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        from datetime import datetime
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="archive_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Title', 'Theme', 'Author', 'Published Date', 'Views', 'Downloads', 'Tags', 'URL'])
        
        for entry in queryset:
            writer.writerow([
                entry.title,
                entry.theme.name,
                entry.author,
                entry.published_date.strftime('%Y-%m-%d'),
                entry.views_count,
                entry.download_count,
                ', '.join([tag.name for tag in entry.tags.all()]),
                entry.get_absolute_url() if hasattr(entry, 'get_absolute_url') else ''
            ])
        
        return response
    export_as_csv.short_description = "Export selected as CSV"
    
    def save_model(self, request, obj, form, change):
        obj.save()


@admin.register(ArchiveImage)
class ArchiveImageAdmin(admin.ModelAdmin):
    """Admin configuration for ArchiveImage model"""
    list_display = ['id', 'entry', 'order', 'image_preview']
    list_filter = ['entry__theme']
    search_fields = ['entry__title', 'caption', 'alt_text']
    list_editable = ['order']
    readonly_fields = ['image_preview']
    
    fieldsets = (
        (None, {
            'fields': ('entry', 'image', 'image_preview', 'caption', 'alt_text', 'order')
        }),
    )
    
    def image_preview(self, obj):
        if obj and obj.image:
            return format_html('<img src="{}" width="100" height="auto" style="border-radius: 4px;" />', obj.image.url)
        return "No image"
    image_preview.short_description = "Preview"


@admin.register(ArchiveDownload)
class ArchiveDownloadAdmin(admin.ModelAdmin):
    """Admin configuration for ArchiveDownload model"""
    list_display = ['entry', 'user', 'ip_address', 'downloaded_at']
    list_filter = ['downloaded_at']
    search_fields = ['entry__title', 'user__username', 'ip_address']
    readonly_fields = ['downloaded_at']
    date_hierarchy = 'downloaded_at'
    
    fieldsets = (
        (None, {
            'fields': ('entry', 'user', 'ip_address', 'downloaded_at')
        }),
    )
    
    def has_add_permission(self, request):
        return False  # Downloads should only be created programmatically
    
    def has_change_permission(self, request, obj=None):
        return False  # Downloads shouldn't be editable