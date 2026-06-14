import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q


class SubscriptionPlan(models.Model):
    """Versionable commercial plan and its entitlement configuration."""

    class BillingPeriod(models.TextChoices):
        MONTHLY = 'monthly', 'Monthly'
        ANNUAL = 'annual', 'Annual'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.SlugField(max_length=40, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, default='')
    rank = models.PositiveSmallIntegerField(default=0)
    features = models.JSONField(default=list, blank=True)
    limits = models.JSONField(default=dict, blank=True)
    price_uzs = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
    )
    currency = models.CharField(max_length=3, default='UZS')
    billing_period = models.CharField(
        max_length=20,
        choices=BillingPeriod.choices,
        default=BillingPeriod.MONTHLY,
    )
    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'subscription_plans'
        ordering = ['rank', 'code']
        indexes = [
            models.Index(fields=['is_active', 'is_public', 'rank']),
        ]

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()
        if not isinstance(self.features, list) or any(
            not isinstance(feature, str) for feature in self.features
        ):
            raise ValidationError({'features': 'Features must be a list of strings.'})
        if not isinstance(self.limits, dict):
            raise ValidationError({'limits': 'Limits must be a JSON object.'})


class CompanySubscription(models.Model):
    """A company's subscription lifecycle record."""

    class Status(models.TextChoices):
        TRIALING = 'trialing', 'Trialing'
        ACTIVE = 'active', 'Active'
        PAST_DUE = 'past_due', 'Past due'
        PAUSED = 'paused', 'Paused'
        CANCELED = 'canceled', 'Canceled'
        EXPIRED = 'expired', 'Expired'

    class Source(models.TextChoices):
        SYSTEM = 'system', 'System'
        PAYMENT = 'payment', 'Payment provider'
        ADMIN = 'admin', 'Admin override'

    EFFECTIVE_CANDIDATE_STATUSES = (
        Status.TRIALING,
        Status.ACTIVE,
    )
    REPLACEABLE_STATUSES = (
        Status.TRIALING,
        Status.ACTIVE,
        Status.PAST_DUE,
        Status.PAUSED,
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(
        'companies.CompanyProfile',
        on_delete=models.CASCADE,
        related_name='subscriptions',
    )
    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.PROTECT,
        related_name='company_subscriptions',
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    source = models.CharField(
        max_length=20,
        choices=Source.choices,
        default=Source.SYSTEM,
    )
    starts_at = models.DateTimeField()
    trial_ends_at = models.DateTimeField(null=True, blank=True)
    current_period_start = models.DateTimeField()
    current_period_end = models.DateTimeField()
    cancel_at_period_end = models.BooleanField(default=False)
    canceled_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    external_reference = models.CharField(max_length=255, blank=True, default='')
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'company_subscriptions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['company', 'status']),
            models.Index(fields=['status', 'current_period_end']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['company'],
                condition=Q(status__in=[
                    'trialing',
                    'active',
                ]),
                name='one_live_subscription_per_company',
            ),
            models.CheckConstraint(
                condition=Q(current_period_end__gt=models.F('current_period_start')),
                name='subscription_period_is_valid',
            ),
        ]

    def __str__(self):
        return f'{self.company} / {self.plan.code} / {self.status}'

    def clean(self):
        super().clean()
        if self.current_period_end <= self.current_period_start:
            raise ValidationError({
                'current_period_end': 'Period end must be after period start.',
            })
        if self.trial_ends_at and self.trial_ends_at < self.starts_at:
            raise ValidationError({
                'trial_ends_at': 'Trial end cannot be before subscription start.',
            })


class UsageRecord(models.Model):
    """Atomic aggregate for a metered action within one billing period."""

    class Metric(models.TextChoices):
        AI_ANALYSIS = 'ai_analysis', 'AI analysis'
        DOCUMENT_GENERATION = 'document_generation', 'Document generation'
        DOCUMENT_EXPORT = 'document_export', 'Document export'
        COMPETITOR_QUERY = 'competitor_query', 'Competitor query'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(
        'companies.CompanyProfile',
        on_delete=models.CASCADE,
        related_name='usage_records',
    )
    subscription = models.ForeignKey(
        CompanySubscription,
        on_delete=models.SET_NULL,
        related_name='usage_records',
        null=True,
        blank=True,
    )
    metric = models.CharField(max_length=50, choices=Metric.choices)
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    used = models.PositiveBigIntegerField(default=0)
    limit_snapshot = models.PositiveBigIntegerField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'usage_records'
        ordering = ['-period_start', 'metric']
        constraints = [
            models.UniqueConstraint(
                fields=['company', 'metric', 'period_start', 'period_end'],
                name='unique_company_metric_period',
            ),
            models.CheckConstraint(
                condition=Q(period_end__gt=models.F('period_start')),
                name='usage_period_is_valid',
            ),
        ]
        indexes = [
            models.Index(fields=['company', 'metric', 'period_end']),
        ]

    def __str__(self):
        return f'{self.company} / {self.metric} / {self.used}'
