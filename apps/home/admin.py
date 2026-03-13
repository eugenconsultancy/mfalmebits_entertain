from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count
from .models import (
    HomeSection, HeroSlide, FeaturedItem, 
    Testimonial, Partner, CTASection
)

class HomeSectionAdmin(admin.ModelAdmin):
    """Admin configuration for HomeSection model"""
    list_display = ['title', 'section_type', 'order', 'is_active', 'created_at']
    list_filter = ['section_type', 'is_active', 'created_at']
    search_fields = ['title', 'subtitle', 'content']
    list_editable = ['order', 'is_active']
    readonly_fields = ['created_at', 'updated_at', 'section_preview']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'subtitle', 'section_type', 'content')
        }),
        ('Background', {
            'fields': ('background_image', 'background_color'),
            'classes': ('collapse',)
        }),
        ('Display Settings', {
            'fields': ('order', 'is_active', 'animation_type', 'animation_delay')
        }),
        ('SEO', {
            'fields': ('seo_title', 'seo_description'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'section_preview'),
            'classes': ('collapse',)
        }),
    )
    
    def section_preview(self, obj):
        """Preview of the section"""
        if obj.id:
            return format_html(
                '<a href="{}" target="_blank" class="button">Preview Section</a>',
                reverse('home:home') + f'#{obj.section_type}'
            )
        return "Save to preview"
    section_preview.short_description = "Preview"
    
    actions = ['activate_sections', 'deactivate_sections']
    
    def activate_sections(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} sections activated.')
    activate_sections.short_description = "Activate selected sections"
    
    def deactivate_sections(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} sections deactivated.')
    deactivate_sections.short_description = "Deactivate selected sections"


from django.contrib import admin
from django.utils.html import format_html

# @admin.register(HeroSlide)
class HeroSlideAdmin(admin.ModelAdmin):
    """Admin configuration for HeroSlide model"""
    list_display = ['title', 'order', 'is_active', 'button_text', 'image_preview']
    list_filter = ['is_active', 'button_style']
    search_fields = ['title', 'subtitle', 'description']
    list_editable = ['order', 'is_active']
    
    # 1. Added 'created_at' here so Django knows it's display-only
    readonly_fields = ['image_preview', 'created_at']
    
    fieldsets = (
        ('Content', {
            'fields': ('title', 'subtitle', 'description'),
            'classes': ('collapse',), # Optional: makes it toggleable in Jazzmin
        }),
        ('Media', {
            'fields': ('image', 'image_preview', 'image_alt')
        }),
        ('Button', {
            'fields': ('button_text', 'button_url', 'button_style')
        }),
        ('Display Settings', {
            'fields': ('order', 'is_active', 'animation_duration')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'description': 'System-generated timestamps'
        }),
    )
    
    def image_preview(self, obj):
        """Preview of the slide image"""
        if obj.image:
            try:
                return format_html(
                    '<img src="{}" width="200" height="auto" style="border-radius: 8px; border: 1px solid #444;" />',
                    obj.image.url
                )
            except Exception:
                return "Error loading image"
        return "No image"
    image_preview.short_description = "Image Preview"
    
    actions = ['duplicate_slides']
    
    def duplicate_slides(self, request, queryset):
        for slide in queryset:
            slide.pk = None
            slide.title = f"{slide.title} (Copy)"
            slide.save()
        self.message_user(request, f'{queryset.count()} slides duplicated successfully.')
    duplicate_slides.short_description = "Duplicate selected slides"

