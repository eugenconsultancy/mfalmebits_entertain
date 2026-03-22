from django.views.generic import TemplateView
from django.db.models import Q
from .models import (
    HomeSection, HeroSlide, FeaturedItem, 
    Testimonial, Partner, CTASection
)
from apps.archive.models import ArchiveEntry, Theme
from apps.library.models import DigitalProduct, ProductCategory
from apps.blog.models import Post
from utils.seo import SEOMetaGenerator
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connections
from django.db.utils import OperationalError
import json
from utils.schema import get_organization_schema, get_website_schema

class HomeView(TemplateView):
    """Enhanced homepage view with all dynamic sections"""
    template_name = 'home/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all active sections
        context['sections'] = HomeSection.objects.filter(is_active=True)
        
        # Get hero slides
        context['hero_slides'] = HeroSlide.objects.filter(is_active=True)
        
        # Get featured items with their actual content
        featured_items = FeaturedItem.objects.filter(is_active=True)
        enhanced_items = []
        for item in featured_items:
            item_data = {
                'title': item.title,
                'description': item.description,
                'image': item.image,
                'image_alt': item.image_alt,
                'url': item.get_absolute_url(),
                'item_type': item.item_type,
            }
            
            # Get additional data from related content
            if item.item_type == 'archive' and item.content_id:
                try:
                    entry = ArchiveEntry.objects.get(id=item.content_id)
                    item_data['theme'] = entry.theme.name if entry.theme else None
                except ArchiveEntry.DoesNotExist:
                    pass
            elif item.item_type == 'product' and item.content_id:
                try:
                    product = DigitalProduct.objects.get(id=item.content_id)
                    item_data['price'] = str(product.price)
                    item_data['format'] = product.format
                except DigitalProduct.DoesNotExist:
                    pass
            elif item.item_type == 'blog' and item.content_id:
                try:
                    post = Post.objects.get(id=item.content_id)
                    item_data['date'] = post.published_date
                    item_data['author'] = post.author.username
                except Post.DoesNotExist:
                    pass
            
            enhanced_items.append(item_data)
        
        context['featured_items'] = enhanced_items
        
        # Get testimonials
        context['testimonials'] = Testimonial.objects.filter(is_active=True)
        
        # Get partners
        context['partners'] = Partner.objects.filter(is_active=True)
        
        # Get CTA section
        context['cta'] = CTASection.objects.filter(is_active=True).first()
        
        # Get recent content
        context['recent_archive'] = ArchiveEntry.objects.filter(
            is_active=True
        ).order_by('-published_date')[:6]
        
        context['recent_products'] = DigitalProduct.objects.filter(
            is_active=True
        ).order_by('-created_at')[:4]
        
        context['recent_posts'] = Post.objects.filter(
            is_active=True
        ).order_by('-published_date')[:3]
        
        # Get popular themes and categories
        context['popular_themes'] = Theme.objects.filter(
            archiveentry__isnull=False
        ).distinct()[:8]
        
        context['popular_categories'] = ProductCategory.objects.filter(
            digitalproduct__isnull=False
        ).distinct()[:6]
        
        # SEO Metadata
        context['seo_title'] = SEOMetaGenerator.generate_title(
            self, 
            "Home | African Knowledge Archive"
        )
        context['seo_description'] = "MfalmeBits - Your premier destination for African knowledge, cultural archive, digital library, and future thinking resources."
        context['seo_keywords'] = "African knowledge, cultural archive, digital library, African history, African philosophy, Ubuntu, Sankofa"
        
        # Schema.org data
        context['organization_schema'] = get_organization_schema(self.request)
        context['website_schema'] = get_website_schema(self.request)
        
        return context


class AboutView(TemplateView):
    """About page view"""
    template_name = 'home/about.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get partners for about page
        context['partners'] = Partner.objects.filter(is_active=True)
        
        # Get testimonials
        context['testimonials'] = Testimonial.objects.filter(is_active=True)[:6]
        
        # SEO Metadata
        context['seo_title'] = SEOMetaGenerator.generate_title(
            self, 
            "About Us | MfalmeBits - African Knowledge Archive"
        )
        context['seo_description'] = "Learn about MfalmeBits, your premier destination for African knowledge, cultural archive, and digital library resources. Discover our mission, vision, and team."
        context['seo_keywords'] = "about MfalmeBits, African knowledge archive, cultural preservation, digital library mission"
        
        return context


