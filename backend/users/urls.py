"""
TenderHelper — Users URL Configuration
=========================================
Auth API endpoints: OTP, Google OAuth, JWT refresh, profil.
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

app_name = 'users'

urlpatterns = [
    # Email Authentication
    path('register/', views.email_register_view, name='email-register'),
    path('login/', views.email_login_view, name='email-login'),

    # OTP Authentication
    path('send-otp/', views.send_otp_view, name='send-otp'),
    path('verify-otp/', views.verify_otp_view, name='verify-otp'),

    # Google OAuth
    path('google/', views.google_auth_view, name='google-auth'),
    path('google/config/', views.google_oauth_config_view, name='google-config'),
    path('google/start/', views.google_oauth_start_view, name='google-start'),
    path('google/callback/', views.google_oauth_callback_view, name='google-callback'),

    # JWT Refresh
    path('refresh/', TokenRefreshView.as_view(), name='token-refresh'),

    # User Profile
    path('me/', views.user_profile_view, name='user-profile'),
]
