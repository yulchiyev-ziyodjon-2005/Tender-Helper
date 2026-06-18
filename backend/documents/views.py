import logging

from django.db.models import Prefetch
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from analysis.models import AITenderAnalysis
from documents.models import (
    DocumentAuditEvent,
    DocumentExport,
    GeneratedDocument,
    TenderDocumentTemplate,
)
from documents.serializers import (
    ApproveDocumentSerializer,
    DocumentExportSerializer,
    ExportDocumentSerializer,
    GenerateDocumentSerializer,
    GeneratedDocumentDetailSerializer,
    GeneratedDocumentListSerializer,
    GeneratedDocumentRevisionSerializer,
    TenderDocumentTemplateSerializer,
    UpdateDocumentSerializer,
)
from documents.services.exports import (
    request_export,
    verify_download_token,
)
from documents.services.lifecycle import (
    approve_document,
    archive_document,
    request_generation,
    update_document,
)
from documents.tasks import export_document_task, generate_document_task
from subscriptions.constants import Feature
from subscriptions.services.entitlements import authorize_feature
from subscriptions.services.membership import accessible_companies
from subscriptions.services.membership import require_company_permission
from teams.models import TeamPermission
from tenders.models import TenderLot

logger = logging.getLogger(__name__)


class DocumentPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


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


