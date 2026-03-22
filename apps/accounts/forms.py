from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import Profile, UserPreference, SavedItem
import re

class UserRegistrationForm(forms.ModelForm):
    """User registration form with accessibility improvements"""
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border rounded-lg',
            'placeholder': 'Enter password',
            'autocomplete': 'new-password',
            'aria-label': 'Enter your password'
        })
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border rounded-lg',
            'placeholder': 'Confirm password',
            'autocomplete': 'new-password',
            'aria-label': 'Confirm your password'
        })
    )
    agree_terms = forms.BooleanField(
        required=True,
        label='I agree to the Terms of Service and Privacy Policy',
        widget=forms.CheckboxInput(attrs={
            'class': 'rounded',
            'aria-label': 'Agree to terms and conditions'
        })
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'placeholder': 'Choose a username',
                'autocomplete': 'username',
                'aria-label': 'Username'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'placeholder': 'your.email@example.com',
                'autocomplete': 'email',
                'aria-label': 'Email address'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'placeholder': 'First name',
                'autocomplete': 'given-name',
                'aria-label': 'First name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'placeholder': 'Last name',
                'autocomplete': 'family-name',
                'aria-label': 'Last name'
            }),
        }
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise ValidationError("Username can only contain letters, numbers, and underscores.")
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        if User.objects.filter(email=email).exists():
            raise ValidationError("A user with this email already exists.")
        return email
    
    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        try:
            validate_password(password1)
        except ValidationError as e:
            raise ValidationError(list(e.messages))
        return password1
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords do not match.")
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class UserLoginForm(forms.Form):
    """User login form with accessibility improvements"""
    username = forms.CharField(
        label='Username or Email',
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border rounded-lg',
            'placeholder': 'Username or Email',
            'autocomplete': 'username',
            'aria-label': 'Username or email address'
        })
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border rounded-lg',
            'placeholder': 'Password',
            'autocomplete': 'current-password',
            'aria-label': 'Password'
        })
    )
    remember_me = forms.BooleanField(
        required=False,
        label='Remember me',
        initial=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'rounded',
            'aria-label': 'Remember my login on this device'
        })
    )


class UserProfileForm(forms.ModelForm):
    """User profile edit form"""
    
    class Meta:
        model = Profile
        fields = [
            'bio', 'avatar', 'phone', 'birth_date',
            'country', 'city', 'address',
            'occupation', 'organization', 'website',
            'twitter', 'linkedin', 'facebook', 'instagram'
        ]
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'rows': 4,
                'placeholder': 'Tell us about yourself...',
                'aria-label': 'Biography'
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'aria-label': 'Profile picture'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'placeholder': '+1 234 567 8900',
                'autocomplete': 'tel',
                'aria-label': 'Phone number'
            }),
            'birth_date': forms.DateInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'type': 'date',
                'aria-label': 'Birth date'
            }),
            'country': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'placeholder': 'Country',
                'autocomplete': 'country',
                'aria-label': 'Country'
            }),
            'city': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'placeholder': 'City',
                'autocomplete': 'address-level2',
                'aria-label': 'City'
            }),
            'address': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'rows': 2,
                'placeholder': 'Address',
                'autocomplete': 'street-address',
                'aria-label': 'Address'
            }),
            'occupation': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'placeholder': 'Occupation',
                'autocomplete': 'organization-title',
                'aria-label': 'Occupation'
            }),
            'organization': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'placeholder': 'Organization/Institution',
                'autocomplete': 'organization',
                'aria-label': 'Organization'
            }),
            'website': forms.URLInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'placeholder': 'https://',
                'autocomplete': 'url',
                'aria-label': 'Website'
            }),
            'twitter': forms.URLInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'placeholder': 'https://twitter.com/',
                'autocomplete': 'url',
                'aria-label': 'Twitter profile'
            }),
            'linkedin': forms.URLInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'placeholder': 'https://linkedin.com/in/',
                'autocomplete': 'url',
                'aria-label': 'LinkedIn profile'
            }),
            'facebook': forms.URLInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'placeholder': 'https://facebook.com/',
                'autocomplete': 'url',
                'aria-label': 'Facebook profile'
            }),
            'instagram': forms.URLInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'placeholder': 'https://instagram.com/',
                'autocomplete': 'url',
                'aria-label': 'Instagram profile'
            }),
        }


