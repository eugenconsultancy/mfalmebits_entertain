from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import FormView, CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.http import FileResponse, Http404
from .models import LicensingPlan, InstitutionalInquiry, InstitutionalBrochure
from .forms import InstitutionalInquiryForm
from utils.seo import SEOMetaGenerator
from utils.schema import get_breadcrumb_schema, get_organization_schema
import logging

logger = logging.getLogger(__name__)

class InstitutionalIndexView(TemplateView):
    """Main institutional licensing page"""
    template_name = 'institutional/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all active plans grouped by type
        plans = LicensingPlan.objects.filter(is_active=True)
        
        # Group plans by type
        grouped_plans = {}
        for plan in plans:
            if plan.plan_type not in grouped_plans:
                grouped_plans[plan.plan_type] = []
            grouped_plans[plan.plan_type].append(plan)
        
        context['grouped_plans'] = grouped_plans
        context['featured_plans'] = plans.filter(is_featured=True)[:3]
        
        # Get brochures
        context['brochures'] = InstitutionalBrochure.objects.filter(is_active=True)
        
        # Testimonials (you can create a model for these later)
        context['testimonials'] = [
            {
                'institution': 'University of Nairobi',
                'quote': 'MfalmeBits has transformed our African Studies department with comprehensive resources.',
                'author': 'Dr. Jane Kamau',
                'position': 'Head of African Studies'
            },
            {
                'institution': 'African Leadership Academy',
                'quote': 'The curriculum kits are exceptional and have enhanced our students\' learning experience.',
                'author': 'Peter Mwangi',
                'position': 'Academic Director'
            },
            {
                'institution': 'National Library of Kenya',
                'quote': 'Our patrons now have access to an unparalleled collection of African knowledge.',
                'author': 'Sarah Odhiambo',
                'position': 'Chief Librarian'
            },
        ]
        
        # Statistics
        context['statistics'] = {
            'institutions': 150,
            'users': 50000,
            'resources': 10000,
            'countries': 25,
        }
        
        # SEO Metadata
        context['seo_title'] = "Institutional Licensing - MfalmeBits"
        context['seo_description'] = "Bring African knowledge to your institution with MfalmeBits licensing plans. Perfect for schools, universities, libraries, and organizations."
        context['seo_keywords'] = "institutional licensing, educational resources, academic library, African studies, curriculum"
        
        # Schema
        context['breadcrumb_schema'] = get_breadcrumb_schema([
            {'name': 'Home', 'url': '/'},
            {'name': 'Institutional', 'url': ''},
        ], self.request)
        
        return context


class PlanDetailView(DetailView):
    """Individual licensing plan details"""
    model = LicensingPlan
    template_name = 'institutional/plan_detail.html'
    context_object_name = 'plan'
    slug_url_kwarg = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        plan = self.object
        
        # Similar plans
        context['similar_plans'] = LicensingPlan.objects.filter(
            plan_type=plan.plan_type,
            is_active=True
        ).exclude(id=plan.id)[:3]
        
        # SEO Metadata
        context['seo_title'] = SEOMetaGenerator.generate_title(plan)
        context['seo_description'] = SEOMetaGenerator.generate_description(plan)
        
        # Schema
        context['breadcrumb_schema'] = get_breadcrumb_schema([
            {'name': 'Home', 'url': '/'},
            {'name': 'Institutional', 'url': '/institutional/'},
            {'name': plan.name, 'url': ''},
        ], self.request)
        
        return context


