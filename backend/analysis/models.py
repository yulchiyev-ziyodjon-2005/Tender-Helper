"""
TenderHelper AI analysis and calculator models.
"""

import uuid
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.db.models import Q


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
        constraints = [
            models.CheckConstraint(
                condition=Q(eligibility_score__lte=100),
                name='analysis_eligibility_score_range',
            ),
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
        constraints = [
            models.CheckConstraint(
                condition=(
                    Q(raw_material_cost__gte=0)
                    & Q(logistics_cost__gte=0)
                    & Q(labor_cost__gte=0)
                    & Q(other_expenses__gte=0)
                    & Q(calculated_vat__gte=0)
                    & Q(calculated_operator_fee__gte=0)
                    & Q(calculated_zakalat__gte=0)
                    & Q(min_safe_price__gte=0)
                    & Q(recommended_price__gte=0)
                ),
                name='calculator_amounts_non_negative',
            ),
        ]

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


class AnalysisRun(models.Model):
    """Asynchronous AI analysis orchestration state."""

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PROCESSING = 'processing', 'Processing'
        SUCCESS = 'success', 'Success'
        FAILED = 'failed', 'Failed'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    analysis = models.OneToOneField(
        AITenderAnalysis,
        on_delete=models.CASCADE,
        related_name='run',
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    prompt_version = models.CharField(max_length=40, default='analysis-v1')
    additional_text = models.TextField(blank=True, default='')
    progress_percent = models.PositiveSmallIntegerField(default=0)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    error_code = models.CharField(max_length=80, blank=True, default='')
    error_message = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'analysis_runs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['analysis']),
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(progress_percent__lte=100),
                name='analysis_run_progress_percent_range',
            ),
        ]

    def __str__(self):
        return f'{self.analysis_id} / {self.status}'


class AnalysisFinding(models.Model):
    """Structured normalized AI output block."""

    class FindingType(models.TextChoices):
        RISK = 'risk', 'Risk factor'
        COMPLIANCE = 'compliance', 'Compliance'
        REQUIREMENT = 'requirement', 'Requirement'
        DOCUMENT = 'document', 'Missing document'
        STANDARD = 'standard', 'Standard'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    run = models.ForeignKey(
        AnalysisRun,
        on_delete=models.CASCADE,
        related_name='findings',
    )
    finding_type = models.CharField(max_length=30, choices=FindingType.choices)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    risk_factor = models.CharField(max_length=80, blank=True, default='')
    rating_score = models.PositiveSmallIntegerField(default=0)
    compliance_status = models.CharField(max_length=80, blank=True, default='')
    citations = models.JSONField(default=list, blank=True)
    raw_payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'analysis_findings'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['run', 'finding_type']),
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(rating_score__lte=100),
                name='analysis_finding_rating_score_range',
            ),
        ]

    def __str__(self):
        return f'{self.finding_type}: {self.title}'


