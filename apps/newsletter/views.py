from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic.edit import FormView, CreateView
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse, HttpResponse
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.db.models import Q, Count
from .models import (
    Subscriber, NewsletterCampaign, NewsletterIssue, 
    NewsletterArticle, NewsletterCategory, NewsletterSettings,
    NewsletterTemplate, NewsletterTracking, NewsletterLink
)
from .forms import (
    NewsletterSubscribeForm, NewsletterUnsubscribeForm,
    NewsletterPreferencesForm, NewsletterContactForm
)
import logging
import json
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

logger = logging.getLogger(__name__)


class NewsletterSubscribeView(FormView):
    """Handle newsletter subscriptions"""
    template_name = 'newsletter/subscribe.html'
    form_class = NewsletterSubscribeForm
    success_url = '/newsletter/confirm/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['seo_title'] = "Subscribe to Newsletter - MfalmeBits"
        context['seo_description'] = "Subscribe to the MfalmeBits newsletter for updates on African knowledge, culture, and digital resources."
        return context

    def form_valid(self, form):
        email = form.cleaned_data['email']
        first_name = form.cleaned_data.get('first_name', '')
        last_name = form.cleaned_data.get('last_name', '')
        frequency = form.cleaned_data.get('frequency', 'weekly')
        interests = form.cleaned_data.get('interests', [])
        
        # Get or create subscriber
        subscriber, created = Subscriber.objects.get_or_create(
            email=email,
            defaults={
                'first_name': first_name,
                'last_name': last_name,
                'frequency': frequency,
                'interests': interests,
                'source': self.request.GET.get('source', 'website'),
                'source_url': self.request.META.get('HTTP_REFERER', ''),
                'ip_address': self.request.META.get('REMOTE_ADDR'),
            }
        )
        
        if not created:
            # Update existing subscriber
            subscriber.first_name = first_name or subscriber.first_name
            subscriber.last_name = last_name or subscriber.last_name
            subscriber.frequency = frequency
            subscriber.interests = interests
            subscriber.is_active = True
            subscriber.confirmed = False
            subscriber.save()
        
        # Send confirmation email if required
        settings = NewsletterSettings.objects.first()
        if settings and settings.require_confirmation and settings.double_opt_in:
            self.send_confirmation_email(subscriber)
            messages.success(self.request, 'Please check your email to confirm your subscription.')
        else:
            subscriber.confirmed = True
            subscriber.confirmed_at = timezone.now()
            subscriber.save()
            self.send_welcome_email(subscriber)
            messages.success(self.request, 'Thank you for subscribing to our newsletter!')
        
        # Handle AJAX request
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Subscription successful!'
            })
        
        return super().form_valid(form)
    
    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)
        return super().form_invalid(form)
    
    def send_confirmation_email(self, subscriber):
        """Send confirmation email"""
        try:
            token = subscriber.generate_confirmation_token()
            confirm_url = self.request.build_absolute_uri(
                reverse('newsletter:confirm', args=[token])
            )
            
            subject = 'Confirm Your Newsletter Subscription - MfalmeBits'
            message = f"""
            Hi {subscriber.get_full_name()},
            
            Thank you for subscribing to the MfalmeBits newsletter!
            
            Please confirm your subscription by clicking the link below:
            
            {confirm_url}
            
            This link will expire in 48 hours.
            
            If you didn't request this subscription, please ignore this email.
            
            Best regards,
            The MfalmeBits Team
            """
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [subscriber.email],
                fail_silently=True,
            )
        except Exception as e:
            logger.error(f"Failed to send confirmation email: {e}")
    
    def send_welcome_email(self, subscriber):
        """Send welcome email"""
        try:
            settings = NewsletterSettings.objects.first()
            if settings and settings.welcome_email_content:
                subject = settings.welcome_email_subject
                message = settings.welcome_email_content
            else:
                subject = 'Welcome to MfalmeBits Newsletter!'
                message = f"""
                Hi {subscriber.get_full_name()},
                
                Thank you for confirming your subscription to the MfalmeBits newsletter!
                
                You'll now receive updates on African knowledge, culture, and digital resources.
                
                You can manage your preferences at any time:
                {self.request.build_absolute_uri('/newsletter/preferences/')}
                
                Best regards,
                The MfalmeBits Team
                """
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [subscriber.email],
                fail_silently=True,
            )
        except Exception as e:
            logger.error(f"Failed to send welcome email: {e}")


