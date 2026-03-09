"""
SEO utilities for meta tags and content optimization
"""

from django.utils.html import strip_tags
from django.utils.text import Truncator
import re

class SEOMetaGenerator:
    """Generate SEO-optimized meta tags"""
    
    @staticmethod
    def generate_title(obj, site_name="MfalmeBits", max_length=60):
        """
        Generate SEO-optimized title (50-60 chars)
        """
        if hasattr(obj, 'seo_title') and obj.seo_title:
            base = obj.seo_title
        elif hasattr(obj, 'title'):
            base = obj.title
        else:
            base = str(obj)
            
        full_title = f"{base} | {site_name}"
        
        if len(full_title) > max_length:
            # Truncate the base part
            available = max_length - len(site_name) - 3  # 3 for " | "
            truncated = Truncator(base).chars(available)
            return f"{truncated} | {site_name}"
        
        return full_title
    
    @staticmethod
    def generate_description(obj, max_length=160):
        """
        Generate meta description from content
        """
        if hasattr(obj, 'seo_description') and obj.seo_description:
            description = obj.seo_description
        elif hasattr(obj, 'excerpt') and obj.excerpt:
            description = strip_tags(obj.excerpt)
        elif hasattr(obj, 'content') and obj.content:
            description = strip_tags(obj.content)[:200]
        elif hasattr(obj, 'description'):
            description = strip_tags(obj.description)
        else:
            return "MfalmeBits - African Knowledge Archive & Digital Library"
        
        # Clean description
        description = re.sub(r'\s+', ' ', description).strip()
        
        if len(description) > max_length:
            return Truncator(description).chars(max_length - 3) + "..."
        
        return description
    
    @staticmethod
    def generate_keywords(obj):
        """
        Generate meta keywords from tags and categories
        """
        keywords = []
        
        if hasattr(obj, 'tags'):
            keywords.extend([tag.name for tag in obj.tags.all()])
        
        if hasattr(obj, 'theme') and obj.theme:
            keywords.append(obj.theme.name)
        
        if hasattr(obj, 'category') and obj.category:
            keywords.append(obj.category.name)
        
        # Add base keywords if none found
        if not keywords:
            return "African knowledge, cultural archive, digital library, African identity, future thinking"
        
        # Limit to 10 keywords
        return ', '.join(keywords[:10])
    
    @staticmethod
    def generate_image_alt(obj):
        """
        Generate SEO-friendly image alt text
        """
        if hasattr(obj, 'image_alt') and obj.image_alt:
            return obj.image_alt
        elif hasattr(obj, 'title'):
            return f"{obj.title} - MfalmeBits"
        else:
            return "MfalmeBits African Knowledge Archive"


class SEOAnalyzer:
    """Analyze content for SEO optimization"""
    
    @staticmethod
    def analyze_title(title):
        """Check title SEO quality"""
        length = len(title)
        issues = []
        
        if length < 30:
            issues.append("Title is too short (under 30 characters)")
        elif length > 60:
            issues.append("Title is too long (over 60 characters)")
        
        if title[0].islower():
            issues.append("Title should start with capital letter")
        
        return {
            'length': length,
            'is_optimal': 30 <= length <= 60,
            'issues': issues
        }
    
    @staticmethod
    def analyze_description(description):
        """Check meta description SEO quality"""
        length = len(description)
        issues = []
        
        if length < 120:
            issues.append("Description is too short (under 120 characters)")
        elif length > 160:
            issues.append("Description is too long (over 160 characters)")
        
        return {
            'length': length,
            'is_optimal': 120 <= length <= 160,
            'issues': issues
        }
    
    @staticmethod
    def analyze_headings(html_content):
        """Analyze heading structure"""
        import re
        
        # Find all headings
        h1_count = len(re.findall(r'<h1[^>]*>', html_content, re.IGNORECASE))
        h2_count = len(re.findall(r'<h2[^>]*>', html_content, re.IGNORECASE))
        h3_count = len(re.findall(r'<h3[^>]*>', html_content, re.IGNORECASE))
        
        issues = []
        
        if h1_count == 0:
            issues.append("No H1 tag found")
        elif h1_count > 1:
            issues.append(f"Multiple H1 tags found ({h1_count})")
        
        if h2_count == 0 and h3_count > 0:
            issues.append("H3 tags without H2 parent")
        
        return {
            'h1': h1_count,
            'h2': h2_count,
            'h3': h3_count,
            'issues': issues
        }
    
    @staticmethod
    def calculate_readability(text):
        """Calculate Flesch-Kincaid readability score"""
        if not text:
            return 0
        
        # Count sentences (roughly)
        sentences = len(re.findall(r'[.!?]+', text))
        if sentences == 0:
            sentences = 1
        
        # Count words
        words = len(text.split())
        if words == 0:
            return 0
        
        # Count syllables (rough approximation)
        syllables = 0
        for word in text.split():
            word_syllables = len(re.findall(r'[aeiouy]+', word.lower()))
            syllables += max(1, word_syllables)
        
        # Flesch Reading Ease score
        score = 206.835 - 1.015 * (words / sentences) - 84.6 * (syllables / words)
        
        # Clamp to 0-100 range
        return max(0, min(100, score))
