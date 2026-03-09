from django import template
from django.db.models import Count, Sum

register = template.Library()

@register.simple_tag
def total_saved_items(user):
    """Get total saved items count for user"""
    try:
        # Only try to import if the model exists
        from ..models import SavedItem
        return SavedItem.objects.filter(user=user).count()
    except (ImportError, AttributeError):
        return 0

@register.simple_tag
def total_downloads(user):
    """Get total downloads count for user"""
    try:
        from ..models import DownloadHistory
        return DownloadHistory.objects.filter(user=user).count()
    except (ImportError, AttributeError):
        return 0

@register.simple_tag
def total_logins(user):
    """Get total logins count for user"""
    try:
        from ..models import LoginHistory
        return LoginHistory.objects.filter(user=user).count()
    except (ImportError, AttributeError):
        return 0

@register.simple_tag
def total_purchases(user):
    """Get total purchases count for user"""
    # Return 0 since PurchaseHistory doesn't exist
    return 0

@register.simple_tag
def recent_saved_items(user, limit=5):
    """Get recent saved items for user"""
    try:
        from ..models import SavedItem
        return SavedItem.objects.filter(user=user).order_by('-created_at')[:limit]
    except (ImportError, AttributeError):
        return []

@register.simple_tag
def recent_downloads(user, limit=5):
    """Get recent downloads for user"""
    try:
        from ..models import DownloadHistory
        return DownloadHistory.objects.filter(user=user).order_by('-download_date')[:limit]
    except (ImportError, AttributeError):
        return []

@register.simple_tag
def recent_purchases(user, limit=5):
    """Get recent purchases for user"""
    return []

@register.simple_tag
def recent_logins(user, limit=5):
    """Get recent login activity for user"""
    try:
        from ..models import LoginHistory
        return LoginHistory.objects.filter(user=user).order_by('-login_time')[:limit]
    except (ImportError, AttributeError):
        return []