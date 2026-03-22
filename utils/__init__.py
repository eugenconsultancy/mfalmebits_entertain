"""
MfalmeBits Utility Module
Centralized utilities for SEO, slug generation, schema, decorators, and image optimization
"""

# Export all utilities for easier imports
from .seo import SEOMetaGenerator, SEOAnalyzer
from .slug_utils import generate_seo_slug
from .schema import (
    get_article_schema,
    get_breadcrumb_schema,
    get_organization_schema,
    get_website_schema,
    get_product_schema
)
from .decorators import ajax_required, staff_required
from .image_optimizer import optimize_uploaded_image

__all__ = [
    'SEOMetaGenerator',
    'SEOAnalyzer',
    'generate_seo_slug',
    'get_article_schema',
    'get_breadcrumb_schema',
    'get_organization_schema',
    'get_website_schema',
    'get_product_schema',
    'ajax_required',
    'staff_required',
    'optimize_uploaded_image'
]