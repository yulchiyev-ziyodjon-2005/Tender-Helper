from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from companies.models import CompanyProfile


PLANS = [
    {
        'code': 'free',
        'name': 'Free',
        'price_usd': 0,
        'price_uzs': 0,
        'analysis_limit': 4,
        'features': ['AI tahlil: 4 ta/oy', 'Smart kalkulyator', 'Red flags', 'Hujjatlar checklist'],
    },
    {
        'code': 'pro',
        'name': 'Pro',
        'price_usd': 15,
        'price_uzs': 195000,
        'analysis_limit': None,
        'features': ['Cheksiz AI tahlil', '25+ filtr', 'Smart kalkulyator', 'Push notifications'],
    },
    {
        'code': 'enterprise',
        'name': 'Enterprise',
        'price_usd': 50,
        'price_uzs': 650000,
        'analysis_limit': None,
        'features': ['Cheksiz AI tahlil', 'Jamoaviy xona', 'Raqobatchi razvedkasi', 'Priority support'],
    },
]


@api_view(['GET'])
@permission_classes([AllowAny])
def plans_view(request):
    return Response(PLANS)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def status_view(request):
    profile = CompanyProfile.objects.filter(user=request.user).order_by('-created_at').first()
    tariff = profile.current_tariff if profile else 'free'
    limits = settings.SUBSCRIPTION_LIMITS.get(tariff, settings.SUBSCRIPTION_LIMITS['free'])
    return Response({
        'current_tariff': tariff,
        'analysis_per_month': limits['analysis_per_month'],
        'tariff_expires_at': profile.tariff_expires_at if profile else None,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def checkout_view(request):
    return Response({
        'status': 'test_mode',
        'message': "MVP test rejimi: real to'lov merchantlari keyinroq ulanadi",
    })