class ContactView(TemplateView):
    """Contact page view"""
    template_name = 'home/contact.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get CTA section for contact page
        context['cta'] = CTASection.objects.filter(is_active=True).first()
        
        # SEO Metadata
        context['seo_title'] = SEOMetaGenerator.generate_title(
            self, 
            "Contact Us | MfalmeBits"
        )
        context['seo_description'] = "Get in touch with the MfalmeBits team. We'd love to hear from you! Contact us for inquiries, support, or collaboration opportunities."
        context['seo_keywords'] = "contact MfalmeBits, African archive support, digital library contact"
        
        return context


class FAQView(TemplateView):
    """Frequently Asked Questions page"""
    template_name = 'home/faq.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # FAQ categories and questions would typically come from a model
        # For now, using static FAQ data
        context['faq_categories'] = [
            {
                'name': 'General',
                'questions': [
                    {'question': 'What is MfalmeBits?', 'answer': 'MfalmeBits is a premier digital platform dedicated to preserving and sharing African knowledge, culture, history, and creative works through our archive, digital library, and blog.'},
                    {'question': 'Is MfalmeBits free to use?', 'answer': 'Many of our resources are freely accessible. Some premium content in our digital library may require purchase or subscription.'},
                    {'question': 'How can I contribute to MfalmeBits?', 'answer': 'We welcome contributions! You can contact us through our contact page to discuss collaboration opportunities.'},
                ]
            },
            {
                'name': 'Account & Access',
                'questions': [
                    {'question': 'How do I create an account?', 'answer': 'Click on the "Sign Up" button in the navigation bar and fill in your details to create a free account.'},
                    {'question': 'I forgot my password. What should I do?', 'answer': 'Use the "Forgot Password" link on the login page to reset your password.'},
                ]
            },
            {
                'name': 'Content & Usage',
                'questions': [
                    {'question': 'Can I download content from the archive?', 'answer': 'Some content may be available for download depending on copyright restrictions and your access level.'},
                    {'question': 'How do I cite MfalmeBits content?', 'answer': 'Each archive entry includes citation information. Look for the citation button or section on individual item pages.'},
                ]
            }
        ]
        
        # SEO Metadata
        context['seo_title'] = SEOMetaGenerator.generate_title(
            self, 
            "Frequently Asked Questions | MfalmeBits"
        )
        context['seo_description'] = "Find answers to commonly asked questions about MfalmeBits, our archive, digital library, services, and how to make the most of our platform."
        context['seo_keywords'] = "MfalmeBits FAQ, African archive help, digital library questions"
        
        return context


class PrivacyPolicyView(TemplateView):
    """Privacy Policy page"""
    template_name = 'home/privacy_policy.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Last updated date
        context['last_updated'] = 'January 1, 2025'
        
        # SEO Metadata
        context['seo_title'] = SEOMetaGenerator.generate_title(
            self, 
            "Privacy Policy | MfalmeBits"
        )
        context['seo_description'] = "Read our privacy policy to understand how we collect, use, and protect your personal information when you use MfalmeBits platform and services."
        context['seo_keywords'] = "MfalmeBits privacy policy, data protection, privacy terms"
        
        return context


class TermsOfServiceView(TemplateView):
    """Terms of Service page"""
    template_name = 'home/terms_of_service.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Last updated date
        context['last_updated'] = 'January 1, 2025'
        
        # SEO Metadata
        context['seo_title'] = SEOMetaGenerator.generate_title(
            self, 
            "Terms of Service | MfalmeBits"
        )
        context['seo_description'] = "Read our terms of service before using MfalmeBits platform and services. These terms govern your use of our website, archive, and digital library."
        context['seo_keywords'] = "MfalmeBits terms of service, terms and conditions, user agreement"
        
        return context
    

@csrf_exempt
def health_check(request):
    """Health check endpoint for Railway"""
    health_status = {
        'status': 'healthy',
        'timestamp': __import__('django.utils.timezone').now().isoformat(),
        'checks': {}
    }
    
    # Check database
    try:
        connections['default'].ensure_connection()
        health_status['checks']['database'] = 'connected'
    except OperationalError:
        health_status['checks']['database'] = 'disconnected'
        health_status['status'] = 'unhealthy'
    
    # Check cache (if Redis is configured)
    try:
        from django.core.cache import cache
        cache.set('health_check', 'ok', 1)
        if cache.get('health_check') == 'ok':
            health_status['checks']['cache'] = 'operational'
        else:
            health_status['checks']['cache'] = 'error'
    except Exception:
        health_status['checks']['cache'] = 'not_configured'
    
    # Return appropriate HTTP status
    if health_status['status'] == 'healthy':
        return JsonResponse(health_status, status=200)
    else:
        return JsonResponse(health_status, status=500)