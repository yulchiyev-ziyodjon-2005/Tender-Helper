"""
TenderHelper — Companies URL Configuration
"""

from django.urls import path
from . import views

app_name = 'companies'

urlpatterns = [
    path('onboarding/', views.onboarding_view, name='onboarding'),
    path('profile/', views.profile_view, name='profile'),
    path('registry/lookup/', views.registry_lookup_view, name='registry-lookup'),
    path(
        'registry/drafts/<uuid:pk>/',
        views.registry_draft_view,
        name='registry-draft',
    ),
    path(
        'registry/drafts/<uuid:pk>/confirm/',
        views.registry_draft_confirm_view,
        name='registry-draft-confirm',
    ),
    path('onboarding/skip-stir/', views.skip_stir_view, name='skip-stir'),
    path(
        'profile/registry-refresh/',
        views.registry_refresh_view,
        name='registry-refresh',
    ),
]
