"""
TenderHelper — Tenders URL Configuration
"""

from django.urls import path
from . import views

app_name = 'tenders'

urlpatterns = [
    path('', views.TenderListView.as_view(), name='list'),
    path('manual/', views.manual_tender_view, name='manual'),
    path('<uuid:pk>/', views.TenderDetailView.as_view(), name='detail'),
]
