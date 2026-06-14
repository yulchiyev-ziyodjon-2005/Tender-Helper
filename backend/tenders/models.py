"""
TenderHelper tender aggregation models.
"""

import uuid

from django.conf import settings
from django.db import models


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
    lot_number = models.CharField(max_length=100, unique=True)
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
            models.Index(fields=['platform_source']),
            models.Index(fields=['region']),
            models.Index(fields=['category']),
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
