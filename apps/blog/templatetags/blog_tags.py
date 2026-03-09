from django import template
from django.db.models import Count
from ..models import Category, Post, Series
from taggit.models import Tag

register = template.Library()

@register.simple_tag
def get_categories():
    """Get all categories with post counts"""
    return Category.objects.filter(
        is_active=True,
        post__status='published'
    ).annotate(
        post_count=Count('post')
    ).filter(post_count__gt=0).order_by('order', 'name')

@register.simple_tag
def get_popular_tags(limit=10):
    """Get popular tags"""
    return Tag.objects.filter(
        post__status='published'
    ).annotate(
        post_count=Count('taggit_taggeditem_items')
    ).order_by('-post_count')[:limit]

@register.simple_tag
def get_series():
    """Get all active series"""
    return Series.objects.filter(is_active=True).annotate(
        post_count=Count('posts')
    ).order_by('order', 'title')

@register.simple_tag
def get_archive_years():
    """Get years with published posts"""
    return Post.objects.filter(
        status='published',
        is_active=True
    ).dates('published_date', 'year', order='DESC')

@register.simple_tag
def get_month_names():
    """Get month names for archive navigation"""
    import calendar
    return {i: calendar.month_name[i] for i in range(1, 13)}

@register.simple_tag(takes_context=True)
def remove_filter(context, *filters):
    """Remove specified filters from current query string"""
    request = context['request']
    params = request.GET.copy()
    
    for filter_name in filters:
        if filter_name in params:
            del params[filter_name]
    
    if params:
        return '?' + params.urlencode()
    return ''

@register.filter
def get_item(dictionary, key):
    """Get item from dictionary by key"""
    return dictionary.get(key)

@register.simple_tag
def get_recent_posts(limit=5):
    """Get recent posts"""
    return Post.objects.filter(
        status='published',
        is_active=True
    ).order_by('-published_date')[:limit]

@register.simple_tag
def get_featured_posts(limit=3):
    """Get featured posts"""
    return Post.objects.filter(
        status='published',
        is_active=True,
        is_featured=True
    ).order_by('-published_date')[:limit]

@register.inclusion_tag('blog/partials/post_card.html')
def render_post_card(post):
    """Render a post card partial"""
    return {'post': post}