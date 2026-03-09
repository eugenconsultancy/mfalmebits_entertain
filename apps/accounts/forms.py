from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import Profile, UserPreference, SavedItem
import re

class UserRegistrationForm(forms.ModelForm):
    """User registration form"""
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border rounded-lg',
            'placeholder': 'Enter password'
        })
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border rounded-lg',
            'placeholder': 'Confirm password'
        })
    )
    agree_terms = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'rounded'
        })
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'placeholder': 'Choose a username'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'placeholder': 'your.email@example.com'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'placeholder': 'First name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'placeholder': 'Last name'
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
    """User login form"""
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border rounded-lg',
            'placeholder': 'Username or Email'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border rounded-lg',
            'placeholder': 'Password'
        })
    )
    remember_me = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'rounded'
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
                'placeholder': 'Tell us about yourself...'
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'placeholder': '+1 234 567 8900'
            }),
            'birth_date': forms.DateInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'type': 'date'
            }),
            'country': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'placeholder': 'Country'
            }),
            'city': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'placeholder': 'City'
            }),
            'address': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'rows': 2,
                'placeholder': 'Address'
            }),
            'occupation': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'placeholder': 'Occupation'
            }),
            'organization': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'placeholder': 'Organization/Institution'
            }),
            'website': forms.URLInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'placeholder': 'https://'
            }),
            'twitter': forms.URLInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'placeholder': 'https://twitter.com/'
            }),
            'linkedin': forms.URLInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'placeholder': 'https://linkedin.com/in/'
            }),
            'facebook': forms.URLInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'placeholder': 'https://facebook.com/'
            }),
            'instagram': forms.URLInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'placeholder': 'https://instagram.com/'
            }),
        }


class UserChangePasswordForm(forms.Form):
    """Change password form"""
    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border rounded-lg',
            'placeholder': 'Current password'
        })
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border rounded-lg',
            'placeholder': 'New password'
        })
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border rounded-lg',
            'placeholder': 'Confirm new password'
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
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-2 border rounded-lg',
            'placeholder': 'your.email@example.com'
        })
    )


class PasswordResetConfirmForm(forms.Form):
    """Password reset confirmation form"""
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border rounded-lg',
            'placeholder': 'New password'
        })
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border rounded-lg',
            'placeholder': 'Confirm new password'
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
                'class': 'w-full px-4 py-2 border rounded-lg'
            }),
            'items_per_page': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'min': 10,
                'max': 100
            }),
            'profile_visibility': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg'
            }),
            'show_email': forms.CheckboxInput(attrs={
                'class': 'rounded'
            }),
            'show_saved_items': forms.CheckboxInput(attrs={
                'class': 'rounded'
            }),
            'email_on_comment': forms.CheckboxInput(attrs={
                'class': 'rounded'
            }),
            'email_on_reply': forms.CheckboxInput(attrs={
                'class': 'rounded'
            }),
            'email_on_purchase': forms.CheckboxInput(attrs={
                'class': 'rounded'
            }),
            'email_on_newsletter': forms.CheckboxInput(attrs={
                'class': 'rounded'
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
                'placeholder': 'Add notes...'
            }),
            'tags': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'placeholder': 'Comma-separated tags'
            }),
        }
