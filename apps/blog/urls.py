from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    # Main blog pages
    path('', views.BlogIndexView.as_view(), name='index'),
    path('category/<slug:slug>/', views.CategoryView.as_view(), name='category'),
    path('tag/<slug:slug>/', views.TagView.as_view(), name='tag'),
    path('author/<str:username>/', views.AuthorView.as_view(), name='author'),
    path('series/<slug:slug>/', views.SeriesView.as_view(), name='series'),
    
    # Archive
    path('archive/<int:year>/', views.ArchiveView.as_view(), name='archive_year'),
    path('archive/<int:year>/<int:month>/', views.ArchiveView.as_view(), name='archive_month'),
    
    # Post detail
    path('<int:year>/<str:month>/<slug:slug>/', views.PostDetailView.as_view(), name='detail'),
    
    # Comments
    path('<slug:slug>/comment/', views.CommentCreateView.as_view(), name='add_comment'),
    
    # Newsletter
    path('newsletter/subscribe/', views.NewsletterSubscribeView.as_view(), name='newsletter_subscribe'),
    path('newsletter/unsubscribe/', views.NewsletterUnsubscribeView.as_view(), name='newsletter_unsubscribe'),
]
