from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic.edit import FormView, CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.core.mail import send_mail
from django.conf import settings
from django.db import models
from django.http import JsonResponse, HttpResponse
from .models import ContactMessage, FAQ, Office, SupportTicket, SupportReply, ContactSettings
from .forms import ContactForm, SupportTicketForm, SupportReplyForm
from utils.seo import SEOMetaGenerator
from utils.schema import get_breadcrumb_schema
import logging

logger = logging.getLogger(__name__)

class ContactIndexView(TemplateView):
    """Main contact page"""
    template_name = 'contact/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get contact settings
        context['settings'] = ContactSettings.objects.first()
        
        # Get offices
        context['offices'] = Office.objects.filter(is_active=True)
        
        # Get FAQs (first 6)
        context['faqs'] = FAQ.objects.filter(is_active=True)[:6]
        
        # Contact form
        context['form'] = ContactForm()
        
        # SEO Metadata
        context['seo_title'] = "Contact Us - MfalmeBits"
        context['seo_description'] = "Get in touch with MfalmeBits. We're here to help with questions about our knowledge archive, digital library, institutional licensing, and collaborations."
        context['seo_keywords'] = "contact us, support, help, customer service, MfalmeBits"
        
        # Schema
        context['breadcrumb_schema'] = get_breadcrumb_schema([
            {'name': 'Home', 'url': '/'},
            {'name': 'Contact', 'url': ''},
        ], self.request)
        
        return context


class ContactSubmitView(FormView):
    """Handle contact form submission"""
    form_class = ContactForm
    
    def form_valid(self, form):
        # Save contact message
        message = form.save(commit=False)
        
        # Capture metadata
        message.ip_address = self.request.META.get('REMOTE_ADDR')
        message.user_agent = self.request.META.get('HTTP_USER_AGENT', '')[:200]
        message.source = self.request.GET.get('source', 'website')
        message.save()
        
        # Send email notification to admin
        self.send_admin_notification(message)
        
        # Send auto-reply to user
        if self.should_send_auto_reply():
            self.send_auto_reply(message)
        
        # Handle newsletter subscription
        if form.cleaned_data.get('subscribe_newsletter'):
            self.handle_newsletter_subscription(form.cleaned_data['email'])
        
        # Return JSON response for AJAX requests
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Thank you for your message. We\'ll get back to you soon!'
            })
        
        messages.success(self.request, 'Thank you for your message. We\'ll get back to you soon!')
        
        # Redirect back to contact page
        return redirect('contact:index')
    
    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)
        
        # Add form errors to messages
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{field}: {error}")
        
        return redirect('contact:index')
    
    def send_admin_notification(self, message):
        """Send email notification to admin"""
        try:
            settings_obj = ContactSettings.objects.first()
            admin_email = settings_obj.contact_email if settings_obj else settings.DEFAULT_FROM_EMAIL
            
            subject = f'New Contact Form Submission: {message.get_subject_type_display()}'
            body = f"""
            New contact form submission:
            
            Name: {message.name}
            Email: {message.email}
            Phone: {message.phone or 'Not provided'}
            Subject: {message.get_subject_type_display()} - {message.subject}
            
            Message:
            {message.message}
            
            View in admin: {self.request.build_absolute_uri(message.get_absolute_url())}
            """
            
            send_mail(
                subject,
                body,
                settings.DEFAULT_FROM_EMAIL,
                [admin_email],
                fail_silently=True,
            )
        except Exception as e:
            logger.error(f"Failed to send admin notification: {e}")
    
    def send_auto_reply(self, message):
        """Send auto-reply to the user"""
        try:
            settings_obj = ContactSettings.objects.first()
            
            if settings_obj and settings_obj.enable_auto_reply:
                subject = settings_obj.auto_reply_subject
                body = settings_obj.auto_reply_message
            else:
                subject = 'Thank you for contacting MfalmeBits'
                body = f"""
                Dear {message.name},
                
                Thank you for contacting MfalmeBits. We have received your message and will get back to you as soon as possible.
                
                Your reference: {message.get_subject_type_display()} - {message.subject}
                
                In the meantime, you might find answers in our FAQ section:
                {self.request.build_absolute_uri('/contact/#faq')}
                
                Best regards,
                The MfalmeBits Team
                """
            
            send_mail(
                subject,
                body,
                settings.DEFAULT_FROM_EMAIL,
                [message.email],
                fail_silently=True,
            )
        except Exception as e:
            logger.error(f"Failed to send auto-reply: {e}")
    
    def should_send_auto_reply(self):
        """Check if auto-reply should be sent"""
        settings_obj = ContactSettings.objects.first()
        return settings_obj and settings_obj.enable_auto_reply
    
    def handle_newsletter_subscription(self, email):
        """Handle newsletter subscription"""
        try:
            from apps.blog.models import NewsletterSubscription
            
            sub, created = NewsletterSubscription.objects.get_or_create(
                email=email,
                defaults={
                    'ip_address': self.request.META.get('REMOTE_ADDR'),
                    'source': 'contact'
                }
            )
            
            if not created and not sub.is_active:
                sub.is_active = True
                sub.save()
                
        except Exception as e:
            logger.error(f"Failed to handle newsletter subscription: {e}")


