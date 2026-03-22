from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import models
from django.views.generic import TemplateView, DetailView, ListView, UpdateView
from django.views.generic.edit import FormView, CreateView
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.http import JsonResponse, Http404
from django.db.models import Q, Count
from django.core.mail import send_mail
from django.conf import settings
from .models import (
    Profile, LoginHistory, SavedItem, UserPreference, 
    DownloadHistory, PaymentMethod, AccountSettings
)
from .forms import (
    UserRegistrationForm, UserLoginForm, UserProfileForm,
    UserChangePasswordForm, PasswordResetRequestForm, PasswordResetConfirmForm,
    UserPreferencesForm, SavedItemForm
)
from utils.decorators import ajax_required
import logging

logger = logging.getLogger(__name__)


class LoginView(FormView):
    """User login view"""
    template_name = 'accounts/login.html'
    form_class = UserLoginForm
    success_url = reverse_lazy('accounts:dashboard')
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('accounts:dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        remember_me = form.cleaned_data.get('remember_me', False)
        
        user = authenticate(self.request, username=username, password=password)
        
        if user is not None:
            if user.is_active:
                login(self.request, user)
                
                # Set session expiry
                if not remember_me:
                    self.request.session.set_expiry(0)
                
                # Record login history
                self.record_login_history(user)
                
                # Update profile
                user.profile.login_count += 1
                user.profile.last_active = timezone.now()
                user.profile.save()
                
                messages.success(self.request, f"Welcome back, {user.get_full_name() or user.username}!")
                
                # FIX: Redirect to next page if specified, otherwise to success_url
                next_url = self.request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                
                return super().form_valid(form)
            else:
                messages.error(self.request, "This account is inactive.")
        else:
            messages.error(self.request, "Invalid username or password.")
        
        return self.form_invalid(form)
    
    def record_login_history(self, user):
        """Record login attempt in history"""
        try:
            ip = self.request.META.get('REMOTE_ADDR')
            user_agent = self.request.META.get('HTTP_USER_AGENT', '')
            
            # Parse user agent for device info (simplified)
            device_type = 'desktop'
            browser = 'Unknown'
            os = 'Unknown'
            
            if 'Mobile' in user_agent:
                device_type = 'mobile'
            elif 'Tablet' in user_agent:
                device_type = 'tablet'
            
            if 'Chrome' in user_agent:
                browser = 'Chrome'
            elif 'Firefox' in user_agent:
                browser = 'Firefox'
            elif 'Safari' in user_agent:
                browser = 'Safari'
            
            if 'Windows' in user_agent:
                os = 'Windows'
            elif 'Mac' in user_agent:
                os = 'macOS'
            elif 'Linux' in user_agent:
                os = 'Linux'
            elif 'Android' in user_agent:
                os = 'Android'
            elif 'iOS' in user_agent:
                os = 'iOS'
            
            LoginHistory.objects.create(
                user=user,
                ip_address=ip,
                user_agent=user_agent[:200],
                device_type=device_type,
                browser=browser,
                os=os,
                login_successful=True
            )
        except Exception as e:
            logger.error(f"Failed to record login history: {e}")


class LogoutView(TemplateView):
    """User logout view"""
    
    def get(self, request, *args, **kwargs):
        logout(request)
        messages.success(request, "You have been logged out successfully.")
        return redirect('home:home')


class RegisterView(CreateView):
    """User registration view"""
    template_name = 'accounts/register.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('accounts:registration_complete')
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('accounts:dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Send verification email if required
        settings_obj = AccountSettings.objects.first()
        if settings_obj and settings_obj.require_email_verification:
            self.send_verification_email(self.object)
            messages.success(self.request, "Registration successful! Please check your email to verify your account.")
        else:
            messages.success(self.request, "Registration successful! You can now log in.")
        
        return response
    
    def send_verification_email(self, user):
        """Send email verification link"""
        try:
            token = user.profile.generate_verification_token()
            verify_url = self.request.build_absolute_uri(
                reverse('accounts:verify_email', args=[token])
            )
            
            subject = 'Verify your email address - MfalmeBits'
            message = f"""
            Hi {user.get_full_name() or user.username},
            
            Thank you for registering with MfalmeBits. Please verify your email address by clicking the link below:
            
            {verify_url}
            
            This link will expire in 24 hours.
            
            If you didn't register for an account, please ignore this email.
            
            Best regards,
            The MfalmeBits Team
            """
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=True,
            )
        except Exception as e:
            logger.error(f"Failed to send verification email: {e}")


class RegistrationCompleteView(TemplateView):
    """Registration complete page"""
    template_name = 'accounts/registration_complete.html'


class VerifyEmailView(TemplateView):
    """Email verification view"""
    template_name = 'accounts/email_verified.html'
    
    def get(self, request, *args, **kwargs):
        token = kwargs.get('token')
        
        try:
            profile = Profile.objects.get(email_verification_token=token)
            
            if not profile.email_verified:
                profile.email_verified = True
                profile.email_verification_token = ''
                profile.save()
                
                messages.success(request, "Your email has been verified successfully!")
            else:
                messages.info(request, "Your email was already verified.")
                
        except Profile.DoesNotExist:
            messages.error(request, "Invalid verification link.")
            return redirect('home:home')
        
        return super().get(request, *args, **kwargs)


class DashboardView(TemplateView):
    """User dashboard"""
    template_name = 'accounts/dashboard.html'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get recent activity
        context['recent_saved'] = SavedItem.objects.filter(user=user)[:5]
        context['recent_downloads'] = DownloadHistory.objects.filter(user=user)[:5]
        context['recent_logins'] = LoginHistory.objects.filter(user=user)[:5]
        
        # Get statistics
        context['stats'] = {
            'saved_items': SavedItem.objects.filter(user=user).count(),
            'downloads': DownloadHistory.objects.filter(user=user).aggregate(
                total=models.Sum('download_count')
            )['total'] or 0,
            'logins': user.profile.login_count,
            'member_since': user.date_joined,
        }
        
        # Get purchases
        from apps.library.models import Purchase
        context['recent_purchases'] = Purchase.objects.filter(user=user)[:5]
        
        return context


class ProfileView(DetailView):
    """User profile view"""
    model = User
    template_name = 'accounts/profile.html'
    context_object_name = 'profile_user'
    slug_field = 'username'
    slug_url_kwarg = 'username'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Check if viewing own profile
        context['is_own_profile'] = self.request.user == self.object
        
        # Get public saved items if allowed
        if self.object.preferences.show_saved_items or self.request.user == self.object:
            context['saved_items'] = SavedItem.objects.filter(user=self.object)[:10]
        
        return context


class ProfileEditView(UpdateView):
    """Edit user profile"""
    model = Profile
    form_class = UserProfileForm
    template_name = 'accounts/profile_edit.html'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_object(self, queryset=None):
        return self.request.user.profile
    
    def get_success_url(self):
        return reverse('accounts:profile', args=[self.request.user.username])
    
    def form_valid(self, form):
        messages.success(self.request, "Profile updated successfully!")
        return super().form_valid(form)


class SettingsView(UpdateView):
    """User preferences/settings"""
    model = UserPreference
    form_class = UserPreferencesForm
    template_name = 'accounts/settings.html'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_object(self, queryset=None):
        return self.request.user.preferences
    
    def get_success_url(self):
        return reverse('accounts:settings')
    
    def form_valid(self, form):
        messages.success(self.request, "Settings updated successfully!")
        return super().form_valid(form)


class ChangePasswordView(FormView):
    """Change password view"""
    template_name = 'accounts/change_password.html'
    form_class = UserChangePasswordForm
    success_url = reverse_lazy('accounts:settings')
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        user = self.request.user
        new_password = form.cleaned_data.get('new_password')
        
        user.set_password(new_password)
        user.save()
        
        # Keep user logged in
        update_session_auth_hash(self.request, user)
        
        messages.success(self.request, "Password changed successfully!")
        return super().form_valid(form)


class PasswordResetRequestView(FormView):
    """Password reset request"""
    template_name = 'accounts/password_reset_request.html'
    form_class = PasswordResetRequestForm
    success_url = reverse_lazy('accounts:password_reset_sent')
    
    def form_valid(self, form):
        email = form.cleaned_data.get('email')
        
        try:
            user = User.objects.get(email=email)
            
            # Generate reset token (in production, use a proper token system)
            import hashlib
            import time
            token = hashlib.sha256(f"{user.email}{time.time()}{user.password}".encode()).hexdigest()
            
            # Store token in session (in production, use database)
            self.request.session['reset_token'] = token
            self.request.session['reset_user_id'] = user.id
            
            # Send reset email
            reset_url = self.request.build_absolute_uri(
                reverse('accounts:password_reset_confirm', args=[token])
            )
            
            subject = 'Password Reset Request - MfalmeBits'
            message = f"""
            Hi {user.get_full_name() or user.username},
            
            You requested to reset your password. Click the link below to set a new password:
            
            {reset_url}
            
            This link will expire in 1 hour.
            
            If you didn't request this, please ignore this email.
            
            Best regards,
            The MfalmeBits Team
            """
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=True,
            )
            
            messages.success(self.request, "Password reset instructions have been sent to your email.")
            
        except User.DoesNotExist:
            # Don't reveal that user doesn't exist for security
            messages.success(self.request, "If an account exists with this email, password reset instructions have been sent.")
        
        return super().form_valid(form)


