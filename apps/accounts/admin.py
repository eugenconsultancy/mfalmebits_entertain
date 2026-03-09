from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile, LoginHistory, SavedItem, UserPreference, DownloadHistory, PaymentMethod, AccountSettings

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'


class UserPreferenceInline(admin.StackedInline):
    model = UserPreference
    can_delete = False
    verbose_name_plural = 'Preferences'


class UserAdmin(BaseUserAdmin):
    inlines = [ProfileInline, UserPreferenceInline]
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_active', 'date_joined']
    list_filter = ['is_active', 'is_staff', 'groups']


@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'ip_address', 'device_type', 'browser', 'login_time', 'login_successful']
    list_filter = ['login_successful', 'device_type', 'browser', 'os']
    search_fields = ['user__username', 'user__email', 'ip_address']
    readonly_fields = ['login_time']


@admin.register(SavedItem)
class SavedItemAdmin(admin.ModelAdmin):
    list_display = ['user', 'item_type', 'item_id', 'created_at']
    list_filter = ['item_type']
    search_fields = ['user__username', 'notes', 'tags']


@admin.register(DownloadHistory)
class DownloadHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'item_title', 'item_type', 'download_count', 'last_downloaded']
    list_filter = ['item_type']
    search_fields = ['user__username', 'item_title']


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ['user', 'method_type', 'is_default', 'is_active', 'created_at']
    list_filter = ['method_type', 'is_default', 'is_active']
    search_fields = ['user__username', 'card_last4', 'paypal_email', 'mpesa_phone']


@admin.register(AccountSettings)
class AccountSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Registration', {
            'fields': ('allow_registration', 'require_email_verification', 'allow_social_login')
        }),
        ('Security', {
            'fields': ('password_min_length', 'password_require_uppercase', 
                      'password_require_numbers', 'password_require_special')
        }),
        ('Session', {
            'fields': ('session_timeout', 'max_login_attempts', 'lockout_duration')
        }),
        ('Defaults', {
            'fields': ('default_user_group', 'default_email_notifications')
        }),
    )
    
    def has_add_permission(self, request):
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
