# apps/newsletter/urls.py
from django.urls import path
from . import views

app_name = 'newsletter'

urlpatterns = [
    # Subscription
    path('subscribe/', views.NewsletterSubscribeView.as_view(), name='subscribe'),
    
    # Updated Confirmation: Both paths now point to the same view
    path('confirm/', views.NewsletterConfirmView.as_view(), name='confirm_no_token'),
    path('confirm/<str:token>/', views.NewsletterConfirmView.as_view(), name='confirm'),
    
    path('unsubscribe/', views.NewsletterUnsubscribeView.as_view(), name='unsubscribe'),
    path('unsubscribe/<str:token>/', views.NewsletterUnsubscribeView.as_view(), name='unsubscribe_with_token'),
    path('unsubscribed/', views.NewsletterUnsubscribedView.as_view(), name='unsubscribed'),
    
    # Preferences
    path('preferences/', views.NewsletterPreferencesView.as_view(), name='preferences'),
    path('preferences/<str:token>/', views.NewsletterPreferencesView.as_view(), name='preferences_with_token'),
    path('preferences/updated/', views.NewsletterPreferencesUpdatedView.as_view(), name='preferences_updated'),
    
    # Archive & Articles
    path('archive/', views.NewsletterArchiveView.as_view(), name='archive'),
    path('archive/<slug:campaign_slug>/<int:issue_number>/', views.NewsletterIssueView.as_view(), name='issue'),
    path('articles/', views.NewsletterArchiveView.as_view(), name='articles'), 
    path('articles/<slug:slug>/', views.NewsletterArticleView.as_view(), name='article_detail'),
    path('category/<slug:slug>/', views.NewsletterCategoryView.as_view(), name='category'),
    
    # Contact & Tracking
    path('contact/', views.NewsletterContactView.as_view(), name='contact'),
    path('contact/success/', views.NewsletterPreferencesUpdatedView.as_view(), name='contact_success'),
    path('track/', views.NewsletterTrackView.as_view(), name='track'),
]