class PasswordResetConfirmView(FormView):
    """Confirm password reset"""
    template_name = 'accounts/password_reset_confirm.html'
    form_class = PasswordResetConfirmForm
    success_url = reverse_lazy('accounts:login')
    
    def dispatch(self, request, *args, **kwargs):
        token = kwargs.get('token')
        session_token = request.session.get('reset_token')
        
        if not token or token != session_token:
            messages.error(request, "Invalid or expired reset link.")
            return redirect('accounts:password_reset_request')
        
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        user_id = self.request.session.get('reset_user_id')
        
        try:
            user = User.objects.get(id=user_id)
            new_password = form.cleaned_data.get('new_password')
            
            user.set_password(new_password)
            user.save()
            
            # Clear session
            del self.request.session['reset_token']
            del self.request.session['reset_user_id']
            
            messages.success(self.request, "Password reset successfully! You can now log in.")
            
        except User.DoesNotExist:
            messages.error(self.request, "An error occurred. Please try again.")
            return redirect('accounts:password_reset_request')
        
        return super().form_valid(form)


class SavedItemsView(ListView):
    """User's saved items"""
    template_name = 'accounts/saved_items.html'
    context_object_name = 'saved_items'
    paginate_by = 20
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        queryset = SavedItem.objects.filter(user=self.request.user)
        
        # Filter by type
        item_type = self.request.GET.get('type')
        if item_type:
            queryset = queryset.filter(item_type=item_type)
        
        # Search
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(notes__icontains=q) | Q(tags__icontains=q)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get counts by type
        context['counts'] = {
            'archive': SavedItem.objects.filter(
                user=self.request.user, item_type='archive'
            ).count(),
            'product': SavedItem.objects.filter(
                user=self.request.user, item_type='product'
            ).count(),
            'blog': SavedItem.objects.filter(
                user=self.request.user, item_type='blog'
            ).count(),
            'total': SavedItem.objects.filter(user=self.request.user).count(),
        }
        
        context['current_type'] = self.request.GET.get('type', 'all')
        context['search_query'] = self.request.GET.get('q', '')
        
        return context


