from django.urls import path
from . import views

app_name = 'library'

urlpatterns = [
    path('', views.LibraryIndexView.as_view(), name='index'),
    path('category/<slug:slug>/', views.CategoryView.as_view(), name='category'),
    path('<slug:category>/<slug:product_slug>/', views.ProductDetailView.as_view(), name='detail'),
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('success/', views.PaymentSuccessView.as_view(), name='success'),
    path('download/<int:pk>/', views.DownloadView.as_view(), name='download'),
    path('review/<slug:product_slug>/', views.AddReviewView.as_view(), name='add_review'),
]
