"""
TenderHelper — Companies URL Configuration
"""

from django.urls import path
from . import views

app_name = 'companies'

urlpatterns = [
    path('onboarding/', views.onboarding_view, name='onboarding'),
    path('profile/', views.profile_view, name='profile'),
]