class ModelInvocation(models.Model):
    """Provider telemetry for cost, latency, and prompt governance."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    run = models.ForeignKey(
        AnalysisRun,
        on_delete=models.CASCADE,
        related_name='model_invocations',
    )
    provider = models.CharField(max_length=80, default='google_gemini')
    model_name = models.CharField(max_length=120)
    prompt_version = models.CharField(max_length=40)
    token_count = models.PositiveIntegerField(default=0)
    prompt_tokens = models.PositiveIntegerField(default=0)
    output_tokens = models.PositiveIntegerField(default=0)
    calculated_cost = models.DecimalField(
        max_digits=12,
        decimal_places=6,
        default=Decimal('0'),
    )
    latency_ms = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, default='success')
    error_code = models.CharField(max_length=80, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'model_invocations'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['run', 'provider', 'created_at']),
        ]

    def __str__(self):
        return f'{self.provider}/{self.model_name} {self.status}'


class LegalKnowledgeSource(models.Model):
    """Authoritative source policy for Uzbekistan legal RAG."""

    class AuthorityLevel(models.TextChoices):
        PRIMARY_NORMATIVE = 'primary_normative', 'Primary normative'
        OFFICIAL_CONTEXT = 'official_context', 'Official context'
        TECHNICAL_STANDARD = 'technical_standard', 'Technical standard'

    code = models.SlugField(max_length=80, unique=True)
    name = models.CharField(max_length=255)
    authority_level = models.CharField(
        max_length=40,
        choices=AuthorityLevel.choices,
    )
    base_url = models.URLField()
    allowed_domains = models.JSONField(default=list, blank=True)
    source_rank = models.PositiveSmallIntegerField(default=100)
    requires_effective_date_check = models.BooleanField(default=True)
    requires_manual_review = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'legal_knowledge_sources'
        ordering = ['source_rank', 'code']
        indexes = [
            models.Index(fields=['is_active', 'authority_level', 'source_rank']),
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(source_rank__gte=1),
                name='legal_source_rank_positive',
            ),
        ]

    def __str__(self):
        return f'{self.code}: {self.name}'


class LegalKnowledgeDocument(models.Model):
    """Versioned legal or standard document prepared for retrieval."""

    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        SUPERSEDED = 'superseded', 'Superseded'
        FUTURE = 'future', 'Future effective'
        ARCHIVED = 'archived', 'Archived'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source = models.ForeignKey(
        LegalKnowledgeSource,
        on_delete=models.PROTECT,
        related_name='documents',
    )
    external_id = models.CharField(max_length=160)
    title = models.CharField(max_length=500)
    url = models.URLField()
    language = models.CharField(max_length=12, default='uz')
    document_type = models.CharField(max_length=80, blank=True, default='')
    document_number = models.CharField(max_length=80, blank=True, default='')
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    published_at = models.DateField(null=True, blank=True)
    effective_from = models.DateField(null=True, blank=True)
    effective_to = models.DateField(null=True, blank=True)
    retrieved_at = models.DateTimeField(null=True, blank=True)
    content_hash = models.CharField(max_length=64, blank=True, default='')
    version_label = models.CharField(max_length=120, blank=True, default='')
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'legal_knowledge_documents'
        ordering = ['source__source_rank', 'title', '-effective_from']
        constraints = [
            models.UniqueConstraint(
                fields=['source', 'external_id', 'version_label'],
                name='unique_legal_document_version',
            ),
            models.CheckConstraint(
                condition=(
                    Q(effective_to__isnull=True)
                    | Q(effective_from__isnull=True)
                    | Q(effective_to__gt=models.F('effective_from'))
                ),
                name='legal_document_effective_period_valid',
            ),
        ]
        indexes = [
            models.Index(fields=['source', 'status', 'effective_from']),
            models.Index(fields=['document_type', 'document_number']),
        ]

    def __str__(self):
        return self.title


class LegalKnowledgeChunk(models.Model):
    """Retrievable article/section chunk with citation metadata."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(
        LegalKnowledgeDocument,
        on_delete=models.CASCADE,
        related_name='chunks',
    )
    chunk_index = models.PositiveIntegerField()
    section_path = models.CharField(max_length=255, blank=True, default='')
    article_number = models.CharField(max_length=40, blank=True, default='')
    text = models.TextField()
    text_hash = models.CharField(max_length=64)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'legal_knowledge_chunks'
        ordering = ['document', 'chunk_index']
        constraints = [
            models.UniqueConstraint(
                fields=['document', 'chunk_index'],
                name='unique_legal_document_chunk',
            ),
            models.CheckConstraint(
                condition=Q(text_hash__gt=''),
                name='legal_chunk_hash_not_empty',
            ),
        ]
        indexes = [
            models.Index(fields=['document', 'article_number']),
        ]

    def __str__(self):
        return f'{self.document_id}:{self.chunk_index}'
