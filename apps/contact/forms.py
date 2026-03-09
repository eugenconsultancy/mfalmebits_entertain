from django import forms
from .models import ContactMessage, SupportTicket, SupportReply
import os

class ContactForm(forms.ModelForm):
    """Contact form"""
    subscribe_newsletter = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'rounded'
        })
    )
    
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'subject_type', 'subject', 'message', 'attachment']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'placeholder': 'Your full name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'placeholder': 'your.email@example.com'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'placeholder': '+1 234 567 8900 (optional)'
            }),
            'subject_type': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'placeholder': 'What is this regarding?'
            }),
            'message': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'rows': 6,
                'placeholder': 'Your message...'
            }),
            'attachment': forms.FileInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'accept': '.pdf,.doc,.docx,.jpg,.png'
            }),
        }
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if len(name) < 2:
            raise forms.ValidationError("Name must be at least 2 characters long.")
        return name
    
    def clean_message(self):
        message = self.cleaned_data.get('message')
        if len(message) < 10:
            raise forms.ValidationError("Message must be at least 10 characters long.")
        if len(message) > 5000:
            raise forms.ValidationError("Message must not exceed 5000 characters.")
        return message
    
    def clean_attachment(self):
        attachment = self.cleaned_data.get('attachment')
        if attachment:
            # Check file size (10MB limit)
            if attachment.size > 10 * 1024 * 1024:
                raise forms.ValidationError("File size must be under 10MB")
            
            # Check file extension
            ext = os.path.splitext(attachment.name)[1].lower()
            valid_extensions = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png']
            if ext not in valid_extensions:
                raise forms.ValidationError(f"Unsupported file extension. Please use: {', '.join(valid_extensions)}")
        
        return attachment


class SupportTicketForm(forms.ModelForm):
    """Support ticket form"""
    
    class Meta:
        model = SupportTicket
        fields = ['name', 'email', 'category', 'priority', 'subject', 'description', 'attachment']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'placeholder': 'Your full name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'placeholder': 'your.email@example.com'
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg'
            }),
            'priority': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'placeholder': 'Brief summary of the issue'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'rows': 8,
                'placeholder': 'Please describe your issue in detail...'
            }),
            'attachment': forms.FileInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'accept': '.pdf,.doc,.docx,.jpg,.png,.zip'
            }),
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        # You could add additional validation here
        return email.lower()
    
    def clean_attachment(self):
        attachment = self.cleaned_data.get('attachment')
        if attachment:
            if attachment.size > 20 * 1024 * 1024:  # 20MB limit for support
                raise forms.ValidationError("File size must be under 20MB")
        return attachment


class SupportReplyForm(forms.ModelForm):
    """Support ticket reply form"""
    
    class Meta:
        model = SupportReply
        fields = ['message', 'attachment', 'is_internal']
        widgets = {
            'message': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'rows': 4,
                'placeholder': 'Type your reply...'
            }),
            'attachment': forms.FileInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'accept': '.pdf,.doc,.docx,.jpg,.png,.zip'
            }),
            'is_internal': forms.CheckboxInput(attrs={
                'class': 'rounded'
            }),
        }
    
    def clean_message(self):
        message = self.cleaned_data.get('message')
        if not message and not self.cleaned_data.get('attachment'):
            raise forms.ValidationError("Please provide either a message or an attachment.")
        return message


class FAQSearchForm(forms.Form):
    """FAQ search form"""
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border rounded-lg',
            'placeholder': 'Search FAQs...'
        })
    )
    
    def clean_q(self):
        q = self.cleaned_data.get('q', '').strip()
        if q and len(q) < 3:
            raise forms.ValidationError("Search term must be at least 3 characters long.")
        return q