def _owned_documents(user):
    return (
        GeneratedDocument.objects.filter(company__in=accessible_companies(user))
        .select_related('company', 'template', 'tender_lot', 'created_by')
        .prefetch_related(
            Prefetch(
                'exports',
                queryset=DocumentExport.objects.order_by('-created_at'),
            ),
        )
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def template_list_view(request):
    company = _current_company(request.user, request.query_params.get('company_id'))
    if company is None:
        return _profile_required_response()
    authorize_feature(request.user, company, Feature.DOCUMENT_GENERATION)
    templates = TenderDocumentTemplate.objects.filter(
        is_active=True,
        is_published=True,
    )
    document_type = request.query_params.get('document_type')
    language = request.query_params.get('language')
    if document_type:
        templates = templates.filter(document_type=document_type)
    if language:
        templates = templates.filter(language=language)
    return Response(TenderDocumentTemplateSerializer(templates, many=True).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def document_list_view(request):
    documents = _owned_documents(request.user)
    company_id = request.query_params.get('company_id')
    document_status = request.query_params.get('status')
    document_type = request.query_params.get('document_type')
    language = request.query_params.get('language')
    tender_lot_id = request.query_params.get('tender_lot_id')
    if company_id:
        documents = documents.filter(company_id=company_id)
    if document_status:
        documents = documents.filter(status=document_status)
    if document_type:
        documents = documents.filter(document_type=document_type)
    if language:
        documents = documents.filter(language=language)
    if tender_lot_id:
        documents = documents.filter(tender_lot_id=tender_lot_id)
    paginator = DocumentPagination()
    page = paginator.paginate_queryset(documents, request)
    serializer = GeneratedDocumentListSerializer(page, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_document_view(request):
    serializer = GenerateDocumentSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data
    company = _current_company(request.user, data.get('company_id'))
    if company is None:
        return _profile_required_response()
    require_company_permission(
        request.user,
        company,
        TeamPermission.GENERATE_DOCUMENTS,
    )
    tender = get_object_or_404(TenderLot, pk=data['tender_lot_id'])
    template = get_object_or_404(
        TenderDocumentTemplate,
        pk=data['template_id'],
    )
    analysis = None
    if data.get('analysis_id'):
        analysis = get_object_or_404(
            AITenderAnalysis.objects.filter(
                company=company,
                tender_lot=tender,
            ),
            pk=data['analysis_id'],
        )
        if analysis.analysis_status != AITenderAnalysis.Status.COMPLETED:
            return Response(
                {
                    'code': 'analysis_not_ready',
                    'message': 'Faqat yakunlangan tahlil kontekstga qo‘shiladi.',
                    'details': {'analysis_id': analysis.id},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
    document = request_generation(
        user=request.user,
        company=company,
        tender=tender,
        template=template,
        analysis=analysis,
        title=data['title'],
        user_instructions=data['user_instructions'],
    )
    try:
        generate_document_task.delay(str(document.id))
    except Exception:
        logger.exception('Document task dispatch failed document=%s', document.id)
        document.status = GeneratedDocument.Status.FAILED
        document.error_message = 'Document generation queue is unavailable'
        document.failed_at = timezone.now()
        document.generation_metadata = {
            **document.generation_metadata,
            'provider_status': 'failed',
            'error_code': 'task_dispatch_failed',
        }
        document.save(
            update_fields=[
                'status',
                'error_message',
                'failed_at',
                'generation_metadata',
                'updated_at',
            ],
        )
        DocumentAuditEvent.objects.create(
            document=document,
            actor=None,
            event=DocumentAuditEvent.Event.GENERATION_FAILED,
            metadata={'error_code': 'task_dispatch_failed'},
        )
    document.refresh_from_db()
    return Response(
        GeneratedDocumentDetailSerializer(
            document,
            context={'request': request},
        ).data,
        status=status.HTTP_202_ACCEPTED,
    )


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def document_detail_view(request, pk):
    document = get_object_or_404(_owned_documents(request.user), pk=pk)
    if request.method == 'GET':
        return Response(
            GeneratedDocumentDetailSerializer(
                document,
                context={'request': request},
            ).data,
        )

    require_company_permission(
        request.user,
        document.company,
        TeamPermission.EDIT_DOCUMENTS,
    )
    serializer = UpdateDocumentSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    updated = update_document(
        user=request.user,
        document=document,
        expected_edit_version=serializer.validated_data['edit_version'],
        content_json=serializer.validated_data['content_json'],
        title=serializer.validated_data.get('title'),
        change_summary=serializer.validated_data['change_summary'],
    )
    return Response(
        GeneratedDocumentDetailSerializer(
            updated,
            context={'request': request},
        ).data,
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def approve_document_view(request, pk):
    document = get_object_or_404(_owned_documents(request.user), pk=pk)
    require_company_permission(
        request.user,
        document.company,
        TeamPermission.EDIT_DOCUMENTS,
    )
    serializer = ApproveDocumentSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    approved = approve_document(
        user=request.user,
        document=document,
        expected_edit_version=serializer.validated_data['edit_version'],
    )
    return Response(
        GeneratedDocumentDetailSerializer(
            approved,
            context={'request': request},
        ).data,
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def archive_document_view(request, pk):
    document = get_object_or_404(_owned_documents(request.user), pk=pk)
    require_company_permission(
        request.user,
        document.company,
        TeamPermission.EDIT_DOCUMENTS,
    )
    archived = archive_document(user=request.user, document=document)
    return Response(
        GeneratedDocumentDetailSerializer(
            archived,
            context={'request': request},
        ).data,
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def document_versions_view(request, pk):
    document = get_object_or_404(_owned_documents(request.user), pk=pk)
    return Response(
        GeneratedDocumentRevisionSerializer(
            document.revisions.select_related('created_by'),
            many=True,
        ).data,
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def export_document_view(request, pk):
    document = get_object_or_404(_owned_documents(request.user), pk=pk)
    require_company_permission(
        request.user,
        document.company,
        TeamPermission.EXPORT_DOCUMENTS,
    )
    serializer = ExportDocumentSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    export = request_export(
        user=request.user,
        document=document,
        export_format=serializer.validated_data['format'],
    )
    try:
        export_document_task.delay(str(export.id))
    except Exception:
        logger.exception('Export task dispatch failed export=%s', export.id)
        export.status = DocumentExport.Status.FAILED
        export.error_message = 'Document export queue is unavailable'
        export.failed_at = timezone.now()
        export.save(
            update_fields=[
                'status',
                'error_message',
                'failed_at',
                'updated_at',
            ],
        )
        DocumentAuditEvent.objects.create(
            document=document,
            actor=None,
            event=DocumentAuditEvent.Event.EXPORT_FAILED,
            metadata={
                'export_id': str(export.id),
                'error_code': 'task_dispatch_failed',
            },
        )
    export.refresh_from_db()
    return Response(
        DocumentExportSerializer(
            export,
            context={'request': request},
        ).data,
        status=status.HTTP_202_ACCEPTED,
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_status_view(request, pk):
    export = get_object_or_404(
        DocumentExport.objects.select_related('document').filter(
            document__company__in=accessible_companies(request.user),
        ),
        pk=pk,
    )
    return Response(
        DocumentExportSerializer(
            export,
            context={'request': request},
        ).data,
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_download_view(request, pk):
    export = get_object_or_404(
        DocumentExport.objects.select_related('document').filter(
            document__company__in=accessible_companies(request.user),
            status=DocumentExport.Status.COMPLETED,
        ),
        pk=pk,
    )
    verify_download_token(export, request.query_params.get('token', ''))
    filename = f'{export.document.title}.{export.format}'
    return FileResponse(
        export.file.open('rb'),
        as_attachment=True,
        filename=filename,
        content_type=export.metadata.get(
            'content_type',
            'application/octet-stream',
        ),
    )
