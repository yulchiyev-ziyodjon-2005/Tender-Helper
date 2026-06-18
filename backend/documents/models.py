import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from documents.constants import (
    CANONICAL_DOCUMENT_VERSION,
    COMPANY_CONTEXT_FIELDS,
)


class DocumentType(models.TextChoices):
    APPLICATION = 'application', 'Tender application'
    GUARANTEE = 'guarantee', 'Guarantee letter'
    COMMERCIAL = 'commercial', 'Commercial proposal'
    COMPLIANCE = 'compliance', 'Technical compliance'
    OTHER = 'other', 'Other official letter'


class DocumentLanguage(models.TextChoices):
    UZ = 'uz', 'O‘zbek'
    RU = 'ru', 'Русский'


class TenderDocumentTemplate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.SlugField(max_length=100)
    name = models.CharField(max_length=255)
    document_type = models.CharField(max_length=30, choices=DocumentType.choices)
    language = models.CharField(
        max_length=10,
        choices=DocumentLanguage.choices,
    )
    version = models.PositiveIntegerField()
    prompt_template = models.TextField()
    content_schema = models.JSONField(default=dict)
    required_company_fields = models.JSONField(default=list)
    is_active = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='created_document_templates',
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    IMMUTABLE_FIELDS = (
        'code',
        'name',
        'document_type',
        'language',
        'version',
        'prompt_template',
        'content_schema',
        'required_company_fields',
        'created_by_id',
    )

    class Meta:
        db_table = 'tender_document_templates'
        ordering = ['document_type', 'language', '-version']
        constraints = [
            models.UniqueConstraint(
                fields=['code', 'language', 'version'],
                name='unique_document_template_version',
            ),
            models.UniqueConstraint(
                fields=['code', 'language'],
                condition=Q(is_active=True),
                name='one_active_document_template',
            ),
            models.CheckConstraint(
                condition=Q(version__gt=0),
                name='document_template_version_positive',
            ),
        ]
        indexes = [
            models.Index(fields=['document_type', 'language', 'is_active']),
            models.Index(fields=['code', 'is_active']),
        ]

    def __str__(self):
        return f'{self.name} ({self.language} v{self.version})'

    def clean(self):
        super().clean()
        errors = {}
        required_fields = self.required_company_fields
        if (
            not isinstance(required_fields, list)
            or any(not isinstance(item, str) for item in required_fields)
        ):
            errors['required_company_fields'] = 'Must be a list of field names.'
        else:
            unknown = set(required_fields) - COMPANY_CONTEXT_FIELDS
            if unknown:
                errors['required_company_fields'] = (
                    'Unsupported company fields: ' + ', '.join(sorted(unknown))
                )
            elif len(required_fields) != len(set(required_fields)):
                errors['required_company_fields'] = 'Field names must be unique.'
        if not isinstance(self.content_schema, dict):
            errors['content_schema'] = 'Content schema must be a JSON object.'
        elif (
            self.content_schema.get('type') != 'document'
            or self.content_schema.get('version') != CANONICAL_DOCUMENT_VERSION
        ):
            errors['content_schema'] = (
                'Content schema type/version is not supported.'
            )
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if self.pk:
            original = type(self).objects.filter(pk=self.pk).first()
            if original is not None:
                changed = [
                    field
                    for field in self.IMMUTABLE_FIELDS
                    if getattr(original, field) != getattr(self, field)
                ]
                if changed:
                    raise ValidationError({
                        field: 'Published template versions are immutable.'
                        for field in changed
                    })
        self.full_clean()
        return super().save(*args, **kwargs)


