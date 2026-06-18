import logging
from time import monotonic

from django.db import transaction
from django.db.models import Max
from django.utils import timezone

from documents.exceptions import (
    DocumentStateConflict,
    EditVersionConflict,
    TemplateUnavailable,
)
from documents.models import (
    DocumentAuditEvent,
    GeneratedDocument,
    GeneratedDocumentRevision,
)
from documents.services.content import render_content
from documents.services.context import (
    build_context_snapshot,
    validate_required_company_fields,
)
from documents.services.providers import get_document_generation_provider
from subscriptions.constants import Feature
from subscriptions.models import UsageRecord
from subscriptions.services.entitlements import authorize_feature
from subscriptions.services.usage import consume_usage

logger = logging.getLogger(__name__)


def _next_revision_version(document):
    current = document.revisions.aggregate(value=Max('version'))['value'] or 0
    return current + 1


def _create_revision(document, *, source, actor, change_summary=''):
    return GeneratedDocumentRevision.objects.create(
        document=document,
        version=_next_revision_version(document),
        title=document.title,
        content_json=document.content_json,
        content_html=document.content_html,
        content_text=document.content_text,
        source=source,
        change_summary=change_summary,
        created_by=actor,
    )


@transaction.atomic
def request_generation(
    *,
    user,
    company,
    tender,
    template,
    analysis=None,
    title='',
    user_instructions='',
):
    authorize_feature(user, company, Feature.DOCUMENT_GENERATION)
    if not template.is_active or not template.is_published:
        raise TemplateUnavailable()
    validate_required_company_fields(company, template)
    if analysis is not None and (
        analysis.company_id != company.id
        or analysis.tender_lot_id != tender.id
    ):
        raise ValueError('Analysis does not belong to this company and tender.')
    context_snapshot = build_context_snapshot(company, tender, analysis)
    consume_usage(company, UsageRecord.Metric.DOCUMENT_GENERATION)
    document = GeneratedDocument.objects.create(
        company=company,
        tender_lot=tender,
        template=template,
        analysis=analysis,
        created_by=user,
        title=title or f'{template.name} - {tender.lot_number}',
        document_type=template.document_type,
        language=template.language,
        status=GeneratedDocument.Status.GENERATING,
        context_snapshot=context_snapshot,
        generation_metadata={
            'user_instructions': user_instructions,
            'provider_status': 'queued',
        },
        template_version=template.version,
    )
    DocumentAuditEvent.objects.create(
        document=document,
        actor=user,
        event=DocumentAuditEvent.Event.GENERATION_REQUESTED,
        metadata={
            'template_id': str(template.id),
            'template_version': template.version,
            'tender_lot_id': str(tender.id),
        },
    )
    return document


@transaction.atomic
def run_generation(document_id):
    document = (
        GeneratedDocument.objects.select_for_update()
        .select_related('template', 'created_by')
        .get(pk=document_id)
    )
    if document.status != GeneratedDocument.Status.GENERATING:
        return document

    started = monotonic()
    try:
        provider = get_document_generation_provider()
        result = provider.generate(
            template=document.template,
            context=document.context_snapshot,
            user_instructions=document.generation_metadata.get(
                'user_instructions',
                '',
            ),
        )
        content_html, content_text = render_content(result.content_json)
    except Exception as exc:
        logger.exception('Document generation failed document=%s', document.id)
        document.status = GeneratedDocument.Status.FAILED
        document.error_message = 'AI document provider is temporarily unavailable'
        document.failed_at = timezone.now()
        document.generation_metadata = {
            **document.generation_metadata,
            'provider_status': 'failed',
            'error_code': getattr(exc, 'code', 'document_generation_failed'),
            'duration_ms': int((monotonic() - started) * 1000),
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
            metadata={
                'error_code': getattr(
                    exc,
                    'code',
                    'document_generation_failed',
                ),
            },
        )
        return document

    document.content_json = result.content_json
    document.content_html = content_html
    document.content_text = content_text
    document.status = GeneratedDocument.Status.DRAFT
    document.edit_version = 1
    document.error_message = ''
    document.generated_at = timezone.now()
    document.generation_metadata = {
        **result.metadata,
        'provider_status': 'completed',
        'duration_ms': int((monotonic() - started) * 1000),
    }
    document.save(
        update_fields=[
            'content_json',
            'content_html',
            'content_text',
            'status',
            'edit_version',
            'error_message',
            'generated_at',
            'generation_metadata',
            'updated_at',
        ],
    )
    _create_revision(
        document,
        source=GeneratedDocumentRevision.Source.GENERATION,
        actor=document.created_by,
        change_summary='Initial AI-generated draft',
    )
    DocumentAuditEvent.objects.create(
        document=document,
        actor=None,
        event=DocumentAuditEvent.Event.GENERATION_COMPLETED,
        metadata={
            'provider': result.metadata.get('provider'),
            'model': result.metadata.get('model'),
        },
    )
    return document