class NewsletterConfirmView(TemplateView):
    """Confirm subscription"""
    template_name = 'newsletter/confirm.html'
    
    def get(self, request, *args, **kwargs):
        token = kwargs.get('token')
        
        try:
            subscriber = Subscriber.objects.get(confirmation_token=token)
            
            if not subscriber.confirmed:
                subscriber.confirmed = True
                subscriber.confirmed_at = timezone.now()
                subscriber.confirmation_token = ''
                subscriber.save()
                
                # Send welcome email
                self.send_welcome_email(subscriber)
                
                messages.success(request, 'Your subscription has been confirmed!')
            else:
                messages.info(request, 'Your subscription was already confirmed.')
                
        except Subscriber.DoesNotExist:
            messages.error(request, 'Invalid confirmation link.')
            return redirect('newsletter:subscribe')
        
        return super().get(request, *args, **kwargs)
    
    def send_welcome_email(self, subscriber):
        """Send welcome email"""
        try:
            settings = NewsletterSettings.objects.first()
            if settings and settings.welcome_email_content:
                subject = settings.welcome_email_subject
                message = settings.welcome_email_content
            else:
                subject = 'Welcome to MfalmeBits Newsletter!'
                message = f"""
                Hi {subscriber.get_full_name()},
                
                Thank you for confirming your subscription to the MfalmeBits newsletter!
                
                You'll now receive updates on African knowledge, culture, and digital resources.
                
                You can manage your preferences at any time:
                {self.request.build_absolute_uri('/newsletter/preferences/')}
                
                Best regards,
                The MfalmeBits Team
                """
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [subscriber.email],
                fail_silently=True,
            )
        except Exception as e:
            logger.error(f"Failed to send welcome email: {e}")


class NewsletterUnsubscribeView(FormView):
    """Handle unsubscriptions"""
    template_name = 'newsletter/unsubscribe.html'
    form_class = NewsletterUnsubscribeForm
    success_url = '/newsletter/unsubscribed/'
    
    def get_initial(self):
        initial = super().get_initial()
        token = self.kwargs.get('token')
        email = self.request.GET.get('email')
        
        if token:
            try:
                subscriber = Subscriber.objects.get(unsubscribe_token=token)
                initial['email'] = subscriber.email
                initial['token'] = token
            except Subscriber.DoesNotExist:
                pass
        elif email:
            initial['email'] = email
        
        return initial
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['seo_title'] = "Unsubscribe from Newsletter - MfalmeBits"
        return context
    
    def form_valid(self, form):
        email = form.cleaned_data['email']
        token = form.cleaned_data.get('token')
        reason = form.cleaned_data.get('reason', '')
        
        try:
            if token:
                subscriber = Subscriber.objects.get(unsubscribe_token=token, email=email)
            else:
                subscriber = Subscriber.objects.get(email=email)
            
            subscriber.is_active = False
            subscriber.unsubscribed_at = timezone.now()
            subscriber.save()
            
            # Record reason if provided
            if reason:
                # You could create an UnsubscribeReason model here
                pass
            
            messages.success(self.request, 'You have been unsubscribed successfully.')
            
        except Subscriber.DoesNotExist:
            messages.error(self.request, 'Email not found in our subscription list.')
            return self.form_invalid(form)
        
        return super().form_valid(form)


class NewsletterUnsubscribedView(TemplateView):
    """Unsubscribe confirmation page"""
    template_name = 'newsletter/unsubscribed.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['seo_title'] = "Unsubscribed - MfalmeBits Newsletter"
        return context


class NewsletterPreferencesView(FormView):
    """Manage subscription preferences"""
    template_name = 'newsletter/preferences.html'
    form_class = NewsletterPreferencesForm
    success_url = '/newsletter/preferences/updated/'
    
    def get_initial(self):
        initial = super().get_initial()
        token = self.kwargs.get('token')
        
        if token:
            try:
                subscriber = Subscriber.objects.get(unsubscribe_token=token, is_active=True)
                initial['email'] = subscriber.email
                initial['first_name'] = subscriber.first_name
                initial['last_name'] = subscriber.last_name
                initial['frequency'] = subscriber.frequency
                initial['interests'] = subscriber.interests
                initial['token'] = token
            except Subscriber.DoesNotExist:
                pass
        
        return initial
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['seo_title'] = "Newsletter Preferences - MfalmeBits"
        return context
    
    def form_valid(self, form):
        email = form.cleaned_data['email']
        token = form.cleaned_data.get('token')
        
        try:
            if token:
                subscriber = Subscriber.objects.get(unsubscribe_token=token, email=email)
            else:
                subscriber = Subscriber.objects.get(email=email, is_active=True)
            
            subscriber.first_name = form.cleaned_data['first_name']
            subscriber.last_name = form.cleaned_data['last_name']
            subscriber.frequency = form.cleaned_data['frequency']
            subscriber.interests = form.cleaned_data['interests']
            subscriber.save()
            
            messages.success(self.request, 'Your preferences have been updated.')
            
        except Subscriber.DoesNotExist:
            messages.error(self.request, 'Subscriber not found.')
            return self.form_invalid(form)
        
        return super().form_valid(form)


class NewsletterPreferencesUpdatedView(TemplateView):
    """Preferences update confirmation"""
    template_name = 'newsletter/preferences_updated.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['seo_title'] = "Preferences Updated - MfalmeBits Newsletter"
        return context


