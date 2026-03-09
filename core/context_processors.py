from django.conf import settings
from django.templatetags.static import static

def seo_settings(request):
    """Add SEO settings to template context"""
    return {
        'default_og_image': request.build_absolute_uri(static('images/og-default.jpg')),
        'site_name': 'MfalmeBits',
        'site_description': 'African Knowledge Archive & Digital Library',
        'site_keywords': 'African knowledge, cultural archive, digital library, African identity',
        'twitter_site': '@mfalmebits',
    }

def organization_schema(request):
    """Add organization schema to context"""
    return {
        'organization_schema': {
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
    }
