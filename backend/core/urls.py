"""
TenderHelper AI — URL Configuration
=====================================
Barcha app URL'lari /api/v1/ prefiksi ostida markazlashtirilgan.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


# ──────────────── Health Check Endpoint ────────────────
@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """API sog'liq tekshiruvi — monitoring va deploy uchun."""
    return Response({
        'status': 'ok',
        'service': 'TenderHelper AI',
        'version': '1.0.0-mvp',
    })


# ──────────────── API v1 URL Patterns ────────────────
api_v1_patterns = [
    path('auth/', include('users.urls')),
    path('company/', include('companies.urls')),
    path('tenders/', include('tenders.urls')),
    path('analysis/', include('analysis.urls')),
    path('subscription/', include('subscriptions.urls')),
    path('team/', include('teams.urls')),
    path('competitors/', include('competitors.urls')),
]

# ──────────────── Root URL Patterns ────────────────
urlpatterns = [
    # Admin panel
    path('admin/', admin.site.urls),

    # Health check
    path('api/health/', health_check, name='health-check'),

    # API v1
    path('api/v1/', include((api_v1_patterns, 'api-v1'))),
]

# Development: serve media files
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
