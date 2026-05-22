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
    # OTP Authentication
    path('send-otp/', views.send_otp_view, name='send-otp'),
    path('verify-otp/', views.verify_otp_view, name='verify-otp'),

    # Google OAuth
    path('google/', views.google_auth_view, name='google-auth'),

    # JWT Refresh
    path('refresh/', TokenRefreshView.as_view(), name='token-refresh'),

    # User Profile
    path('me/', views.user_profile_view, name='user-profile'),
]
