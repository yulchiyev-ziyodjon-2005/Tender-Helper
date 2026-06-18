from datetime import timedelta

from django.conf import settings
from django.db.models import Max
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from competitors.models import (
    CompetitorAnalytics,
    CompetitorDataQualityIssue,
)
from competitors.serializers import (
    CompanyScopeQuerySerializer,
    CompetitorAnalyticsSerializer,
    CompetitorHistoryQuerySerializer,
    CompetitorQuerySerializer,
)
from subscriptions.constants import Feature
from subscriptions.models import UsageRecord
from subscriptions.services.entitlements import authorize_feature
from subscriptions.services.membership import accessible_companies
from subscriptions.services.membership import require_company_permission
from subscriptions.services.usage import consume_usage
from teams.models import TeamPermission
from tenders.models import TenderLot


def _current_company(user, company_id=None):
    companies = accessible_companies(user)
    if company_id:
        return get_object_or_404(companies, pk=company_id)
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


def _authorize(request, company_id=None):
    company = _current_company(request.user, company_id)
    if company is None:
        return None
    authorize_feature(request.user, company, Feature.COMPETITOR_INTELLIGENCE)
    require_company_permission(
        request.user,
        company,
        TeamPermission.VIEW_COMPETITORS,
    )
    return company


def _period(validated_data):
    if validated_data.get('period_start'):
        return validated_data['period_start'], validated_data['period_end']
    days = int(validated_data['period'][:-1])
    end = timezone.localdate()
    return end - timedelta(days=days - 1), end


def _insufficient_response(*, scope, period_start, period_end, available):
    return Response({
        'status': 'insufficient_data',
        'scope': scope,
        'period_start': period_start,
        'period_end': period_end,
        'minimum_source_count': settings.COMPETITOR_MIN_SAMPLE_SIZE,
        'available_competitors': available,
        'results': [],
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def top_competitors_view(request):
    serializer = CompetitorQuerySerializer(data=request.query_params)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data
    company = _authorize(request, data.get('company_id'))
    if company is None:
        return _profile_required_response()
    period_start, period_end = _period(data)

    if data.get('lot_id'):
        lot = get_object_or_404(TenderLot, pk=data['lot_id'])
        scope = {'type': 'lot', 'lot_id': lot.id, 'category': lot.category}
        snapshots = CompetitorAnalytics.objects.filter(
            scope_type=CompetitorAnalytics.Scope.LOT,
            tender_lot=lot,
            period_start=period_start,
            period_end=period_end,
        )
    else:
        category = data['category']
        scope = {'type': 'category', 'category': category}
        snapshots = CompetitorAnalytics.objects.filter(
            scope_type=CompetitorAnalytics.Scope.CATEGORY,
            category=category,
            period_start=period_start,
            period_end=period_end,
        )

    consume_usage(company, UsageRecord.Metric.COMPETITOR_QUERY)
    snapshots = snapshots.prefetch_related('sources__award').order_by(
        'rank',
        'identity_key',
    )
    available = snapshots.count()
    snapshots = snapshots.filter(
        source_count__gte=settings.COMPETITOR_MIN_SAMPLE_SIZE,
    )
    if not snapshots.exists():
        return _insufficient_response(
            scope=scope,
            period_start=period_start,
            period_end=period_end,
            available=available,
        )

    results = list(snapshots)
    calculated_at = max(item.calculated_at for item in results)
    source_lot_ids = {
        str(source.award.tender_lot_id)
        for snapshot in results
        for source in snapshot.sources.all()
    }
    return Response({
        'status': 'ready',
        'scope': scope,
        'period_start': period_start,
        'period_end': period_end,
        'calculated_at': calculated_at,
        'source_lot_count': len(source_lot_ids),
        'results': CompetitorAnalyticsSerializer(results, many=True).data,
        'disclaimer': (
            "Tarixiy ochiq ma'lumotlarga asoslangan statistika; "
            "g'alaba kafolati emas."
        ),
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def competitor_history_view(request, stir):
    if len(stir) != 9 or not stir.isdigit():
        return Response(
            {
                'code': 'invalid_stir',
                'message': "STIR 9 ta raqamdan iborat bo'lishi kerak.",
                'details': {'stir': stir},
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
    serializer = CompetitorHistoryQuerySerializer(data=request.query_params)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data
    company = _authorize(request, data.get('company_id'))
    if company is None:
        return _profile_required_response()

    snapshots = CompetitorAnalytics.objects.filter(
        scope_type=CompetitorAnalytics.Scope.CATEGORY,
        competitor_stir=stir,
        source_count__gte=settings.COMPETITOR_MIN_SAMPLE_SIZE,
    ).prefetch_related('sources__award')
    if data.get('category'):
        snapshots = snapshots.filter(category=data['category'])
    consume_usage(company, UsageRecord.Metric.COMPETITOR_QUERY)
    snapshots = snapshots.order_by('-period_end', 'category', 'rank')
    if not snapshots.exists():
        return Response({
            'status': 'insufficient_data',
            'competitor_stir': stir,
            'results': [],
        })
    return Response({
        'status': 'ready',
        'competitor_stir': stir,
        'results': CompetitorAnalyticsSerializer(snapshots, many=True).data,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def competitor_freshness_view(request):
    serializer = CompanyScopeQuerySerializer(data=request.query_params)
    serializer.is_valid(raise_exception=True)
    company = _authorize(
        request,
        serializer.validated_data.get('company_id'),
    )
    if company is None:
        return _profile_required_response()

    latest = CompetitorAnalytics.objects.aggregate(
        value=Max('calculated_at'),
    )['value']
    open_issues = CompetitorDataQualityIssue.objects.filter(
        resolved_at__isnull=True,
    ).count()
    if latest is None:
        freshness_status = 'empty'
        age_seconds = None
    else:
        age_seconds = max(
            int((timezone.now() - latest).total_seconds()),
            0,
        )
        freshness_status = (
            'fresh'
            if age_seconds <= settings.COMPETITOR_FRESHNESS_SECONDS
            else 'stale'
        )
    return Response({
        'status': freshness_status,
        'calculated_at': latest,
        'age_seconds': age_seconds,
        'freshness_slo_seconds': settings.COMPETITOR_FRESHNESS_SECONDS,
        'open_data_quality_issues': open_issues,
    })