@login_required
@ajax_required
def toggle_saved_item(request):
    """AJAX view to toggle saved item"""
    if request.method == 'POST':
        item_type = request.POST.get('item_type')
        item_id = request.POST.get('item_id')
        
        if not item_type or not item_id:
            return JsonResponse({'success': False, 'error': 'Missing parameters'})
        
        try:
            saved_item = SavedItem.objects.get(
                user=request.user,
                item_type=item_type,
                item_id=item_id
            )
            saved_item.delete()
            return JsonResponse({'success': True, 'saved': False})
        except SavedItem.DoesNotExist:
            SavedItem.objects.create(
                user=request.user,
                item_type=item_type,
                item_id=item_id
            )
            return JsonResponse({'success': True, 'saved': True})
    
    return JsonResponse({'success': False, 'error': 'Invalid method'})


class DownloadHistoryView(ListView):
    """User's download history"""
    template_name = 'accounts/downloads.html'
    context_object_name = 'downloads'
    paginate_by = 20
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        return DownloadHistory.objects.filter(user=self.request.user)


class LoginHistoryView(ListView):
    """User's login history"""
    template_name = 'accounts/login_history.html'
    context_object_name = 'logins'
    paginate_by = 20
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        return LoginHistory.objects.filter(user=self.request.user)


class DeleteAccountView(TemplateView):
    """Account deletion confirmation"""
    template_name = 'accounts/delete_account.html'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        user = request.user
        
        # Logout user
        logout(request)
        
        # Deactivate user (soft delete)
        user.is_active = False
        user.email = f"deleted_{user.id}_{user.email}"
        user.save()
        
        messages.success(request, "Your account has been deactivated.")
        return redirect('home:home')