from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get item from dictionary by key"""
    return dictionary.get(str(key), 0)

@register.filter
def multiply(value, arg):
    """Multiply value by argument"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def currency(value):
    """Format as currency"""
    try:
        return f"${float(value):.2f}"
    except (ValueError, TypeError):
        return "$0.00"

@register.simple_tag
def rating_stars(rating):
    """Generate star rating HTML"""
    stars = ''
    for i in range(1, 6):
        if i <= rating:
            stars += '<i class="fas fa-star text-warning"></i>'
        else:
            stars += '<i class="far fa-star text-warning"></i>'
    return stars

@register.inclusion_tag('library/product_card.html')
def product_card(product, **kwargs):
    """Render product card"""
    return {
        'product': product,
        'show_add_to_cart': kwargs.get('show_add_to_cart', True),
        'show_wishlist': kwargs.get('show_wishlist', True),
    }

@register.inclusion_tag('library/breadcrumb.html')
def library_breadcrumb(category=None, product=None):
    """Render library breadcrumb"""
    items = [('Home', '/'), ('Library', '/library/')]
    if category:
        items.append((category.name, category.get_absolute_url()))
    if product:
        items.append((product.title, ''))
    return {'items': items}