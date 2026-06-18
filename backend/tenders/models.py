"""
TenderHelper tender aggregation models.
"""

import uuid

from django.conf import settings
from django.db import models
from django.db.models import Q


class TenderSource(models.Model):
    """Canonical configuration and identity namespace for a tender portal."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.SlugField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    base_url = models.URLField(blank=True, default='')
    is_active = models.BooleanField(default=True)
    configuration = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tender_sources'
        ordering = ['code']

    def __str__(self):
        return self.name


class TenderLot(models.Model):
    """Milliy portallardan yoki qo'lda kiritilgan yagona tender loti."""

    class PlatformSource(models.TextChoices):
        XARID_UZEX = 'xarid_uzex', 'xarid.uzex.uz'
        DXARID_UZEX = 'dxarid_uzex', 'dxarid.uzex.uz'
        EXARID_UZEX = 'exarid_uzex', 'exarid.uzex.uz'
        E_AUKSION = 'e_auksion', 'e-auksion.uz'
        MANUAL = 'manual', "Qo'lda kiritilgan"

    class Status(models.TextChoices):
        ACTIVE = 'active', 'Faol'
        COMPLETED = 'completed', 'Yakunlangan'
        CANCELLED = 'cancelled', 'Bekor qilingan'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source = models.ForeignKey(
        TenderSource,
        on_delete=models.PROTECT,
        related_name='lots',
    )
    external_id = models.CharField(max_length=255, blank=True, default='')
    lot_number = models.CharField(max_length=100)
    platform_source = models.CharField(
        max_length=30,
        choices=PlatformSource.choices,
        default=PlatformSource.MANUAL,
    )
    title = models.TextField()
    buyer_name = models.CharField(max_length=500, blank=True, default='')
    start_price = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    zakalat_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    region = models.CharField(max_length=100, blank=True, default='')
    category = models.CharField(max_length=255, blank=True, default='')
    posted_date = models.DateTimeField()
    deadline = models.DateTimeField()
    status = models.CharField(
        max_length=50,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    raw_portal_url = models.URLField(blank=True, default='')
    raw_json = models.JSONField(default=dict, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='manual_tenders',
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tender_lots'
        ordering = ['-posted_date']
        indexes = [
            models.Index(fields=['status', 'deadline']),
            models.Index(fields=['source', 'status', 'deadline']),
            models.Index(fields=['platform_source']),
            models.Index(fields=['region']),
            models.Index(fields=['category']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['source', 'external_id'],
                condition=Q(source__isnull=False) & ~Q(external_id=''),
                name='unique_tender_source_external_id',
            ),
            models.CheckConstraint(
                condition=Q(start_price__gte=0),
                name='tender_start_price_non_negative',
            ),
            models.CheckConstraint(
                condition=Q(zakalat_amount__gte=0),
                name='tender_zakalat_non_negative',
            ),
            models.CheckConstraint(
                condition=Q(deadline__gt=models.F('posted_date')),
                name='tender_deadline_after_posted',
            ),
            models.CheckConstraint(
                condition=(
                    Q(
                        platform_source='manual',
                        external_id='',
                    )
                    | (
                        ~Q(platform_source='manual')
                        & ~Q(external_id='')
                    )
                ),
                name='tender_external_identity_matches_source_type',
            ),
        ]

    def __str__(self):
        return f"{self.lot_number} - {self.title[:80]}"


class TenderDocumentChunk(models.Model):
    """Tender hujjatlari matn bo'laklari."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tender_lot = models.ForeignKey(
        TenderLot,
        on_delete=models.CASCADE,
        related_name='chunks',
    )
    file_name = models.CharField(max_length=255)
    chunk_index = models.PositiveIntegerField(default=0)
    raw_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tender_document_chunks'
        ordering = ['tender_lot_id', 'chunk_index']
        unique_together = ('tender_lot', 'file_name', 'chunk_index')

    def __str__(self):
        return f"{self.tender_lot.lot_number} chunk {self.chunk_index}"


class ScrapeRun(models.Model):
    """Tracks one external portal ingestion batch."""

    class Status(models.TextChoices):
        RUNNING = 'running', 'Running'
        SUCCESS = 'success', 'Success'
        FAILED = 'failed', 'Failed'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source = models.ForeignKey(
        TenderSource,
        on_delete=models.PROTECT,
        related_name='scrape_runs',
    )
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.RUNNING,
    )
    processed_count = models.PositiveIntegerField(default=0)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'scrape_runs'
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['source', 'status', 'started_at']),
        ]

    def __str__(self):
        return f'{self.source.code} scrape {self.started_at:%Y-%m-%d %H:%M:%S}'


class TenderDocument(models.Model):
    """Idempotent external lot payload cache before/alongside TenderLot."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    scrape_run = models.ForeignKey(
        ScrapeRun,
        on_delete=models.SET_NULL,
        related_name='documents',
        null=True,
        blank=True,
    )
    source = models.ForeignKey(
        TenderSource,
        on_delete=models.PROTECT,
        related_name='documents',
    )
    tender_id = models.CharField(max_length=255)
    tender_lot = models.ForeignKey(
        TenderLot,
        on_delete=models.SET_NULL,
        related_name='source_documents',
        null=True,
        blank=True,
    )
    title = models.TextField()
    organization_name = models.CharField(max_length=500, blank=True, default='')
    total_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    category = models.CharField(max_length=255, blank=True, default='')
    published_at = models.DateTimeField()
    deadline_at = models.DateTimeField()
    raw_payload = models.JSONField(default=dict, blank=True)
    hash_sum = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tender_documents'
        ordering = ['-published_at']
        indexes = [
            models.Index(fields=['source', 'tender_id']),
            models.Index(fields=['source', 'deadline_at']),
            models.Index(fields=['hash_sum']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['source', 'tender_id'],
                name='unique_tender_document_source_tender_id',
            ),
            models.CheckConstraint(
                condition=Q(total_amount__gte=0),
                name='tender_document_total_amount_non_negative',
            ),
            models.CheckConstraint(
                condition=Q(deadline_at__gt=models.F('published_at')),
                name='tender_document_deadline_after_published',
            ),
        ]

    def __str__(self):
        return f'{self.source.code}:{self.tender_id}'


class ScrapeError(models.Model):
    """Persistent ingestion failure log for observability and replay."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    scrape_run = models.ForeignKey(
        ScrapeRun,
        on_delete=models.CASCADE,
        related_name='errors',
    )
    source = models.ForeignKey(
        TenderSource,
        on_delete=models.PROTECT,
        related_name='scrape_errors',
    )
    error_message = models.TextField()
    traceback = models.TextField(blank=True, default='')
    failed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'scrape_errors'
        ordering = ['-failed_at']
        indexes = [
            models.Index(fields=['source', 'failed_at']),
        ]

    def __str__(self):
        return f'{self.source.code}: {self.error_message[:80]}'
