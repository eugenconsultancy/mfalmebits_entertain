from django.utils.text import slugify
from unidecode import unidecode

def generate_seo_slug(text, model, slug_field='slug', max_length=250):
    """
    Generate a unique SEO-friendly slug for a model instance.
    
    Args:
        text: The text to slugify
        model: The Django model class
        slug_field: The name of the slug field (default: 'slug')
        max_length: Maximum length of the slug (default: 250)
    
    Returns:
        A unique slug string
    """
    # Convert to ASCII, remove accents
    ascii_text = unidecode(text)
    
    # Generate base slug
    base_slug = slugify(ascii_text)
    if not base_slug:
        base_slug = 'untitled'
    
    # Truncate to max_length
    base_slug = base_slug[:max_length]
    
    # Check for uniqueness
    slug = base_slug
    counter = 1
    
    while model.objects.filter(**{slug_field: slug}).exists():
        suffix = f"-{counter}"
        max_slug_length = max_length - len(suffix)
        slug = f"{base_slug[:max_slug_length]}{suffix}"
        counter += 1
    
    return slug