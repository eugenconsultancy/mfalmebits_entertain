"""
Schema.org structured data generators
"""

from django.templatetags.static import static

def get_article_schema(obj, request):
    """
    Generate JSON-LD schema for articles
    """
    schema = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": obj.title,
        "description": getattr(obj, 'excerpt', obj.content)[:200] if hasattr(obj, 'content') else obj.description,
        "author": {
            "@type": "Person",
            "name": getattr(obj, 'author', "MfalmeBits"),
        },
        "publisher": {
            "@type": "Organization",
            "name": "MfalmeBits",
            "logo": {
                "@type": "ImageObject",
                "url": request.build_absolute_uri(static('images/logo.png'))
            }
        },
        "mainEntityOfPage": request.build_absolute_uri(),
    }
    
    # Add image if available
    if hasattr(obj, 'featured_image') and obj.featured_image:
        schema["image"] = request.build_absolute_uri(obj.featured_image.url)
    elif hasattr(obj, 'cover_image') and obj.cover_image:
        schema["image"] = request.build_absolute_uri(obj.cover_image.url)
    
    # Add dates if available
    if hasattr(obj, 'published_date') and obj.published_date:
        schema["datePublished"] = obj.published_date.isoformat()
    if hasattr(obj, 'updated_at') and obj.updated_at:
        schema["dateModified"] = obj.updated_at.isoformat()
    elif hasattr(obj, 'updated_date') and obj.updated_date:
        schema["dateModified"] = obj.updated_date.isoformat()
    
    # Add keywords from tags
    if hasattr(obj, 'tags'):
        tags = [tag.name for tag in obj.tags.all()]
        if tags:
            schema["keywords"] = ', '.join(tags)
    
    return schema


def get_product_schema(product, request):
    """
    Generate JSON-LD schema for digital products
    """
    schema = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": product.title,
        "description": getattr(product, 'short_description', product.description)[:200],
        "offers": {
            "@type": "Offer",
            "price": str(product.price),
            "priceCurrency": "USD",
            "availability": "https://schema.org/InStock",
            "url": request.build_absolute_uri(),
        },
        "brand": {
            "@type": "Brand",
            "name": "MfalmeBits"
        },
    }
    
    # Add image if available
    if hasattr(product, 'cover_image') and product.cover_image:
        schema["image"] = request.build_absolute_uri(product.cover_image.url)
    
    # Add category if available
    if hasattr(product, 'category') and product.category:
        schema["category"] = product.category.name
    
    return schema


def get_breadcrumb_schema(items, request):
    """
    Generate JSON-LD schema for breadcrumbs
    """
    item_list_elements = []
    
    for position, item in enumerate(items, start=1):
        element = {
            "@type": "ListItem",
            "position": position,
            "name": item['name'],
        }
        
        if 'url' in item and item['url']:
            element["item"] = request.build_absolute_uri(item['url'])
        
        item_list_elements.append(element)
    
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": item_list_elements
    }


def get_organization_schema(request):
    """
    Generate JSON-LD schema for organization
    """
    return {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": "MfalmeBits",
        "url": request.build_absolute_uri('/'),
        "logo": request.build_absolute_uri(static('images/logo.png')),
        "sameAs": [
            "https://twitter.com/mfalmebits",
            "https://instagram.com/mfalmebits",
            "https://facebook.com/mfalmebits",
            "https://linkedin.com/company/mfalmebits",
        ],
        "contactPoint": {
            "@type": "ContactPoint",
            "telephone": "+254-XXX-XXXX",
            "contactType": "customer service",
            "email": "info@mfalmebits.com",
        }
    }


def get_website_schema(request):
    """
    Generate JSON-LD schema for website
    """
    return {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": "MfalmeBits",
        "url": request.build_absolute_uri('/'),
        "potentialAction": {
            "@type": "SearchAction",
            "target": {
                "@type": "EntryPoint",
                "urlTemplate": request.build_absolute_uri('/search/?q={search_term_string}')
            },
            "query-input": "required name=search_term_string"
        }
    }
