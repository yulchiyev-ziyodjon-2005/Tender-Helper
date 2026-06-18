"""
TenderHelper — Analysis URL Configuration
"""

from django.urls import path
from . import views

app_name = 'analysis'

urlpatterns = [
    path('start/', views.start_analysis_view, name='start'),
    path('history/', views.analysis_history_view, name='history'),
    path('legal-sources/', views.legal_sources_view, name='legal-sources'),
    path('<uuid:pk>/status/', views.analysis_status_view, name='status'),
    path('<uuid:pk>/result/', views.analysis_result_view, name='result'),
    path('<uuid:pk>/calculate/', views.calculate_view, name='calculate'),
]
