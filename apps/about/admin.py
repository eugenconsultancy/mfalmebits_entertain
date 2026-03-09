from django.contrib import admin
from .models import (
    AboutSection, TeamMember, Timeline, 
    Achievement, Value, Partner, Testimonial,
    AboutSettings
)

@admin.register(AboutSection)
class AboutSectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'section_type', 'order', 'is_active']
    list_filter = ['section_type', 'is_active']
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['order', 'is_active']


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ['name', 'position', 'order', 'is_leadership', 'is_founder', 'is_active']
    list_filter = ['is_leadership', 'is_founder', 'is_active']
    search_fields = ['name', 'position', 'bio']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['order', 'is_leadership', 'is_founder', 'is_active']


@admin.register(Timeline)
class TimelineAdmin(admin.ModelAdmin):
    list_display = ['year', 'title', 'order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['year', 'title', 'description']
    list_editable = ['order', 'is_active']


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ['title', 'value', 'order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['title', 'description']
    list_editable = ['order', 'is_active']


@admin.register(Value)
class ValueAdmin(admin.ModelAdmin):
    list_display = ['title', 'order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['title', 'description']
    list_editable = ['order', 'is_active']


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ['name', 'partner_type', 'order', 'is_active']
    list_filter = ['partner_type', 'is_active']
    search_fields = ['name', 'description']
    list_editable = ['order', 'is_active']


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['author_name', 'author_organization', 'rating', 'order', 'is_active']
    list_filter = ['rating', 'is_active']
    search_fields = ['author_name', 'content']
    list_editable = ['order', 'is_active']


@admin.register(AboutSettings)
class AboutSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Company Information', {
            'fields': ('company_name', 'tagline', 'founded_year', 'headquarters')
        }),
        ('Contact', {
            'fields': ('contact_email', 'contact_phone')
        }),
        ('Social Media', {
            'fields': ('facebook', 'twitter', 'instagram', 'linkedin', 'youtube')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords')
        }),
    )
    
    def has_add_permission(self, request):
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)