class InstitutionalInquiryView(CreateView):
    """Handle institutional inquiries"""
    model = InstitutionalInquiry
    form_class = InstitutionalInquiryForm
    template_name = 'institutional/inquiry.html'
    success_url = reverse_lazy('institutional:inquiry_success')
    
    def get_initial(self):
        initial = super().get_initial()
        # Pre-fill plan if provided in URL
        plan_id = self.request.GET.get('plan')
        if plan_id:
            try:
                plan = LicensingPlan.objects.get(id=plan_id)
                initial['plan'] = plan
                initial['plan_name'] = plan.name
            except LicensingPlan.DoesNotExist:
                pass
        return initial
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['plans'] = LicensingPlan.objects.filter(is_active=True)
        context['seo_title'] = "Request Institutional Information - MfalmeBits"
        return context
    
    def form_valid(self, form):
        # Save the inquiry
        response = super().form_valid(form)
        
        # Capture metadata
        inquiry = self.object
        inquiry.ip_address = self.request.META.get('REMOTE_ADDR')
        inquiry.user_agent = self.request.META.get('HTTP_USER_AGENT', '')
        inquiry.source = self.request.GET.get('utm_source', 'website')
        inquiry.utm_source = self.request.GET.get('utm_source', '')
        inquiry.utm_medium = self.request.GET.get('utm_medium', '')
        inquiry.utm_campaign = self.request.GET.get('utm_campaign', '')
        inquiry.save()
        
        # Send email notification to admin
        self.send_admin_notification(inquiry)
        
        # Send auto-reply to inquirer
        self.send_auto_reply(inquiry)
        
        messages.success(self.request, 'Thank you for your interest! Our institutional team will contact you within 24 hours.')
        
        return response
    
    def send_admin_notification(self, inquiry):
        """Send email notification to admin"""
        try:
            subject = f'New Institutional Inquiry: {inquiry.institution_name}'
            message = f"""
            New institutional inquiry received:
            
            Institution: {inquiry.institution_name}
            Type: {inquiry.get_institution_type_display()}
            Contact: {inquiry.contact_person}
            Email: {inquiry.email}
            Phone: {inquiry.phone}
            Plan: {inquiry.plan.name if inquiry.plan else 'Not specified'}
            Users: {inquiry.number_of_users}
            
            Message:
            {inquiry.message}
            
            View in admin: {self.request.build_absolute_uri(inquiry.get_absolute_url())}
            """
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.INSTITUTIONAL_EMAIL or settings.DEFAULT_FROM_EMAIL],
                fail_silently=True,
            )
        except Exception as e:
            logger.error(f"Failed to send admin notification: {e}")
    
    def send_auto_reply(self, inquiry):
        """Send auto-reply to the inquirer"""
        try:
            subject = 'Thank you for your interest in MfalmeBits Institutional Licensing'
            message = f"""
            Dear {inquiry.contact_person},
            
            Thank you for your interest in MfalmeBits institutional licensing. We have received your inquiry and our team will review it shortly.
            
            Here's a summary of your inquiry:
            - Institution: {inquiry.institution_name}
            - Number of users: {inquiry.number_of_users}
            - Interested in: {inquiry.content_types}
            
            What happens next?
            1. Our institutional specialist will review your requirements
            2. We'll contact you within 24 hours to discuss your needs
            3. We'll provide a customized proposal based on your requirements
            
            In the meantime, you can:
            - Download our institutional brochure: {self.request.build_absolute_uri('/institutional/brochure/')}
            - Explore our public archive: {self.request.build_absolute_uri('/archive/')}
            - View sample resources: {self.request.build_absolute_uri('/library/')}
            
            If you have any immediate questions, please reply to this email or contact us at institutional@mfalmebits.com.
            
            Best regards,
            The MfalmeBits Institutional Team
            """
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [inquiry.email],
                fail_silently=True,
            )
        except Exception as e:
            logger.error(f"Failed to send auto-reply: {e}")


class InquirySuccessView(TemplateView):
    """Inquiry submission success page"""
    template_name = 'institutional/success.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['seo_title'] = "Inquiry Received - MfalmeBits"
        context['seo_description'] = "Thank you for your interest in MfalmeBits institutional licensing."
        return context


class BrochureDownloadView(DetailView):
    """Handle brochure downloads"""
    model = InstitutionalBrochure
    slug_field = 'id'
    slug_url_kwarg = 'pk'
    
    def get(self, request, *args, **kwargs):
        brochure = self.get_object()
        
        # Check if file exists
        if not brochure.file:
            raise Http404("Brochure file not found")
        
        # Increment download count
        brochure.increment_download()
        
        # Return file response
        response = FileResponse(brochure.file.open('rb'))
        response['Content-Disposition'] = f'attachment; filename="{brochure.file.name}"'
        return response


class PricingCalculatorView(TemplateView):
    """Interactive pricing calculator"""
    template_name = 'institutional/calculator.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['plans'] = LicensingPlan.objects.filter(is_active=True)
        context['seo_title'] = "Pricing Calculator - MfalmeBits Institutional"
        return context
    
    def post(self, request, *args, **kwargs):
        """Calculate price based on parameters"""
        import json
        from django.http import JsonResponse
        
        data = json.loads(request.body)
        plan_id = data.get('plan_id')
        users = int(data.get('users', 1))
        
        try:
            plan = LicensingPlan.objects.get(id=plan_id, is_active=True)
            
            # Calculate price
            base_price = float(plan.price_per_year)
            setup_fee = float(plan.setup_fee)
            
            # Volume discount
            if users > 100:
                discount = 0.20  # 20% discount for 100+ users
            elif users > 50:
                discount = 0.15  # 15% discount for 50+ users
            elif users > 20:
                discount = 0.10  # 10% discount for 20+ users
            elif users > 10:
                discount = 0.05  # 5% discount for 10+ users
            else:
                discount = 0
            
            total = (base_price * users * (1 - discount)) + setup_fee
            
            return JsonResponse({
                'success': True,
                'base_price': base_price,
                'setup_fee': setup_fee,
                'users': users,
                'discount': discount * 100,
                'total': round(total, 2),
                'per_user': round(total / users, 2),
            })
            
        except LicensingPlan.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Plan not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})


