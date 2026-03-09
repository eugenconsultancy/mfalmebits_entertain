from django import forms
from .models import CollaborationSubmission, CollaborationProject
import os

class CollaborationSubmissionForm(forms.ModelForm):
    """Form for quick collaboration submissions"""
    
    class Meta:
        model = CollaborationSubmission
        fields = [
            'first_name', 'last_name', 'email', 'creator_type',
            'portfolio_link', 'project_idea', 'samples', 'terms_accepted'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'placeholder': 'First name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'placeholder': 'Last name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'placeholder': 'you@example.com'
            }),
            'creator_type': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg'
            }),
            'portfolio_link': forms.URLInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'placeholder': 'https://'
            }),
            'project_idea': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'rows': 5,
                'placeholder': 'Tell us about your collaboration idea...'
            }),
            'samples': forms.FileInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'accept': '.pdf,.doc,.docx,.jpg,.png,.zip'
            }),
            'terms_accepted': forms.CheckboxInput(attrs={
                'class': 'rounded'
            }),
        }
    
    def clean_samples(self):
        samples = self.cleaned_data.get('samples')
        if samples:
            # Check file size (10MB limit)
            if samples.size > 10 * 1024 * 1024:
                raise forms.ValidationError("File size must be under 10MB")
            
            # Check file extension
            ext = os.path.splitext(samples.name)[1].lower()
            valid_extensions = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png', '.zip']
            if ext not in valid_extensions:
                raise forms.ValidationError(f"Unsupported file extension. Please use: {', '.join(valid_extensions)}")
        
        return samples
    
    def clean_terms_accepted(self):
        terms = self.cleaned_data.get('terms_accepted')
        if not terms:
            raise forms.ValidationError("You must accept the terms to submit")
        return terms


class CollaborationProjectForm(forms.ModelForm):
    """Detailed project proposal form"""
    
    class Meta:
        model = CollaborationProject
        fields = [
            'title', 'category', 'collaboration_category',
            'creator_name', 'creator_bio', 'creator_email', 'creator_phone',
            'creator_website', 'creator_location',
            'description', 'short_description', 'goals', 'inspiration',
            'proposed_duration', 'proposed_start_date',
            'has_budget', 'budget_details', 'funding_request',
            'portfolio_url', 'proposal_document', 'featured_image',
            'terms_accepted'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'placeholder': 'Project title'
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg'
            }),
            'collaboration_category': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg'
            }),
            'creator_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'placeholder': 'Your full name'
            }),
            'creator_bio': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'rows': 4,
                'placeholder': 'Tell us about yourself...'
            }),
            'creator_email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'placeholder': 'you@example.com'
            }),
            'creator_phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'placeholder': '+1 234 567 8900'
            }),
            'creator_website': forms.URLInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'placeholder': 'https://'
            }),
            'creator_location': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'placeholder': 'City, Country'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'rows': 8,
                'placeholder': 'Detailed description of your project...'
            }),
            'short_description': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'placeholder': 'Brief summary (max 300 characters)'
            }),
            'goals': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'rows': 4,
                'placeholder': 'What do you hope to achieve?'
            }),
            'inspiration': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'rows': 4,
                'placeholder': 'What inspired this project?'
            }),
            'proposed_duration': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'placeholder': 'e.g., 3 months'
            }),
            'proposed_start_date': forms.DateInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'type': 'date'
            }),
            'has_budget': forms.CheckboxInput(attrs={
                'class': 'rounded'
            }),
            'budget_details': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'rows': 3,
                'placeholder': 'Provide budget details if applicable'
            }),
            'funding_request': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'step': '0.01',
                'placeholder': 'Amount requested (if any)'
            }),
            'portfolio_url': forms.URLInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'placeholder': 'Link to your portfolio'
            }),
            'proposal_document': forms.FileInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'accept': '.pdf,.doc,.docx'
            }),
            'featured_image': forms.FileInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'accept': 'image/*'
            }),
            'terms_accepted': forms.CheckboxInput(attrs={
                'class': 'rounded'
            }),
        }
    
    def clean_short_description(self):
        description = self.cleaned_data.get('short_description')
        if description and len(description) > 300:
            raise forms.ValidationError("Short description must be under 300 characters")
        return description
    
    def clean_funding_request(self):
        has_budget = self.cleaned_data.get('has_budget')
        funding = self.cleaned_data.get('funding_request')
        
        if has_budget and not funding:
            raise forms.ValidationError("Please provide funding request amount")
        return funding
    
    def clean_terms_accepted(self):
        terms = self.cleaned_data.get('terms_accepted')
        if not terms:
            raise forms.ValidationError("You must accept the terms to submit")
        return terms
