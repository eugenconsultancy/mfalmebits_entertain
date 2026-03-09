from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import CreateView, FormView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from .models import (
    CollaborationProject, CollaborationCategory, 
    CollaborationSubmission, CollaborationTestimonial,
    CollaborationFAQ
)
from .forms import CollaborationSubmissionForm, CollaborationProjectForm
from utils.seo import SEOMetaGenerator
from utils.schema import get_breadcrumb_schema
import logging

logger = logging.getLogger(__name__)

class CollaborationIndexView(TemplateView):
    """Main collaboration page"""
    template_name = 'collaboration/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get featured projects
        context['featured_projects'] = CollaborationProject.objects.filter(
            status='published',
            featured_image__isnull=False
        ).order_by('-created_at')[:6]
        
        # Get categories
        context['categories'] = CollaborationCategory.objects.filter(is_active=True)
        
        # Get testimonials
        context['testimonials'] = CollaborationTestimonial.objects.filter(
            is_active=True,
            is_featured=True
        )[:6]
        
        # Get FAQs
        context['faqs'] = CollaborationFAQ.objects.filter(is_active=True)[:6]
        
        # Statistics
        context['statistics'] = {
            'projects': CollaborationProject.objects.filter(status='published').count(),
            'collaborators': CollaborationProject.objects.values('creator_name').distinct().count(),
            'countries': 15,  # This would be calculated from actual data
            'categories': CollaborationCategory.objects.filter(is_active=True).count(),
        }
        
        # SEO Metadata
        context['seo_title'] = "Collaborate with MfalmeBits"
        context['seo_description'] = "Join our community of artists, designers, writers, and cultural creators. Collaborate with MfalmeBits to bring African knowledge and creativity to the world."
        context['seo_keywords'] = "collaboration, artists, designers, writers, cultural creators, African creativity"
        
        return context


class CategoryView(ListView):
    """Projects by category"""
    model = CollaborationProject
    template_name = 'collaboration/category.html'
    context_object_name = 'projects'
    paginate_by = 12
    
    def get_category(self):
        return get_object_or_404(CollaborationCategory, slug=self.kwargs['slug'], is_active=True)
    
    def get_queryset(self):
        return CollaborationProject.objects.filter(
            collaboration_category=self.get_category(),
            status='published'
        ).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.get_category()
        
        # SEO Metadata
        context['seo_title'] = f"{context['category'].name} Collaborations - MfalmeBits"
        context['seo_description'] = context['category'].description
        
        return context


class ProjectDetailView(DetailView):
    """Individual collaboration project detail"""
    model = CollaborationProject
    template_name = 'collaboration/project_detail.html'
    context_object_name = 'project'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        return CollaborationProject.objects.filter(status='published')
    
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        self.object.increment_views()
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.object
        
        # Related projects
        context['related_projects'] = CollaborationProject.objects.filter(
            category=project.category,
            status='published'
        ).exclude(id=project.id)[:3]
        
        # SEO Metadata
        context['seo_title'] = f"{project.title} - Collaboration with {project.creator_name}"
        context['seo_description'] = project.short_description
        
        # Schema
        context['breadcrumb_schema'] = get_breadcrumb_schema([
            {'name': 'Home', 'url': '/'},
            {'name': 'Collaboration', 'url': '/collaboration/'},
            {'name': project.title, 'url': ''},
        ], self.request)
        
        return context


