from django.urls import path
from . import views

app_name = 'archive'

urlpatterns = [
    path('', views.ArchiveIndexView.as_view(), name='index'),
    path('theme/<slug:theme>/', views.ThemeView.as_view(), name='by_theme'),
    path('tag/<slug:tag>/', views.TagView.as_view(), name='by_tag'),
    path('<slug:theme>/<slug:entry_slug>/', views.ArchiveDetailView.as_view(), name='detail'),
]
