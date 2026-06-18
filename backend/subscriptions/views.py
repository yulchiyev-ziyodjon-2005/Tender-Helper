from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from subscriptions.constants import Feature
from subscriptions.models import SubscriptionPlan, UsageRecord
from subscriptions.serializers import (
    CheckoutSerializer,
    CompanySubscriptionSerializer,
    EntitlementSerializer,
    PaymentTransactionSerializer,
    SubscriptionPlanSerializer,
    UsageRecordSerializer,
)
from subscriptions.services.billing import get_effective_subscription
from subscriptions.services.entitlements import (
    authorize_feature,
    list_entitlements,
)
from subscriptions.services.membership import accessible_companies
from subscriptions.services.payments import create_checkout_transaction
from subscriptions.services.payments import process_click_callback


def _current_company(user, company_id=None):
    companies = accessible_companies(user)
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


def _click_ip_allowed(request):
    allowed_ips = getattr(settings, 'CLICK_ALLOWED_IPS', [])
    if not allowed_ips:
        return True
    forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR', '')
    client_ip = (
        forwarded_for.split(',')[0].strip()
        if forwarded_for
        else request.META.get('REMOTE_ADDR', '')
    )
    return client_ip in allowed_ips


def _click_forbidden_response():
    return Response(
        {
            'code': 'click_ip_not_allowed',
            'message': 'CLICK webhook source IP is not allowed.',
            'details': {},
        },
        status=status.HTTP_403_FORBIDDEN,
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
        'limits': {
            **effective.plan.limits,
            'sms_allowed_monthly': effective.subscription.sms_allowed_monthly,
            'sms_sent_this_month': effective.subscription.sms_sent_this_month,
            'daily_sms_cap': effective.subscription.daily_sms_cap,
        },
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
    try:
        checkout = create_checkout_transaction(
            company,
            serializer.validated_data['plan_code'],
            provider=serializer.validated_data['provider'],
        )
    except NotImplementedError:
        return Response(
            {
                'code': 'payment_provider_not_supported',
                'message': "Tanlangan to'lov provayderi hali ulanmagan.",
                'details': {
                    'provider': serializer.validated_data['provider'],
                },
            },
            status=status.HTTP_501_NOT_IMPLEMENTED,
        )
    except RuntimeError:
        return Response(
            {
                'code': 'payment_not_configured',
                'message': "To'lov provayderi hali production uchun sozlanmagan.",
                'details': {
                    'company_id': company.id,
                    'plan_code': serializer.validated_data['plan_code'],
                    'provider': serializer.validated_data['provider'],
                },
            },
            status=status.HTTP_501_NOT_IMPLEMENTED,
        )
    except ValueError as exc:
        return Response(
            {
                'code': 'checkout_not_available',
                'message': str(exc),
                'details': {},
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    return Response(
        {
            'transaction': PaymentTransactionSerializer(
                checkout.transaction,
            ).data,
            'payment': checkout.payment,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def click_prepare_view(request):
    if not _click_ip_allowed(request):
        return _click_forbidden_response()
    payload = request.data.copy()
    payload['action'] = '0'
    return Response(process_click_callback(payload))


@api_view(['POST'])
@permission_classes([AllowAny])
def click_complete_view(request):
    if not _click_ip_allowed(request):
        return _click_forbidden_response()
    payload = request.data.copy()
    payload['action'] = '1'
    return Response(process_click_callback(payload))