@transaction.atomic
def update_document(
    *,
    user,
    document,
    expected_edit_version,
    content_json,
    title=None,
    change_summary='',
):
    authorize_feature(user, document.company, Feature.DOCUMENT_GENERATION)
    locked = GeneratedDocument.objects.select_for_update().get(pk=document.pk)
    allowed = (
        GeneratedDocument.Status.DRAFT,
        GeneratedDocument.Status.APPROVED,
        GeneratedDocument.Status.EXPORTED,
    )
    if locked.status not in allowed:
        raise DocumentStateConflict(
            current_status=locked.status,
            allowed_statuses=allowed,
        )
    if locked.edit_version != expected_edit_version:
        raise EditVersionConflict(
            expected=expected_edit_version,
            current=locked.edit_version,
        )
    content_html, content_text = render_content(content_json)
    if title is not None:
        locked.title = title
    locked.content_json = content_json
    locked.content_html = content_html
    locked.content_text = content_text
    locked.edit_version += 1
    locked.last_edited_by = user
    locked.status = GeneratedDocument.Status.DRAFT
    locked.approved_by = None
    locked.approved_at = None
    locked.error_message = ''
    locked.save(
        update_fields=[
            'title',
            'content_json',
            'content_html',
            'content_text',
            'edit_version',
            'last_edited_by',
            'status',
            'approved_by',
            'approved_at',
            'error_message',
            'updated_at',
        ],
    )
    _create_revision(
        locked,
        source=GeneratedDocumentRevision.Source.EDIT,
        actor=user,
        change_summary=change_summary,
    )
    DocumentAuditEvent.objects.create(
        document=locked,
        actor=user,
        event=DocumentAuditEvent.Event.EDITED,
        metadata={'edit_version': locked.edit_version},
    )
    return locked


@transaction.atomic
def approve_document(*, user, document, expected_edit_version):
    authorize_feature(user, document.company, Feature.DOCUMENT_GENERATION)
    locked = GeneratedDocument.objects.select_for_update().get(pk=document.pk)
    if locked.status != GeneratedDocument.Status.DRAFT:
        raise DocumentStateConflict(
            current_status=locked.status,
            allowed_statuses=(GeneratedDocument.Status.DRAFT,),
        )
    if locked.edit_version != expected_edit_version:
        raise EditVersionConflict(
            expected=expected_edit_version,
            current=locked.edit_version,
        )
    locked.status = GeneratedDocument.Status.APPROVED
    locked.approved_by = user
    locked.approved_at = timezone.now()
    locked.save(
        update_fields=[
            'status',
            'approved_by',
            'approved_at',
            'updated_at',
        ],
    )
    _create_revision(
        locked,
        source=GeneratedDocumentRevision.Source.APPROVAL,
        actor=user,
        change_summary='User approved document',
    )
    DocumentAuditEvent.objects.create(
        document=locked,
        actor=user,
        event=DocumentAuditEvent.Event.APPROVED,
        metadata={'edit_version': locked.edit_version},
    )
    return locked


@transaction.atomic
def archive_document(*, user, document):
    authorize_feature(user, document.company, Feature.DOCUMENT_GENERATION)
    locked = GeneratedDocument.objects.select_for_update().get(pk=document.pk)
    allowed = (
        GeneratedDocument.Status.DRAFT,
        GeneratedDocument.Status.APPROVED,
        GeneratedDocument.Status.EXPORTED,
        GeneratedDocument.Status.FAILED,
    )
    if locked.status not in allowed:
        raise DocumentStateConflict(
            current_status=locked.status,
            allowed_statuses=allowed,
        )
    locked.status = GeneratedDocument.Status.ARCHIVED
    locked.archived_at = timezone.now()
    locked.save(update_fields=['status', 'archived_at', 'updated_at'])
    DocumentAuditEvent.objects.create(
        document=locked,
        actor=user,
        event=DocumentAuditEvent.Event.ARCHIVED,
    )
    return locked
