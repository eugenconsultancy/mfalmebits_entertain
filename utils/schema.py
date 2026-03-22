from django.urls import reverse

def get_article_schema(obj, request):
    """Generate Article Schema.org markup"""
    schema = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": obj.title,
        "datePublished": obj.published_date.isoformat() if hasattr(obj, 'published_date') else None,
        "dateModified": obj.updated_at.isoformat() if hasattr(obj, 'updated_at') else None,
        "author": {
            "@type": "Person",
            "name": getattr(obj, 'author', 'MfalmeBits')
        }
    }
    
    if hasattr(obj, 'featured_image') and obj.featured_image:
        schema["image"] = request.build_absolute_uri(obj.featured_image.url)
    
    return schema


def get_breadcrumb_schema(items, request):
    """Generate BreadcrumbList Schema.org markup"""
    schema = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": []
    }
    
    for i, item in enumerate(items, 1):
        schema["itemListElement"].append({
            "@type": "ListItem",
            "position": i,
            "name": item['name'],
            "item": request.build_absolute_uri(item['url']) if item['url'] else None
        })
    
    return schema


def get_organization_schema(request):
    """Generate Organization Schema.org markup"""
    return {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": "MfalmeBits",
        "url": request.build_absolute_uri('/'),
        "logo": request.build_absolute_uri('/static/images/logo.png'),
        "sameAs": [
            "https://twitter.com/mfalmebits",
            "https://facebook.com/mfalmebits",
            "https://instagram.com/mfalmebits",
            "https://linkedin.com/company/mfalmebits"
        ]
    }


def get_website_schema(request):
    """Generate WebSite Schema.org markup"""
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


def get_product_schema(product, request):
    """Generate Product Schema.org markup"""
    schema = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": product.title,
        "description": product.short_description,
        "sku": str(product.id),
        "offers": {
            "@type": "Offer",
            "price": float(product.get_current_price()),
            "priceCurrency": "USD",
            "availability": "https://schema.org/InStock" if product.stock != 0 else "https://schema.org/OutOfStock"
        }
    }
    
    if product.cover_image:
        schema["image"] = request.build_absolute_uri(product.cover_image.url)
    
    return schema