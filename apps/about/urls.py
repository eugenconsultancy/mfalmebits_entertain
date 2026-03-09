from django.urls import path
from . import views

app_name = 'about'

urlpatterns = [
    path('', views.AboutIndexView.as_view(), name='index'),
    path('team/', views.TeamListView.as_view(), name='team'),
    path('team/<slug:slug>/', views.TeamDetailView.as_view(), name='team_detail'),
    path('history/', views.TimelineView.as_view(), name='timeline'),
    path('values/', views.ValuesView.as_view(), name='values'),
    path('partners/', views.PartnersView.as_view(), name='partners'),
]
