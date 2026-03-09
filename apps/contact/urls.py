from django.urls import path
from . import views

app_name = 'contact'

urlpatterns = [
    path('', views.ContactIndexView.as_view(), name='index'),
    path('submit/', views.ContactSubmitView.as_view(), name='submit'),
    path('faq/', views.FAQView.as_view(), name='faq'),
    path('faq/<int:pk>/', views.FAQDetailView.as_view(), name='faq_detail'),
    path('support/', views.SupportTicketView.as_view(), name='support'),
    path('support/success/', views.SupportSuccessView.as_view(), name='support_success'),
    path('support/<str:ticket_id>/', views.SupportTicketDetailView.as_view(), name='ticket_detail'),
    path('support/<str:ticket_id>/reply/', views.SupportReplyView.as_view(), name='ticket_reply'),
    path('offices/', views.OfficesView.as_view(), name='offices'),
]