class FeaturedItemAdmin(admin.ModelAdmin):
    """Admin configuration for FeaturedItem model"""
    list_display = ['title', 'item_type', 'order', 'is_active', 'image_preview', 'linked_content']
    list_filter = ['item_type', 'is_active']
    search_fields = ['title', 'description']
    list_editable = ['order', 'is_active']
    
    # FIX: Added 'created_at' here to stop the FieldError
    readonly_fields = ['image_preview', 'linked_content', 'created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'item_type')
        }),
        ('Media', {
            'fields': ('image', 'image_preview', 'image_alt')
        }),
        ('Content Link', {
            'fields': ('content_id', 'external_url'),
            'description': 'Provide either a content ID for internal items or an external URL'
        }),
        ('Display Settings', {
            'fields': ('order', 'is_active')
        }),
        ('Metadata', {
            'fields': ('created_at', 'linked_content'),
            'classes': ('collapse',)
        }),
    )
    
    def image_preview(self, obj):
        """Preview of the featured item image"""
        if obj.image:
            return format_html(
                '<img src="{}" width="100" height="auto" style="border-radius: 4px; border: 1px solid #444;" />',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = "Preview"
    
    def linked_content(self, obj):
        """Display linked content information"""
        if obj.item_type == 'archive' and obj.content_id:
            from apps.archive.models import ArchiveEntry
            try:
                entry = ArchiveEntry.objects.get(id=obj.content_id)
                url = reverse('admin:archive_archiveentry_change', args=[entry.id])
                return format_html('<a href="{}">{} (Archive)</a>', url, entry.title)
            except (ArchiveEntry.DoesNotExist, Exception):
                return format_html('<span style="color:red;">Archive Entry Not Found</span>')
                
        elif obj.item_type == 'product' and obj.content_id:
            from apps.library.models import DigitalProduct
            try:
                product = DigitalProduct.objects.get(id=obj.content_id)
                url = reverse('admin:library_digitalproduct_change', args=[product.id])
                return format_html('<a href="{}">{} (Product)</a>', url, product.title)
            except (DigitalProduct.DoesNotExist, Exception):
                return format_html('<span style="color:red;">Product Not Found</span>')
                
        elif obj.item_type == 'blog' and obj.content_id:
            from apps.blog.models import Post
            try:
                post = Post.objects.get(id=obj.content_id)
                url = reverse('admin:blog_post_change', args=[post.id])
                return format_html('<a href="{}">{} (Blog)</a>', url, post.title)
            except (Post.DoesNotExist, Exception):
                return format_html('<span style="color:red;">Blog Post Not Found</span>')
                
        elif obj.external_url:
            return format_html('<a href="{}" target="_blank">External Link ↗</a>', obj.external_url)
            
        return "No link"
    linked_content.short_description = "Linked Content"
    
    actions = ['link_to_archive', 'link_to_products', 'link_to_blog']
    
    def link_to_archive(self, request, queryset):
        self.message_user(request, 'Use the content_id field to link to specific archive entries.')
    link_to_archive.short_description = "How to link Archive"
    
    def link_to_products(self, request, queryset):
        self.message_user(request, 'Use the content_id field to link to specific products.')
    link_to_products.short_description = "How to link Products"
    
    def link_to_blog(self, request, queryset):
        self.message_user(request, 'Use the content_id field to link to specific blog posts.')
    link_to_blog.short_description = "How to link Blog"


class TestimonialAdmin(admin.ModelAdmin):
    """Admin configuration for Testimonial model"""
    list_display = ['name', 'company', 'rating', 'order', 'is_active', 'avatar_preview']
    list_filter = ['rating', 'is_active']
    search_fields = ['name', 'company', 'content']
    list_editable = ['order', 'is_active']
    
    # FIX: Added 'created_at' to readonly_fields
    readonly_fields = ['avatar_preview', 'created_at']
    
    fieldsets = (
        ('Author Information', {
            'fields': ('name', 'title', 'company')
        }),
        ('Testimonial Content', {
            'fields': ('content', 'rating')
        }),
        ('Media', {
            'fields': ('avatar', 'avatar_preview')
        }),
        ('Display Settings', {
            'fields': ('order', 'is_active')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )
    
    def avatar_preview(self, obj):
        """Preview of testimonial avatar"""
        if obj.avatar:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius: 50%; object-fit: cover; border: 2px solid #ddd;" />',
                obj.avatar.url
            )
        return format_html(
            '<div style="width:50px;height:50px;border-radius:50%;background:#8B4513;display:flex;align-items:center;justify-content:center;color:white;font-weight:bold;font-size: 1.2rem;">{}</div>',
            obj.name[0].upper() if obj.name else '?'
        )
    avatar_preview.short_description = "Avatar"
    
    actions = ['set_5_star', 'set_4_star', 'set_3_star']
    
    def set_5_star(self, request, queryset):
        updated = queryset.update(rating=5)
        self.message_user(request, f'{updated} testimonials set to 5 stars.')
    set_5_star.short_description = "Set rating to 5 stars"
    
    def set_4_star(self, request, queryset):
        updated = queryset.update(rating=4)
        self.message_user(request, f'{updated} testimonials set to 4 stars.')
    set_4_star.short_description = "Set rating to 4 stars"
    
    def set_3_star(self, request, queryset):
        updated = queryset.update(rating=3)
        self.message_user(request, f'{updated} testimonials set to 3 stars.')
    set_3_star.short_description = "Set rating to 3 stars"


from django.contrib import admin
from django.utils.html import format_html

# @admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    """Admin configuration for Partner model"""
    list_display = ['name', 'order', 'is_active', 'logo_preview', 'website_link']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    list_editable = ['order', 'is_active']
    
    # ADDED 'created_at' here to resolve the FieldError
    readonly_fields = ['logo_preview', 'website_link', 'created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description')
        }),
        ('Media', {
            'fields': ('logo', 'logo_preview')
        }),
        ('Website', {
            'fields': ('website_url', 'website_link')
        }),
        ('Display Settings', {
            'fields': ('order', 'is_active')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',), # Cleanly hides metadata in Jazzmin unless needed
        }),
    )
    
    def logo_preview(self, obj):
        """Preview of partner logo"""
        if obj.logo:
            return format_html(
                '<img src="{}" width="100" height="auto" style="max-height:50px; object-fit:contain; background: #eee; padding: 2px; border-radius: 4px;" />',
                obj.logo.url
            )
        return "No logo"
    logo_preview.short_description = "Logo Preview"
    
    def website_link(self, obj):
        """Link to partner website"""
        if obj.website_url:
            return format_html(
                '<a href="{}" target="_blank" style="font-weight:bold; color: #007bff;">Visit Website ↗</a>',
                obj.website_url
            )
        return "No website"
    website_link.short_description = "Website"
    
    actions = ['export_urls']
    
    def export_urls(self, request, queryset):
        """Export partner URLs as text file"""
        from django.http import HttpResponse
        urls = '\n'.join([p.website_url for p in queryset if p.website_url])
        response = HttpResponse(urls, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="partner_urls.txt"'
        return response
    export_urls.short_description = "Export website URLs"

class CTASectionAdmin(admin.ModelAdmin):
    """Admin configuration for CTASection model"""
    list_display = ['title', 'button_text', 'is_active', 'has_secondary', 'created_at']
    list_filter = ['is_active', 'button_style']
    search_fields = ['title', 'subtitle', 'description']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Main Content', {
            'fields': ('title', 'subtitle', 'description')
        }),
        ('Background', {
            'fields': ('background_image', 'background_color'),
            'classes': ('collapse',)
        }),
        ('Primary Button', {
            'fields': ('button_text', 'button_url', 'button_style')
        }),
        ('Secondary Button (Optional)', {
            'fields': ('secondary_button_text', 'secondary_button_url'),
            'classes': ('collapse',)
        }),
        ('Display Settings', {
            'fields': ('is_active',)
        }),
        ('Metadata', {
            'fields': ('created_at',)
        }),
    )
    
    def has_secondary(self, obj):
        """Check if has secondary button"""
        return bool(obj.secondary_button_text and obj.secondary_button_url)
    has_secondary.boolean = True
    has_secondary.short_description = "Has Secondary Button"
    
    actions = ['duplicate_cta']
    
    def duplicate_cta(self, request, queryset):
        for cta in queryset:
            cta.pk = None
            cta.title = f"{cta.title} (Copy)"
            cta.save()
        self.message_user(request, f'{queryset.count()} CTAs duplicated.')
    duplicate_cta.short_description = "Duplicate selected CTAs"


# Register all models with their respective admin classes
admin.site.register(HomeSection, HomeSectionAdmin)
admin.site.register(HeroSlide, HeroSlideAdmin)
admin.site.register(FeaturedItem, FeaturedItemAdmin)
admin.site.register(Testimonial, TestimonialAdmin)
admin.site.register(Partner, PartnerAdmin)
admin.site.register(CTASection, CTASectionAdmin)