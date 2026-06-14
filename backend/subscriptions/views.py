from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from companies.models import CompanyProfile
from subscriptions.constants import Feature
from subscriptions.models import SubscriptionPlan, UsageRecord
from subscriptions.serializers import (
    CheckoutSerializer,
    CompanySubscriptionSerializer,
    EntitlementSerializer,
    SubscriptionPlanSerializer,
    UsageRecordSerializer,
)
from subscriptions.services.billing import get_effective_subscription
from subscriptions.services.entitlements import (
    authorize_feature,
    list_entitlements,
)


def _current_company(user, company_id=None):
    companies = CompanyProfile.objects.filter(user=user)
    if company_id:
        return get_object_or_404(companies, id=company_id)
    return companies.order_by('-created_at').first()


def _profile_required_response():
    return Response(
        {
            'code': 'profile_required',
            'message': 'Avval kompaniya profilini yarating.',
            'details': {},
        },
        status=status.HTTP_400_BAD_REQUEST,
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def plans_view(request):
    plans = SubscriptionPlan.objects.filter(
        is_active=True,
        is_public=True,
    ).order_by('rank', 'code')
    return Response(SubscriptionPlanSerializer(plans, many=True).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_view(request):
    company = _current_company(request.user, request.query_params.get('company_id'))
    if company is None:
        return _profile_required_response()
    effective = get_effective_subscription(company)
    return Response(CompanySubscriptionSerializer(effective.subscription).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def status_view(request):
    company = _current_company(request.user, request.query_params.get('company_id'))
    if company is None:
        return _profile_required_response()
    effective = get_effective_subscription(company)
    data = CompanySubscriptionSerializer(effective.subscription).data
    data.update({
        'current_tariff': effective.plan.code,
        'analysis_per_month': effective.plan.limits.get('ai_analysis_monthly'),
        'tariff_expires_at': (
            None
            if effective.plan.code == 'free'
            else effective.period_end
        ),
    })
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def usage_view(request):
    company = _current_company(request.user, request.query_params.get('company_id'))
    if company is None:
        return _profile_required_response()
    effective = get_effective_subscription(company)
    records = UsageRecord.objects.filter(
        company=company,
        period_start=effective.period_start,
        period_end=effective.period_end,
    ).order_by('metric')
    return Response({
        'company_id': company.id,
        'plan': effective.plan.code,
        'period_start': effective.period_start,
        'period_end': effective.period_end,
        'usage': UsageRecordSerializer(records, many=True).data,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def entitlements_view(request):
    company = _current_company(request.user, request.query_params.get('company_id'))
    if company is None:
        return _profile_required_response()
    effective, entitlements = list_entitlements(request.user, company)
    return Response({
        'company_id': company.id,
        'plan': effective.plan.code,
        'entitlements': EntitlementSerializer(entitlements, many=True).data,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def feature_check_view(request, feature):
    if feature not in Feature.ALL:
        return Response(
            {
                'code': 'unknown_feature',
                'message': "Noma'lum feature key.",
                'details': {'feature': feature},
            },
            status=status.HTTP_404_NOT_FOUND,
        )
    company = _current_company(request.user, request.data.get('company_id'))
    if company is None:
        return _profile_required_response()
    entitlement = authorize_feature(request.user, company, feature)
    return Response(EntitlementSerializer(entitlement).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def checkout_view(request):
    serializer = CheckoutSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    company = _current_company(
        request.user,
        serializer.validated_data.get('company_id'),
    )
    if company is None:
        return _profile_required_response()
    return Response(
        {
            'code': 'payment_not_configured',
            'message': "To'lov provayderi hali production uchun sozlanmagan.",
            'details': {
                'company_id': company.id,
                'plan_code': serializer.validated_data['plan_code'],
            },
        },
        status=status.HTTP_501_NOT_IMPLEMENTED,
    )
