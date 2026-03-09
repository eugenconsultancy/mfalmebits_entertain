from django import forms
from .models import InstitutionalInquiry, LicensingPlan

class InstitutionalInquiryForm(forms.ModelForm):
    """Form for institutional inquiries"""
    
    plan_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'readonly': 'readonly', 'class': 'bg-gray-100'})
    )
    
    class Meta:
        model = InstitutionalInquiry
        fields = [
            'institution_name', 'institution_type', 'website',
            'country', 'city', 'address',
            'contact_person', 'job_title', 'email', 'phone',
            'plan', 'number_of_users', 'content_types', 'message',
            'additional_requirements', 'start_date', 'budget_range',
            'attachment'
        ]
        widgets = {
            'institution_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'placeholder': 'Official institution name'
            }),
            'institution_type': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg'
            }),
            'website': forms.URLInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'placeholder': 'https://'
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
                'rows': 3,
                'placeholder': 'Street address'
            }),
            'contact_person': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'placeholder': 'Full name'
            }),
            'job_title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'placeholder': 'e.g., Library Director'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'placeholder': 'you@institution.edu'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'placeholder': '+1 234 567 8900'
            }),
            'plan': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg'
            }),
            'number_of_users': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'min': 1,
                'value': 1
            }),
            'content_types': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'placeholder': 'e.g., African history, curriculum materials'
            }),
            'message': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'rows': 5,
                'placeholder': 'Tell us about your institution\'s needs...'
            }),
            'additional_requirements': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'rows': 3,
                'placeholder': 'Any specific requirements?'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'type': 'date'
            }),
            'budget_range': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'placeholder': 'e.g., $5,000 - $10,000'
            }),
            'attachment': forms.FileInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'accept': '.pdf,.doc,.docx,.txt'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['plan'].queryset = LicensingPlan.objects.filter(is_active=True)
        self.fields['plan'].required = False
        self.fields['plan'].empty_label = "Select a plan (optional)"
        
        # Make some fields optional
        self.fields['website'].required = False
        self.fields['address'].required = False
        self.fields['job_title'].required = False
        self.fields['phone'].required = False
        self.fields['additional_requirements'].required = False
        self.fields['start_date'].required = False
        self.fields['budget_range'].required = False
        self.fields['attachment'].required = False
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and InstitutionalInquiry.objects.filter(email=email, status='new').exists():
            raise forms.ValidationError("You already have a pending inquiry. We'll contact you soon.")
        return email
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            # Basic phone number validation
            import re
            phone = re.sub(r'[\s\-\(\)]', '', phone)
            if not re.match(r'^\+?[\d]{10,15}$', phone):
                raise forms.ValidationError("Enter a valid phone number with country code")
        return phone


class QuickQuoteForm(forms.Form):
    """Quick quote request form"""
    institution_name = forms.CharField(max_length=200)
    institution_type = forms.ChoiceField(choices=InstitutionalInquiry.INSTITUTION_TYPES)
    email = forms.EmailField()
    number_of_users = forms.IntegerField(min_value=1, initial=1)
    message = forms.CharField(widget=forms.Textarea, required=False)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'w-full px-4 py-2 border rounded-lg'
            })
