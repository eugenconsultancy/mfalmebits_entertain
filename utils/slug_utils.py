"""
Slug generation utilities for SEO-friendly URLs
"""

import re
from unidecode import unidecode
from django.utils.text import slugify

def generate_seo_slug(text, model=None, max_length=50):
    """
    Generate SEO-optimized slug
    
    Args:
        text: The text to convert to slug
        model: Django model to check uniqueness against (optional)
        max_length: Maximum length of slug
    
    Returns:
        Unique SEO-friendly slug
    """
    if not text:
        return ''
    
    # Convert to ASCII
    text = unidecode(text)
    
    # Use Django's slugify as base
    slug = slugify(text)
    
    # Remove special characters and ensure clean format
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = slug.lower().strip()
    slug = re.sub(r'[-\s]+', '-', slug)
    
    # Truncate
    slug = slug[:max_length].rstrip('-')
    
    # Ensure uniqueness if model provided
    if model:
        slug = ensure_unique_slug(slug, model)
    
    return slug


def ensure_unique_slug(slug, model, slug_field='slug'):
    """
    Ensure slug is unique by appending numbers if necessary
    """
    original_slug = slug
    counter = 1
    
    kwargs = {slug_field: slug}
    while model.objects.filter(**kwargs).exists():
        slug = f"{original_slug}-{counter}"
        kwargs = {slug_field: slug}
        counter += 1
        
        # Safety break
        if counter > 100:
            slug = f"{original_slug}-{counter}"
            break
    
    return slug


def generate_hierarchical_slug(parent_slug, child_title, model=None):
    """
    Generate hierarchical slug (e.g., parent-slug/child-slug)
    """
    child_slug = generate_seo_slug(child_title)
    
    if parent_slug:
        full_slug = f"{parent_slug}/{child_slug}"
    else:
        full_slug = child_slug
    
    if model:
        full_slug = ensure_unique_slug(full_slug, model)
    
    return full_slug


def slug_from_url(url):
    """
    Extract slug from URL
    """
    return url.strip('/').split('/')[-1]


def is_valid_slug(slug):
    """
    Check if slug is valid format
    """
    pattern = r'^[a-z0-9]+(?:-[a-z0-9]+)*(?:/[a-z0-9]+(?:-[a-z0-9]+)*)*$'
    return bool(re.match(pattern, slug))