class GeneratedDocument(models.Model):
    class Status(models.TextChoices):
        GENERATING = 'generating', 'Generating'
        DRAFT = 'draft', 'Draft'
        APPROVED = 'approved', 'Approved'
        EXPORTED = 'exported', 'Exported'
        FAILED = 'failed', 'Failed'
        ARCHIVED = 'archived', 'Archived'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(
        'companies.CompanyProfile',
        on_delete=models.CASCADE,
        related_name='generated_documents',
    )
    tender_lot = models.ForeignKey(
        'tenders.TenderLot',
        on_delete=models.PROTECT,
        related_name='generated_documents',
    )
    template = models.ForeignKey(
        TenderDocumentTemplate,
        on_delete=models.PROTECT,
        related_name='generated_documents',
    )
    analysis = models.ForeignKey(
        'analysis.AITenderAnalysis',
        on_delete=models.SET_NULL,
        related_name='generated_documents',
        null=True,
        blank=True,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='generated_documents',
    )
    last_edited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='edited_documents',
        null=True,
        blank=True,
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='approved_documents',
        null=True,
        blank=True,
    )
    title = models.CharField(max_length=500)
    document_type = models.CharField(max_length=30, choices=DocumentType.choices)
    language = models.CharField(max_length=10, choices=DocumentLanguage.choices)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.GENERATING,
    )
    content_json = models.JSONField(default=dict, blank=True)
    content_html = models.TextField(blank=True, default='')
    content_text = models.TextField(blank=True, default='')
    context_snapshot = models.JSONField(default=dict)
    generation_metadata = models.JSONField(default=dict, blank=True)
    template_version = models.PositiveIntegerField()
    edit_version = models.PositiveIntegerField(default=0)
    error_message = models.TextField(blank=True, default='')
    generated_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    exported_at = models.DateTimeField(null=True, blank=True)
    failed_at = models.DateTimeField(null=True, blank=True)
    archived_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'generated_documents'
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['company', 'status', '-updated_at']),
            models.Index(fields=['tender_lot', 'document_type']),
            models.Index(fields=['created_by', '-created_at']),
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(template_version__gt=0),
                name='generated_document_template_version_positive',
            ),
        ]

    def __str__(self):
        return self.title

    def delete(self, *args, **kwargs):
        raise ValidationError('Generated documents must be archived, not deleted.')


class GeneratedDocumentRevision(models.Model):
    class Source(models.TextChoices):
        GENERATION = 'generation', 'Generation'
        EDIT = 'edit', 'Edit'
        APPROVAL = 'approval', 'Approval'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(
        GeneratedDocument,
        on_delete=models.CASCADE,
        related_name='revisions',
    )
    version = models.PositiveIntegerField()
    title = models.CharField(max_length=500)
    content_json = models.JSONField(default=dict)
    content_html = models.TextField()
    content_text = models.TextField()
    source = models.CharField(max_length=20, choices=Source.choices)
    change_summary = models.CharField(max_length=500, blank=True, default='')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='document_revisions',
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'generated_document_revisions'
        ordering = ['-version']
        constraints = [
            models.UniqueConstraint(
                fields=['document', 'version'],
                name='unique_document_revision_version',
            ),
            models.CheckConstraint(
                condition=Q(version__gt=0),
                name='document_revision_version_positive',
            ),
        ]

    def __str__(self):
        return f'{self.document_id} v{self.version}'


class DocumentExport(models.Model):
    class Format(models.TextChoices):
        PDF = 'pdf', 'PDF'
        DOCX = 'docx', 'DOCX'

    class Status(models.TextChoices):
        QUEUED = 'queued', 'Queued'
        PROCESSING = 'processing', 'Processing'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(
        GeneratedDocument,
        on_delete=models.CASCADE,
        related_name='exports',
    )
    revision = models.ForeignKey(
        GeneratedDocumentRevision,
        on_delete=models.PROTECT,
        related_name='exports',
    )
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='document_exports',
    )
    format = models.CharField(max_length=10, choices=Format.choices)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.QUEUED,
    )
    file = models.FileField(
        upload_to='documents/exports/%Y/%m/',
        null=True,
        blank=True,
    )
    storage_key = models.CharField(max_length=500, blank=True, default='')
    checksum_sha256 = models.CharField(max_length=64, blank=True, default='')
    file_size = models.PositiveBigIntegerField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True, default='')
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    failed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'document_exports'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['document', 'status', '-created_at']),
            models.Index(fields=['requested_by', '-created_at']),
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(file_size__isnull=True) | Q(file_size__gte=0),
                name='document_export_file_size_non_negative',
            ),
        ]

    def __str__(self):
        return f'{self.document_id} {self.format} {self.status}'


class DocumentAuditEvent(models.Model):
    class Event(models.TextChoices):
        GENERATION_REQUESTED = 'generation_requested', 'Generation requested'
        GENERATION_COMPLETED = 'generation_completed', 'Generation completed'
        GENERATION_FAILED = 'generation_failed', 'Generation failed'
        EDITED = 'edited', 'Edited'
        APPROVED = 'approved', 'Approved'
        EXPORT_REQUESTED = 'export_requested', 'Export requested'
        EXPORT_COMPLETED = 'export_completed', 'Export completed'
        EXPORT_FAILED = 'export_failed', 'Export failed'
        ARCHIVED = 'archived', 'Archived'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(
        GeneratedDocument,
        on_delete=models.CASCADE,
        related_name='audit_events',
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='document_audit_events',
        null=True,
        blank=True,
    )
    event = models.CharField(max_length=40, choices=Event.choices)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'document_audit_events'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['document', '-created_at']),
            models.Index(fields=['event', '-created_at']),
        ]

    def __str__(self):
        return f'{self.document_id} {self.event}'

    def delete(self, *args, **kwargs):
        raise ValidationError('Document audit events are append-only.')