class CollaborationSubmissionView(CreateView):
    """Handle collaboration submissions"""
    model = CollaborationSubmission
    form_class = CollaborationSubmissionForm
    template_name = 'collaboration/submit.html'
    success_url = reverse_lazy('collaboration:submission_success')
    
    def form_valid(self, form):
        # Save the submission
        response = super().form_valid(form)
        
        # Capture IP address
        submission = self.object
        submission.ip_address = self.request.META.get('REMOTE_ADDR')
        submission.save()
        
        # Send email notification to admin
        self.send_admin_notification(submission)
        
        # Send auto-reply to submitter
        self.send_auto_reply(submission)
        
        messages.success(self.request, 'Thank you for your submission! Our team will review it and contact you soon.')
        
        return response
    
    def send_admin_notification(self, submission):
        """Send email notification to admin"""
        try:
            subject = f'New Collaboration Submission: {submission.first_name} {submission.last_name}'
            message = f"""
            New collaboration submission received:
            
            Name: {submission.first_name} {submission.last_name}
            Email: {submission.email}
            Type: {submission.get_creator_type_display()}
            Portfolio: {submission.portfolio_link}
            
            Project Idea:
            {submission.project_idea}
            
            View in admin: {self.request.build_absolute_uri('/admin/collaboration/collaborationsubmission/')}
            """
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.COLLABORATION_EMAIL or settings.DEFAULT_FROM_EMAIL],
                fail_silently=True,
            )
        except Exception as e:
            logger.error(f"Failed to send admin notification: {e}")
    
    def send_auto_reply(self, submission):
        """Send auto-reply to the submitter"""
        try:
            subject = 'Thank you for your collaboration interest - MfalmeBits'
            message = f"""
            Dear {submission.first_name},
            
            Thank you for your interest in collaborating with MfalmeBits. We have received your submission and our team will review it shortly.
            
            Here's what happens next:
            1. Our collaboration team will review your proposal
            2. We'll contact you within 5-7 business days
            3. If there's a good fit, we'll schedule a conversation to discuss details
            
            In the meantime, you can:
            - Explore our current collaborations: {self.request.build_absolute_uri('/collaboration/')}
            - Check out our archive: {self.request.build_absolute_uri('/archive/')}
            - Follow us on social media for updates
            
            Best regards,
            The MfalmeBits Collaboration Team
            """
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [submission.email],
                fail_silently=True,
            )
        except Exception as e:
            logger.error(f"Failed to send auto-reply: {e}")


class SubmissionSuccessView(TemplateView):
    """Submission success page"""
    template_name = 'collaboration/success.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['seo_title'] = "Submission Received - MfalmeBits Collaboration"
        return context


class ProjectProposalView(CreateView):
    """Detailed project proposal form"""
    model = CollaborationProject
    form_class = CollaborationProjectForm
    template_name = 'collaboration/propose.html'
    success_url = reverse_lazy('collaboration:proposal_success')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Capture IP
        project = self.object
        project.ip_address = self.request.META.get('REMOTE_ADDR')
        project.save()
        
        # Send notification
        self.send_notification(project)
        
        messages.success(self.request, 'Your project proposal has been submitted successfully!')
        
        return response
    
    def send_notification(self, project):
        """Send notification about new proposal"""
        try:
            subject = f'New Project Proposal: {project.title}'
            message = f"""
            New project proposal received:
            
            Title: {project.title}
            Creator: {project.creator_name}
            Email: {project.creator_email}
            Category: {project.get_category_display()}
            
            Description:
            {project.short_description}
            
            View in admin: {self.request.build_absolute_uri('/admin/collaboration/collaborationproject/')}
            """
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.COLLABORATION_EMAIL or settings.DEFAULT_FROM_EMAIL],
                fail_silently=True,
            )
        except Exception as e:
            logger.error(f"Failed to send proposal notification: {e}")


class ProposalSuccessView(TemplateView):
    """Proposal submission success page"""
    template_name = 'collaboration/proposal_success.html'


class CollaboratorsListView(ListView):
    """List of collaborators"""
    template_name = 'collaboration/collaborators.html'
    context_object_name = 'collaborators'
    
    def get_queryset(self):
        # Get unique creators from published projects
        projects = CollaborationProject.objects.filter(
            status='published'
        ).values('creator_name', 'creator_bio', 'creator_location').distinct()
        
        # This would need a proper model in production
        return projects
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['seo_title'] = "Our Collaborators - MfalmeBits"
        context['seo_description'] = "Meet the talented artists, designers, writers, and cultural creators collaborating with MfalmeBits."
        return context