class FAQView(TemplateView):
    """Institutional FAQ page"""
    template_name = 'institutional/faq.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # FAQ data (can be moved to database later)
        context['faqs'] = [
            {
                'question': 'What types of institutions can license MfalmeBits content?',
                'answer': 'We work with K-12 schools, universities, public libraries, NGOs, corporations, and government agencies worldwide.'
            },
            {
                'question': 'How does pricing work for institutions?',
                'answer': 'Pricing is based on the institution type, number of users, and selected plan. We offer volume discounts for larger institutions. Contact our team for a customized quote.'
            },
            {
                'question': 'Can we access content across multiple campuses?',
                'answer': 'Yes! Our institutional licenses can be configured for multi-campus access. We offer IP authentication, proxy server support, and single sign-on integration.'
            },
            {
                'question': 'What content is included in institutional access?',
                'answer': 'Institutions get access to our complete Knowledge Archive, Digital Library, and curriculum resources. Some premium content may require additional licensing.'
            },
            {
                'question': 'Do you provide usage statistics and reports?',
                'answer': 'Yes, all institutional plans include access to our analytics dashboard showing usage statistics, popular content, and user engagement metrics.'
            },
            {
                'question': 'How do students and faculty access the content?',
                'answer': 'Access can be configured via IP authentication (on-campus), proxy server (off-campus), or individual accounts with institutional email verification.'
            },
            {
                'question': 'What kind of technical support do you provide?',
                'answer': 'Support levels vary by plan, ranging from email support to dedicated account managers with phone support and training sessions.'
            },
            {
                'question': 'Can we integrate MfalmeBits with our learning management system?',
                'answer': 'Yes, we offer API access for integration with popular LMS platforms including Canvas, Blackboard, and Moodle.'
            },
        ]
        
        context['seo_title'] = "Frequently Asked Questions - MfalmeBits Institutional"
        context['seo_description'] = "Find answers to common questions about MfalmeBits institutional licensing, pricing, access methods, and support."
        
        return context


class CaseStudiesView(ListView):
    """Institutional case studies"""
    template_name = 'institutional/case_studies.html'
    context_object_name = 'case_studies'
    
    def get_queryset(self):
        # This would be a model in production
        return [
            {
                'title': 'University of Nairobi African Studies Transformation',
                'institution': 'University of Nairobi',
                'country': 'Kenya',
                'challenge': 'Limited access to contemporary African research materials',
                'solution': 'Full institutional license with campus-wide access',
                'results': '5,000+ students served, 200+ research papers published',
                'image': 'case-study-1.jpg',
                'quote': 'MfalmeBits has revolutionized how we teach African Studies.',
                'author': 'Dr. Jane Kamau',
                'link': '#'
            },
            {
                'title': 'African Leadership Academy Curriculum Enhancement',
                'institution': 'African Leadership Academy',
                'country': 'South Africa',
                'challenge': 'Need for culturally relevant educational materials',
                'solution': 'Curriculum kits and specialized content packages',
                'results': '100% of teachers using materials, 40% increase in student engagement',
                'image': 'case-study-2.jpg',
                'quote': 'The curriculum kits align perfectly with our pan-African focus.',
                'author': 'Peter Mwangi',
                'link': '#'
            },
            {
                'title': 'National Library of Kenya Digital Expansion',
                'institution': 'National Library of Kenya',
                'country': 'Kenya',
                'challenge': 'Limited digital resources for patrons',
                'solution': 'Public library license with remote access',
                'results': '50,000+ downloads, 15 branches accessing content',
                'image': 'case-study-3.jpg',
                'quote': 'Our patrons now have world-class African knowledge at their fingertips.',
                'author': 'Sarah Odhiambo',
                'link': '#'
            },
        ]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['seo_title'] = "Case Studies - MfalmeBits Institutional"
        context['seo_description'] = "See how institutions around the world are using MfalmeBits to enhance their African knowledge resources."
        return context
