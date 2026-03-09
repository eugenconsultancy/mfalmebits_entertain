from django import forms
from .models import Subscriber, NewsletterArticle
import re

class NewsletterSubscribeForm(forms.Form):
    """Newsletter subscription form"""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-2 border rounded-lg',
            'placeholder': 'your.email@example.com'
        })
    )
    first_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border rounded-lg',
            'placeholder': 'First name'
        })
    )
    last_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border rounded-lg',
            'placeholder': 'Last name'
        })
    )
    frequency = forms.ChoiceField(
        choices=Subscriber._meta.get_field('frequency').choices,
        initial='weekly',
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border rounded-lg'
        })
    )
    interests = forms.MultipleChoiceField(
        choices=[
            ('history', 'African History'),
            ('culture', 'Culture & Traditions'),
            ('arts', 'Arts & Literature'),
            ('philosophy', 'Philosophy & Ideas'),
            ('science', 'Science & Innovation'),
            ('contemporary', 'Contemporary Africa'),
        ],
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'space-y-2'
        })
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise forms.ValidationError("Please enter a valid email address.")
        return email


class NewsletterUnsubscribeForm(forms.Form):
    """Unsubscribe form"""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-2 border rounded-lg',
            'placeholder': 'your.email@example.com',
            'readonly': True
        })
    )
    token = forms.CharField(widget=forms.HiddenInput(), required=False)
    reason = forms.ChoiceField(
        choices=[
            ('', 'Select a reason (optional)'),
            ('too_many', 'Too many emails'),
            ('not_relevant', 'Content not relevant'),
            ('spam', 'Looks like spam'),
            ('personal', 'Personal reasons'),
            ('other', 'Other'),
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border rounded-lg'
        })
    )
    other_reason = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-2 border rounded-lg',
            'rows': 3,
            'placeholder': 'Please specify...'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        reason = cleaned_data.get('reason')
        other = cleaned_data.get('other_reason')
        
        if reason == 'other' and not other:
            raise forms.ValidationError("Please specify your reason.")
        
        return cleaned_data


class NewsletterPreferencesForm(forms.Form):
    """Update subscription preferences"""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-2 border rounded-lg',
            'readonly': True
        })
    )
    token = forms.CharField(widget=forms.HiddenInput(), required=False)
    first_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border rounded-lg',
            'placeholder': 'First name'
        })
    )
    last_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border rounded-lg',
            'placeholder': 'Last name'
        })
    )
    frequency = forms.ChoiceField(
        choices=Subscriber._meta.get_field('frequency').choices,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border rounded-lg'
        })
    )
    interests = forms.MultipleChoiceField(
        choices=[
            ('history', 'African History'),
            ('culture', 'Culture & Traditions'),
            ('arts', 'Arts & Literature'),
            ('philosophy', 'Philosophy & Ideas'),
            ('science', 'Science & Innovation'),
            ('contemporary', 'Contemporary Africa'),
        ],
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'space-y-2'
        })
    )
    
    def clean_interests(self):
        interests = self.cleaned_data.get('interests', [])
        return interests


class NewsletterContactForm(forms.Form):
    """Contact newsletter team"""
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border rounded-lg',
            'placeholder': 'Your name'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-2 border rounded-lg',
            'placeholder': 'your.email@example.com'
        })
    )
    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border rounded-lg',
            'placeholder': 'Subject'
        })
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-2 border rounded-lg',
            'rows': 6,
            'placeholder': 'Your message...'
        })
    )
    
    def clean_message(self):
        message = self.cleaned_data.get('message')
        if len(message) < 10:
            raise forms.ValidationError("Message must be at least 10 characters long.")
        return message


class NewsletterSearchForm(forms.Form):
    """Search newsletter archive"""
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border rounded-lg',
            'placeholder': 'Search newsletters...'
        })
    )
    
    def clean_q(self):
        q = self.cleaned_data.get('q', '').strip()
        if q and len(q) < 3:
            raise forms.ValidationError("Search term must be at least 3 characters long.")
        return q
