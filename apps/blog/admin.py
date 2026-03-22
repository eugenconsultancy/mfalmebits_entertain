from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Category, Post, Comment, Series, 
    NewsletterSubscription, Author, BlogSettings
)

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    fields = ['name', 'email', 'content', 'is_approved', 'is_spam']
    readonly_fields = ['ip_address', 'user_agent', 'created_at']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'order', 'post_count', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['order', 'is_active']
    
    def post_count(self, obj):
        return obj.post_set.count()
    post_count.short_description = 'Posts'


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'author', 'published_date', 'status', 'views_count', 'is_featured']
    list_filter = ['status', 'is_featured', 'category', 'author', 'published_date']
    search_fields = ['title', 'content', 'excerpt']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['views_count', 'created_at', 'updated_date', 'reading_time']
    list_editable = ['status', 'is_featured']
    inlines = [CommentInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'category', 'author')
        }),
        ('Content', {
            'fields': ('excerpt', 'content')
        }),
        ('Media', {
            'fields': ('featured_image', 'image_alt', 'image_caption', 'video_url')
        }),
        ('Metadata', {
            'fields': ('tags', 'reading_time', 'views_count')
        }),
        ('Dates', {
            'fields': ('published_date', 'created_at', 'updated_date')
        }),
        ('Status', {
            'fields': ('status', 'is_featured', 'is_active', 'allow_comments')
        }),
        ('SEO', {
            'fields': ('seo_title', 'seo_description', 'canonical_url')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:
            if not obj.author_id:
                obj.author = request.user
        super().save_model(request, obj, form, change)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'post', 'created_at', 'is_approved', 'is_spam']
    list_filter = ['is_approved', 'is_spam', 'created_at']
    search_fields = ['name', 'email', 'content']
    # FIX: Removed 'updated_at' - this field does not exist in Comment model
    readonly_fields = ['ip_address', 'user_agent', 'created_at']
    list_editable = ['is_approved', 'is_spam']
    
    fieldsets = (
        ('Comment', {
            'fields': ('post', 'parent', 'name', 'email', 'website', 'content')
        }),
        ('Moderation', {
            'fields': ('is_approved', 'is_spam')
        }),
        ('Metadata', {
            'fields': ('ip_address', 'user_agent', 'created_at')
        }),
    )
    
    actions = ['approve_comments', 'mark_as_spam']
    
    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True)
    approve_comments.short_description = "Approve selected comments"
    
    def mark_as_spam(self, request, queryset):
        queryset.update(is_spam=True, is_approved=False)
    mark_as_spam.short_description = "Mark selected as spam"


@admin.register(Series)
class SeriesAdmin(admin.ModelAdmin):
    list_display = ['title', 'order', 'post_count', 'is_active']
    list_filter = ['is_active']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ['posts']
    
    def post_count(self, obj):
        return obj.posts.count()
    post_count.short_description = 'Posts'


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['user', 'position', 'show_on_about', 'order']
    list_filter = ['show_on_about']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'bio']
    list_editable = ['show_on_about', 'order']
    
    fieldsets = (
        ('User', {
            'fields': ('user', 'position', 'bio')
        }),
        ('Profile', {
            'fields': ('avatar',)
        }),
        ('Social Media', {
            'fields': ('twitter', 'linkedin', 'website')
        }),
        ('Settings', {
            'fields': ('show_on_about', 'order')
        }),
    )


@admin.register(NewsletterSubscription)
class NewsletterSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['email', 'first_name', 'is_active', 'subscribed_at']
    list_filter = ['is_active', 'source']
    search_fields = ['email', 'first_name']
    readonly_fields = ['ip_address', 'subscribed_at', 'unsubscribed_at']
    
    actions = ['activate_subscriptions', 'deactivate_subscriptions']
    
    def activate_subscriptions(self, request, queryset):
        queryset.update(is_active=True)
    activate_subscriptions.short_description = "Activate selected subscriptions"
    
    def deactivate_subscriptions(self, request, queryset):
        from django.utils import timezone
        queryset.update(is_active=False, unsubscribed_at=timezone.now())
    deactivate_subscriptions.short_description = "Deactivate selected subscriptions"


@admin.register(BlogSettings)
class BlogSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('General Settings', {
            'fields': ('posts_per_page', 'comments_per_page')
        }),
        ('Comment Moderation', {
            'fields': ('moderate_comments', 'allow_guest_comments', 
                      'notify_on_comments', 'comment_notification_email')
        }),
        ('Social Media', {
            'fields': ('twitter_handle', 'facebook_page', 'instagram_handle')
        }),
        ('SEO', {
            'fields': ('blog_title', 'blog_description', 'blog_keywords')
        }),
    )
    
    def has_add_permission(self, request):
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)