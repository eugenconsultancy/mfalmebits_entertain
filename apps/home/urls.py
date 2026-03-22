from django.urls import path
from . import views

app_name = 'home'

urlpatterns = [
    # Home page
    path('', views.HomeView.as_view(), name='home'),
    
    # Static pages
    path('about/', views.AboutView.as_view(), name='about'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('faq/', views.FAQView.as_view(), name='faq'),
    path('privacy-policy/', views.PrivacyPolicyView.as_view(), name='privacy_policy'),
    path('health/', views.health_check, name='health_check'),
    path('terms-of-service/', views.TermsOfServiceView.as_view(), name='terms_of_service'),
]