class FAQView(ListView):
    """FAQ page"""
    model = FAQ
    template_name = 'contact/faq.html'
    context_object_name = 'faqs'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = FAQ.objects.filter(is_active=True)
        
        # Category filter
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        # Search
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                models.Q(question__icontains=q) | 
                models.Q(answer__icontains=q)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get categories with counts
        from django.db.models import Count
        context['categories'] = FAQ.objects.filter(is_active=True).values('category').annotate(
            count=Count('id')
        ).order_by('category')
        
        # Current filters
        context['current_filters'] = {
            'category': self.request.GET.get('category', ''),
            'q': self.request.GET.get('q', ''),
        }
        
        # Popular FAQs
        context['popular_faqs'] = FAQ.objects.filter(is_active=True).order_by('-views_count')[:5]
        
        # SEO Metadata
        context['seo_title'] = "Frequently Asked Questions - MfalmeBits"
        context['seo_description'] = "Find answers to common questions about MfalmeBits, our knowledge archive, digital library, institutional licensing, and more."
        
        return context


class FAQDetailView(DetailView):
    """Individual FAQ detail"""
    model = FAQ
    template_name = 'contact/faq_detail.html'
    context_object_name = 'faq'
    
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        self.object.increment_views()
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Related FAQs (same category)
        context['related_faqs'] = FAQ.objects.filter(
            category=self.object.category,
            is_active=True
        ).exclude(id=self.object.id)[:5]
        
        # SEO Metadata
        context['seo_title'] = self.object.question
        context['seo_description'] = self.object.answer[:160] if self.object.answer else None
        
        return context


