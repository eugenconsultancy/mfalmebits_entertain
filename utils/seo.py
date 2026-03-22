from django.utils.text import slugify
import re

class SEOMetaGenerator:
    """Generate SEO metadata for models"""
    
    @staticmethod
    def generate_title(obj, default=None):
        """Generate SEO title from object"""
        if hasattr(obj, 'seo_title') and obj.seo_title:
            return obj.seo_title
        if hasattr(obj, 'title'):
            return obj.title
        if default:
            return default
        return str(obj)
    
    @staticmethod
    def generate_description(obj, max_length=160):
        """Generate SEO description"""
        if hasattr(obj, 'seo_description') and obj.seo_description:
            return obj.seo_description[:max_length]
        if hasattr(obj, 'excerpt'):
            return obj.excerpt[:max_length]
        if hasattr(obj, 'description'):
            return obj.description[:max_length]
        return ''
    
    @staticmethod
    def generate_keywords(obj):
        """Generate SEO keywords"""
        if hasattr(obj, 'seo_keywords') and obj.seo_keywords:
            return obj.seo_keywords
        return ''


class SEOAnalyzer:
    """Analyze content for SEO optimization"""
    
    @staticmethod
    def analyze_title(title):
        """Analyze title length and keywords"""
        return {
            'length': len(title),
            'optimal': 50 <= len(title) <= 60,
            'score': 100 if 50 <= len(title) <= 60 else max(0, 100 - abs(55 - len(title)) * 2)
        }
    
    @staticmethod
    def analyze_description(description):
        """Analyze meta description"""
        return {
            'length': len(description),
            'optimal': 150 <= len(description) <= 160,
            'score': 100 if 150 <= len(description) <= 160 else max(0, 100 - abs(155 - len(description)))
        }
    
    @staticmethod
    def analyze_headings(content):
        """Count heading tags in content"""
        h1_count = content.count('<h1') if '<h1' in content else 0
        h2_count = content.count('<h2') if '<h2' in content else 0
        return {
            'h1_count': h1_count,
            'h2_count': h2_count,
            'has_single_h1': h1_count == 1
        }
    
    @staticmethod
    def calculate_readability(content):
        """Calculate Flesch-Kincaid readability score"""
        import re
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', content)
        words = len(text.split())
        sentences = len(re.split(r'[.!?]+', text))
        if sentences == 0:
            return 0
        return round(206.835 - 1.015 * (words / sentences) - 84.6 * (sum(len(w) for w in text.split()) / words), 1)