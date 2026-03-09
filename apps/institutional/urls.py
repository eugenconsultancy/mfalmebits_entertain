from django.urls import path
from . import views

app_name = 'institutional'

urlpatterns = [
    path('', views.InstitutionalIndexView.as_view(), name='index'),
    path('plan/<slug:slug>/', views.PlanDetailView.as_view(), name='plan_detail'),
    path('inquiry/', views.InstitutionalInquiryView.as_view(), name='inquiry'),
    path('inquiry/success/', views.InquirySuccessView.as_view(), name='inquiry_success'),
    path('calculator/', views.PricingCalculatorView.as_view(), name='calculator'),
    path('faq/', views.FAQView.as_view(), name='faq'),
    path('case-studies/', views.CaseStudiesView.as_view(), name='case_studies'),
    path('brochure/<int:pk>/', views.BrochureDownloadView.as_view(), name='brochure_download'),
]
