from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('register/complete/', views.RegistrationCompleteView.as_view(), name='registration_complete'),
    path('verify-email/<str:token>/', views.VerifyEmailView.as_view(), name='verify_email'),
    
    # Password Reset
    path('password-reset/', views.PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset/sent/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html'
    ), name='password_reset_sent'),
    path('password-reset/<str:token>/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html'
    ), name='password_reset_complete'),
    
    # Dashboard & Profile
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('profile/<str:username>/', views.ProfileView.as_view(), name='profile'),
    path('profile/edit/', views.ProfileEditView.as_view(), name='profile_edit'),
    
    # Settings
    path('settings/', views.SettingsView.as_view(), name='settings'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change_password'),
    
    # Saved Items
    path('saved/', views.SavedItemsView.as_view(), name='saved_items'),
    path('saved/toggle/', views.toggle_saved_item, name='toggle_saved'),
    
    # History
    path('downloads/', views.DownloadHistoryView.as_view(), name='downloads'),
    path('login-history/', views.LoginHistoryView.as_view(), name='login_history'),
    
    # Account Management
    path('delete/', views.DeleteAccountView.as_view(), name='delete_account'),
]
