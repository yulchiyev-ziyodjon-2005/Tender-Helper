import logging

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from subscriptions.models import UsageRecord
from subscriptions.services.membership import (
    accessible_companies,
    require_company_permission,
)
from subscriptions.services.usage import consume_usage
from teams.models import TeamPermission
from tenders.models import TenderLot
from .models import AITenderAnalysis, AnalysisRun, SmartCalculator
from .serializers import (
    AITenderAnalysisSerializer,
    AnalysisStatusSerializer,
    CalculatorInputSerializer,
    LegalKnowledgeSourceSerializer,
    SmartCalculatorSerializer,
    StartAnalysisSerializer,
    StartAnalysisResponseSerializer,
)
from .services.legal_sources import sync_official_legal_sources
from .tasks import run_analysis_task

logger = logging.getLogger(__name__)


def _current_company(user, company_id=None):
    companies = accessible_companies(user)
    if company_id:
        return get_object_or_404(companies, id=company_id)
    return companies.order_by('-created_at').first()


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_analysis_view(request):
    serializer = StartAnalysisSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    company = _current_company(request.user, data.get('company_id'))
    if company is None:
        return Response(
            {
                'error': 'profile_required',
                'message': 'AI tahlil uchun avval kompaniya profilini yarating',
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    tender = get_object_or_404(TenderLot, id=data['lot_id'])
    require_company_permission(
        request.user,
        company,
        TeamPermission.RUN_AI_ANALYSIS,
    )
    require_company_permission(
        request.user,
        company,
        TeamPermission.USE_ANALYSIS_QUOTAS,
    )
    consume_usage(company, UsageRecord.Metric.AI_ANALYSIS)
    analysis = AITenderAnalysis.objects.create(
        company=company,
        tender_lot=tender,
        analysis_status=AITenderAnalysis.Status.PENDING,
    )
    run = AnalysisRun.objects.create(
        analysis=analysis,
        additional_text=data.get('additional_text', ''),
    )

    try:
        run_analysis_task.delay(str(run.id))
    except Exception:
        logger.exception('AI analysis task dispatch failed run=%s', run.id)
        run.status = AnalysisRun.Status.FAILED
        run.progress_percent = 100
        run.error_code = 'task_dispatch_failed'
        run.error_message = 'AI analysis queue is unavailable'
        run.save(update_fields=[
            'status',
            'progress_percent',
            'error_code',
            'error_message',
            'updated_at',
        ])
        analysis.analysis_status = AITenderAnalysis.Status.FAILED
        analysis.error_message = run.error_message
        analysis.save(update_fields=[
            'analysis_status',
            'error_message',
            'updated_at',
        ])

    run.refresh_from_db()
    return Response(
        StartAnalysisResponseSerializer(run).data,
        status=status.HTTP_202_ACCEPTED,
    )


def _owned_runs(user):
    return AnalysisRun.objects.filter(
        analysis__company__in=accessible_companies(user),
    ).select_related(
        'analysis',
        'analysis__company',
        'analysis__tender_lot',
    ).prefetch_related('findings', 'model_invocations')


def _get_run_or_analysis(user, pk):
    run = _owned_runs(user).filter(id=pk).first()
    if run is not None:
        return run
    analysis = get_object_or_404(
        AITenderAnalysis.objects.filter(
            company__in=accessible_companies(user),
        ),
        id=pk,
    )
    run, _ = AnalysisRun.objects.get_or_create(
        analysis=analysis,
        defaults={
            'status': (
                AnalysisRun.Status.SUCCESS
                if analysis.analysis_status == AITenderAnalysis.Status.COMPLETED
                else AnalysisRun.Status.FAILED
                if analysis.analysis_status == AITenderAnalysis.Status.FAILED
                else AnalysisRun.Status.PENDING
            ),
            'progress_percent': (
                100
                if analysis.analysis_status in {
                    AITenderAnalysis.Status.COMPLETED,
                    AITenderAnalysis.Status.FAILED,
                }
                else 0
            ),
            'error_message': analysis.error_message,
        },
    )
    return run


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def analysis_status_view(request, pk):
    run = _get_run_or_analysis(request.user, pk)
    return Response(AnalysisStatusSerializer(run).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def analysis_result_view(request, pk):
    run = _get_run_or_analysis(request.user, pk)
    return Response(AITenderAnalysisSerializer(run.analysis).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def analysis_history_view(request):
    analyses = AITenderAnalysis.objects.filter(
        company__in=accessible_companies(request.user),
    ).select_related(
        'company',
        'tender_lot',
    )
    serializer = AITenderAnalysisSerializer(analyses, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def calculate_view(request, pk):
    analysis = get_object_or_404(
        AITenderAnalysis.objects.filter(
            company__in=accessible_companies(request.user),
        ),
        id=pk,
    )
    serializer = CalculatorInputSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    calculator, _ = SmartCalculator.objects.get_or_create(analysis=analysis)
    for field, value in serializer.validated_data.items():
        setattr(calculator, field, value)
    calculator.calculate()
    calculator.save()
    return Response(SmartCalculatorSerializer(calculator).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def legal_sources_view(request):
    sources = sync_official_legal_sources()
    include_inactive = request.query_params.get('include_inactive') == 'true'
    if not include_inactive:
        sources = [source for source in sources if source.is_active]
    return Response(LegalKnowledgeSourceSerializer(sources, many=True).data)
