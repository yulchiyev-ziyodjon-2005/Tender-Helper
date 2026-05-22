"""
TenderHelper — Subscriptions URL Configuration
"""

from django.urls import path
from . import views

app_name = 'subscriptions'

urlpatterns = [
    path('plans/', views.plans_view, name='plans'),
    path('status/', views.status_view, name='status'),
    path('checkout/', views.checkout_view, name='checkout'),
]
