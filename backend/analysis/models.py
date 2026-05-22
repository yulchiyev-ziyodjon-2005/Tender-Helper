"""
TenderHelper AI analysis and calculator models.
"""

import uuid
from decimal import Decimal

from django.conf import settings
from django.db import models


class AITenderAnalysis(models.Model):
    """AI tahlil natijalari."""

    class Status(models.TextChoices):
        PENDING = 'pending', 'Kutilmoqda'
        PROCESSING_DOCS = 'processing_docs', 'Hujjatlar qayta ishlanmoqda'
        CHECKING_COMPLIANCE = 'checking_compliance', 'Talablar tekshirilmoqda'
        DETECTING_RED_FLAGS = 'detecting_red_flags', 'Risklar aniqlanmoqda'
        COMPLETED = 'completed', 'Tayyor'
        FAILED = 'failed', 'Xatolik'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(
        'companies.CompanyProfile',
        on_delete=models.CASCADE,
        related_name='analyses',
    )
    tender_lot = models.ForeignKey(
        'tenders.TenderLot',
        on_delete=models.CASCADE,
        related_name='analyses',
    )
    analysis_status = models.CharField(
        max_length=40,
        choices=Status.choices,
        default=Status.PENDING,
    )
    eligibility_score = models.PositiveSmallIntegerField(default=0)
    summary_text = models.TextField(null=True, blank=True)
    missing_documents = models.JSONField(default=list, blank=True)
    red_flags = models.JSONField(default=list, blank=True)
    requirements = models.JSONField(default=list, blank=True)
    standards = models.JSONField(default=list, blank=True)
    decision = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ai_tender_analyses'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['company', 'analysis_status']),
            models.Index(fields=['tender_lot']),
        ]

    def __str__(self):
        return f"{self.company.company_name} / {self.tender_lot.lot_number}"


class SmartCalculator(models.Model):
    """Anti-demping va stop-loss kalkulyatori."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    analysis = models.OneToOneField(
        AITenderAnalysis,
        on_delete=models.CASCADE,
        related_name='calculator',
    )
    raw_material_cost = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    logistics_cost = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    labor_cost = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    other_expenses = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    calculated_vat = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    calculated_operator_fee = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    calculated_zakalat = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    min_safe_price = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    recommended_price = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    net_profit = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'smart_calculators'

    def calculate(self):
        """Moliyaviy natijalarni sozlamalardagi stavkalar asosida hisoblaydi."""
        tannarx = (
            self.raw_material_cost
            + self.logistics_cost
            + self.labor_cost
            + self.other_expenses
        )
        vat_rate = Decimal(str(getattr(settings, 'VAT_RATE', 0.12)))
        operator_rate = Decimal(str(getattr(settings, 'OPERATOR_FEE_RATE', 0.0015)))
        zakalat_rate = Decimal(str(getattr(settings, 'ZAKALAT_RATE', 0.03)))
        margin = Decimal('0.15')

        tender = self.analysis.tender_lot
        zakalat = tender.zakalat_amount or (tender.start_price * zakalat_rate)

        self.calculated_vat = tannarx * vat_rate
        self.calculated_operator_fee = tannarx * operator_rate
        self.calculated_zakalat = zakalat
        self.min_safe_price = tannarx + self.calculated_vat + self.calculated_operator_fee + zakalat
        self.recommended_price = self.min_safe_price * (Decimal('1') + margin)
        self.net_profit = tender.start_price - self.recommended_price
        return self