class SupportTicketView(CreateView):
    """Create support ticket"""
    model = SupportTicket
    form_class = SupportTicketForm
    template_name = 'contact/support.html'
    success_url = reverse_lazy('contact:support_success')
    
    def get_initial(self):
        initial = super().get_initial()
        if self.request.user.is_authenticated:
            initial['name'] = self.request.user.get_full_name() or self.request.user.username
            initial['email'] = self.request.user.email
        return initial
    
    def form_valid(self, form):
        ticket = form.save(commit=False)
        
        # Set user if authenticated
        if self.request.user.is_authenticated:
            ticket.user = self.request.user
        
        # Capture metadata
        ticket.ip_address = self.request.META.get('REMOTE_ADDR')
        
        # Save ticket
        ticket.save()
        
        # Send notification
        self.send_notifications(ticket)
        
        messages.success(self.request, f'Support ticket created. Your ticket ID is: {ticket.ticket_id}')
        
        return super().form_valid(form)
    
    def send_notifications(self, ticket):
        """Send notifications for new ticket"""
        try:
            settings_obj = ContactSettings.objects.first()
            support_email = settings_obj.support_email if settings_obj else settings.DEFAULT_FROM_EMAIL
            
            # Notify support team
            subject = f'New Support Ticket: {ticket.ticket_id}'
            body = f"""
            New support ticket created:
            
            Ticket ID: {ticket.ticket_id}
            Name: {ticket.name}
            Email: {ticket.email}
            Category: {ticket.get_category_display()}
            Priority: {ticket.get_priority_display()}
            
            Subject: {ticket.subject}
            
            Description:
            {ticket.description}
            
            View in admin: {self.request.build_absolute_uri('/admin/contact/supportticket/')}
            """
            
            send_mail(
                subject,
                body,
                settings.DEFAULT_FROM_EMAIL,
                [support_email],
                fail_silently=True,
            )
            
            # Auto-reply to customer
            subject = f'Support Ticket Created: {ticket.ticket_id}'
            body = f"""
            Dear {ticket.name},
            
            Thank you for contacting MfalmeBits support. Your ticket has been created and will be processed shortly.
            
            Ticket ID: {ticket.ticket_id}
            Subject: {ticket.subject}
            
            You can track the status of your ticket by replying to this email with your ticket ID in the subject line.
            
            Best regards,
            The MfalmeBits Support Team
            """
            
            send_mail(
                subject,
                body,
                settings.DEFAULT_FROM_EMAIL,
                [ticket.email],
                fail_silently=True,
            )
            
        except Exception as e:
            logger.error(f"Failed to send ticket notifications: {e}")


class SupportTicketDetailView(DetailView):
    """View support ticket and replies"""
    model = SupportTicket
    template_name = 'contact/ticket_detail.html'
    context_object_name = 'ticket'
    slug_field = 'ticket_id'
    slug_url_kwarg = 'ticket_id'
    
    def get_queryset(self):
        if self.request.user.is_authenticated:
            return SupportTicket.objects.filter(
                models.Q(user=self.request.user) | models.Q(email=self.request.user.email)
            )
        return SupportTicket.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reply_form'] = SupportReplyForm()
        return context


class SupportReplyView(CreateView):
    """Add reply to support ticket"""
    model = SupportReply
    form_class = SupportReplyForm
    
    def form_valid(self, form):
        ticket = get_object_or_404(SupportTicket, ticket_id=self.kwargs['ticket_id'])
        
        reply = form.save(commit=False)
        reply.ticket = ticket
        
        if self.request.user.is_authenticated:
            reply.user = self.request.user
        
        reply.ip_address = self.request.META.get('REMOTE_ADDR')
        reply.save()
        
        # Update ticket status
        ticket.status = 'waiting' if reply.is_internal else 'in_progress'
        ticket.save(update_fields=['status'])
        
        # Send email notification if not internal
        if not reply.is_internal:
            self.send_reply_notification(ticket, reply)
        
        messages.success(self.request, 'Reply added successfully.')
        
        return redirect('contact:ticket_detail', ticket_id=ticket.ticket_id)
    
    def send_reply_notification(self, ticket, reply):
        """Send email notification for reply"""
        try:
            subject = f'Support Ticket Update: {ticket.ticket_id}'
            body = f"""
            Your support ticket has been updated:
            
            Ticket ID: {ticket.ticket_id}
            
            New message:
            {reply.message}
            
            View your ticket: {self.request.build_absolute_uri(ticket.get_absolute_url())}
            """
            
            send_mail(
                subject,
                body,
                settings.DEFAULT_FROM_EMAIL,
                [ticket.email],
                fail_silently=True,
            )
        except Exception as e:
            logger.error(f"Failed to send reply notification: {e}")


class SupportSuccessView(TemplateView):
    """Support ticket creation success page"""
    template_name = 'contact/support_success.html'


class OfficesView(ListView):
    """Office locations page"""
    model = Office
    template_name = 'contact/offices.html'
    context_object_name = 'offices'
    
    def get_queryset(self):
        return Office.objects.filter(is_active=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['headquarters'] = Office.objects.filter(is_headquarters=True, is_active=True).first()
        context['seo_title'] = "Our Offices - MfalmeBits"
        return context