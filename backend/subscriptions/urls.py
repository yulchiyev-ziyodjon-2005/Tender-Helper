from django.urls import path

from . import views

app_name = 'subscriptions'

urlpatterns = [
    path('plans/', views.plans_view, name='plans'),
    path('current/', views.current_view, name='current'),
    path('status/', views.status_view, name='status'),
    path('usage/', views.usage_view, name='usage'),
    path('entitlements/', views.entitlements_view, name='entitlements'),
    path(
        'features/<str:feature>/check/',
        views.feature_check_view,
        name='feature-check',
    ),
    path('checkout/', views.checkout_view, name='checkout'),
]