class UserChangePasswordForm(forms.Form):
    """Change password form"""
    current_password = forms.CharField(
        label='Current Password',
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border rounded-lg',
            'placeholder': 'Current password',
            'autocomplete': 'current-password',
            'aria-label': 'Current password'
        })
    )
    new_password = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border rounded-lg',
            'placeholder': 'New password',
            'autocomplete': 'new-password',
            'aria-label': 'New password'
        })
    )
    confirm_password = forms.CharField(
        label='Confirm New Password',
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border rounded-lg',
            'placeholder': 'Confirm new password',
            'autocomplete': 'new-password',
            'aria-label': 'Confirm new password'
        })
    )
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def clean_current_password(self):
        current = self.cleaned_data.get('current_password')
        if not self.user.check_password(current):
            raise ValidationError("Current password is incorrect.")
        return current
    
    def clean_new_password(self):
        new = self.cleaned_data.get('new_password')
        try:
            validate_password(new, self.user)
        except ValidationError as e:
            raise ValidationError(list(e.messages))
        return new
    
    def clean(self):
        cleaned_data = super().clean()
        new = cleaned_data.get('new_password')
        confirm = cleaned_data.get('confirm_password')
        
        if new and confirm and new != confirm:
            raise ValidationError("New passwords do not match.")
        
        return cleaned_data


class PasswordResetRequestForm(forms.Form):
    """Password reset request form"""
    email = forms.EmailField(
        label='Email Address',
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-2 border rounded-lg',
            'placeholder': 'your.email@example.com',
            'autocomplete': 'email',
            'aria-label': 'Email address'
        })
    )


class PasswordResetConfirmForm(forms.Form):
    """Password reset confirmation form"""
    new_password = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border rounded-lg',
            'placeholder': 'New password',
            'autocomplete': 'new-password',
            'aria-label': 'New password'
        })
    )
    confirm_password = forms.CharField(
        label='Confirm New Password',
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border rounded-lg',
            'placeholder': 'Confirm new password',
            'autocomplete': 'new-password',
            'aria-label': 'Confirm new password'
        })
    )
    
    def clean_new_password(self):
        new = self.cleaned_data.get('new_password')
        try:
            validate_password(new)
        except ValidationError as e:
            raise ValidationError(list(e.messages))
        return new
    
    def clean(self):
        cleaned_data = super().clean()
        new = cleaned_data.get('new_password')
        confirm = cleaned_data.get('confirm_password')
        
        if new and confirm and new != confirm:
            raise ValidationError("Passwords do not match.")
        
        return cleaned_data


class UserPreferencesForm(forms.ModelForm):
    """User preferences form"""
    
    class Meta:
        model = UserPreference
        exclude = ['user']
        widgets = {
            'theme': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'aria-label': 'Theme preference'
            }),
            'items_per_page': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'min': 10,
                'max': 100,
                'aria-label': 'Items per page'
            }),
            'profile_visibility': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'aria-label': 'Profile visibility'
            }),
            'show_email': forms.CheckboxInput(attrs={
                'class': 'rounded',
                'aria-label': 'Show email on profile'
            }),
            'show_saved_items': forms.CheckboxInput(attrs={
                'class': 'rounded',
                'aria-label': 'Show saved items on profile'
            }),
            'email_on_comment': forms.CheckboxInput(attrs={
                'class': 'rounded',
                'aria-label': 'Receive email on comment'
            }),
            'email_on_reply': forms.CheckboxInput(attrs={
                'class': 'rounded',
                'aria-label': 'Receive email on reply'
            }),
            'email_on_purchase': forms.CheckboxInput(attrs={
                'class': 'rounded',
                'aria-label': 'Receive email on purchase'
            }),
            'email_on_newsletter': forms.CheckboxInput(attrs={
                'class': 'rounded',
                'aria-label': 'Receive newsletter'
            }),
        }


class SavedItemForm(forms.ModelForm):
    """Form for updating saved items"""
    
    class Meta:
        model = SavedItem
        fields = ['notes', 'tags']
        widgets = {
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'rows': 3,
                'placeholder': 'Add notes...',
                'aria-label': 'Notes'
            }),
            'tags': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'placeholder': 'Comma-separated tags',
                'aria-label': 'Tags'
            }),
        }