class NewsletterArchiveView(ListView):
    """Newsletter archive"""
    model = NewsletterIssue
    template_name = 'newsletter/archive.html'
    context_object_name = 'issues'
    paginate_by = 12
    
    def get_queryset(self):
        return NewsletterIssue.objects.all().order_by('-issue_number', '-sent_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['seo_title'] = "Newsletter Archive - MfalmeBits"
        context['seo_description'] = "Browse our archive of past newsletters featuring African knowledge, culture, and digital resources."
        
        # Get recent campaigns
        context['recent_campaigns'] = NewsletterCampaign.objects.filter(
            status='sent'
        ).order_by('-sent_at')[:5]
        
        return context


class NewsletterIssueView(DetailView):
    """View a specific newsletter issue"""
    model = NewsletterIssue
    template_name = 'newsletter/issue.html'
    context_object_name = 'issue'
    
    def get_object(self):
        return get_object_or_404(
            NewsletterIssue,
            campaign__slug=self.kwargs['campaign_slug'],
            issue_number=self.kwargs['issue_number']
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        issue = self.object
        
        # Track view if tracking pixel is requested
        if self.request.GET.get('track') == 'open':
            self.track_open(issue)
        
        context['seo_title'] = f"{issue.subject} - MfalmeBits Newsletter"
        context['seo_description'] = f"Issue #{issue.issue_number} of the MfalmeBits newsletter."
        
        return context
    
    def track_open(self, issue):
        """Track newsletter open"""
        # This would be called from a tracking pixel
        pass


class NewsletterArticleView(DetailView):
    """View newsletter article"""
    model = NewsletterArticle
    template_name = 'newsletter/article.html'
    context_object_name = 'article'
    slug_url_kwarg = 'slug'
    
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        self.object.views_count += 1
        self.object.save(update_fields=['views_count'])
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        article = self.object
        
        # Related articles
        context['related_articles'] = NewsletterArticle.objects.filter(
            category=article.category,
            is_active=True
        ).exclude(id=article.id)[:3]
        
        # SEO
        context['seo_title'] = article.title
        context['seo_description'] = article.excerpt
        
        return context


class NewsletterCategoryView(ListView):
    """Articles by category"""
    model = NewsletterArticle
    template_name = 'newsletter/category.html'
    context_object_name = 'articles'
    paginate_by = 10
    
    def get_category(self):
        return get_object_or_404(NewsletterCategory, slug=self.kwargs['slug'], is_active=True)
    
    def get_queryset(self):
        return NewsletterArticle.objects.filter(
            category=self.get_category(),
            is_active=True
        ).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.get_category()
        context['seo_title'] = f"{context['category'].name} - MfalmeBits Newsletter"
        context['seo_description'] = context['category'].description
        return context


@method_decorator(csrf_exempt, name='dispatch')
class NewsletterTrackView(TemplateView):
    """Tracking endpoint for newsletter events"""
    
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            event_type = data.get('event')
            issue_id = data.get('issue_id')
            subscriber_id = data.get('subscriber_id')
            link_id = data.get('link_id')
            
            issue = NewsletterIssue.objects.get(id=issue_id)
            subscriber = Subscriber.objects.get(id=subscriber_id)
            
            # Create tracking event
            tracking = NewsletterTracking.objects.create(
                issue=issue,
                subscriber=subscriber,
                event_type=event_type,
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:200]
            )
            
            # Update counts
            if event_type == 'open':
                issue.opens += 1
                issue.save(update_fields=['opens'])
            elif event_type == 'click' and link_id:
                try:
                    link = NewsletterLink.objects.get(id=link_id)
                    link.click_count += 1
                    link.save(update_fields=['click_count'])
                    tracking.link = link
                    tracking.save()
                    
                    issue.clicks += 1
                    issue.save(update_fields=['clicks'])
                except NewsletterLink.DoesNotExist:
                    pass
            
            return JsonResponse({'success': True})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)


class NewsletterContactView(FormView):
    """Contact form for newsletter team"""
    template_name = 'newsletter/contact.html'
    form_class = NewsletterContactForm
    success_url = '/newsletter/contact/success/'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['seo_title'] = "Contact Newsletter Team - MfalmeBits"
        return context
    
    def form_valid(self, form):
        name = form.cleaned_data['name']
        email = form.cleaned_data['email']
        subject = form.cleaned_data['subject']
        message = form.cleaned_data['message']
        
        # Send email to newsletter team
        try:
            send_mail(
                f"Newsletter Contact: {subject}",
                f"From: {name} <{email}>\n\n{message}",
                settings.DEFAULT_FROM_EMAIL,
                [settings.NEWSLETTER_EMAIL or settings.DEFAULT_FROM_EMAIL],
                fail_silently=True,
            )
            messages.success(self.request, 'Your message has been sent. We\'ll respond shortly.')
        except Exception as e:
            logger.error(f"Failed to send contact email: {e}")
            messages.error(self.request, 'An error occurred. Please try again later.')
        
        return super().form_valid(form)
