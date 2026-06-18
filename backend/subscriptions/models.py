import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from subscriptions.constants import Feature


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
        constraints = [
            models.CheckConstraint(
                condition=Q(price_uzs__isnull=True) | Q(price_uzs__gte=0),
                name='subscription_plan_price_non_negative',
            ),
        ]

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()
        errors = {}
        if not isinstance(self.features, list) or any(
            not isinstance(feature, str) for feature in self.features
        ):
            errors['features'] = 'Features must be a list of strings.'
        else:
            unknown_features = set(self.features) - set(Feature.ALL)
            if unknown_features:
                errors['features'] = (
                    'Unknown feature keys: '
                    + ', '.join(sorted(unknown_features))
                )
            elif len(self.features) != len(set(self.features)):
                errors['features'] = 'Feature keys must be unique.'

        if not isinstance(self.limits, dict):
            errors['limits'] = 'Limits must be a JSON object.'
        else:
            invalid_limits = {
                key: value
                for key, value in self.limits.items()
                if (
                    not isinstance(key, str)
                    or isinstance(value, bool)
                    or (
                        value is not None
                        and (not isinstance(value, int) or value < 0)
                    )
                )
            }
            if invalid_limits:
                errors['limits'] = (
                    'Limit values must be non-negative integers or null.'
                )
        if self.price_uzs is not None and self.price_uzs < 0:
            errors['price_uzs'] = 'Price cannot be negative.'

        if errors:
            raise ValidationError(errors)


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
    scheduled_plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.PROTECT,
        related_name='scheduled_company_subscriptions',
        null=True,
        blank=True,
    )
    scheduled_change_at = models.DateTimeField(null=True, blank=True)
    scheduled_period_end = models.DateTimeField(null=True, blank=True)
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
    sms_allowed_monthly = models.PositiveIntegerField(default=0)
    sms_sent_this_month = models.PositiveIntegerField(default=0)
    daily_sms_cap = models.PositiveIntegerField(default=0)
    sms_counter_period_start = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'company_subscriptions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['company', 'status']),
            models.Index(fields=['status', 'current_period_end']),
            models.Index(fields=['status', 'scheduled_change_at']),
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
            models.CheckConstraint(
                condition=(
                    Q(trial_ends_at__isnull=True)
                    | Q(trial_ends_at__gte=models.F('starts_at'))
                ),
                name='subscription_trial_period_is_valid',
            ),
            models.CheckConstraint(
                condition=(
                    Q(
                        scheduled_plan__isnull=True,
                        scheduled_change_at__isnull=True,
                    )
                    | Q(
                        scheduled_plan__isnull=False,
                        scheduled_change_at__isnull=False,
                    )
                ),
                name='subscription_schedule_pair_complete',
            ),
            models.CheckConstraint(
                condition=(
                    Q(scheduled_period_end__isnull=True)
                    | Q(
                        scheduled_plan__isnull=False,
                        scheduled_change_at__isnull=False,
                        scheduled_period_end__gt=models.F(
                            'scheduled_change_at'
                        ),
                    )
                ),
                name='subscription_scheduled_period_is_valid',
            ),
            models.CheckConstraint(
                condition=Q(sms_sent_this_month__lte=models.F('sms_allowed_monthly')),
                name='subscription_sms_monthly_counter_within_cap',
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
        if bool(self.scheduled_plan_id) != bool(self.scheduled_change_at):
            raise ValidationError({
                'scheduled_plan': (
                    'Scheduled plan and change time must be set together.'
                ),
            })
        if self.scheduled_period_end and not self.scheduled_plan_id:
            raise ValidationError({
                'scheduled_period_end': (
                    'Scheduled period end requires a scheduled plan.'
                ),
            })
        if (
            self.scheduled_period_end
            and self.scheduled_change_at
            and self.scheduled_period_end <= self.scheduled_change_at
        ):
            raise ValidationError({
                'scheduled_period_end': (
                    'Scheduled period end must follow the change time.'
                ),
            })
        if self.sms_sent_this_month > self.sms_allowed_monthly:
            raise ValidationError({
                'sms_sent_this_month': 'Monthly SMS usage cannot exceed allowance.',
            })


class NotificationLog(models.Model):
    """SMS notification dispatch audit and throttle ledger."""

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        SENDING = 'sending', 'Sending'
        DELIVERED = 'delivered', 'Delivered'
        THROTTLED = 'throttled', 'Throttled'
        FAILED = 'failed', 'Failed'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        'users.CustomUser',
        on_delete=models.CASCADE,
        related_name='notification_logs',
    )
    team = models.ForeignKey(
        'teams.CompanyMember',
        on_delete=models.SET_NULL,
        related_name='notification_logs',
        null=True,
        blank=True,
    )
    tender = models.ForeignKey(
        'tenders.TenderDocument',
        on_delete=models.CASCADE,
        related_name='notification_logs',
    )
    sent_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
    )
    provider_message_id = models.CharField(max_length=255, blank=True, default='')
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'notification_logs'
        ordering = ['-sent_at']
        indexes = [
            models.Index(fields=['user', 'sent_at']),
            models.Index(fields=['team', 'sent_at']),
            models.Index(fields=['tender', 'status']),
            models.Index(fields=['status', 'sent_at']),
        ]

    def __str__(self):
        return f'{self.user_id}:{self.tender_id}:{self.status}'


class PaymentTransaction(models.Model):
    """Provider-backed payment intent and confirmation ledger."""

    class Provider(models.TextChoices):
        CLICK = 'click', 'CLICK'
        PAYME = 'payme', 'Payme'
        UZUM = 'uzum', 'Uzum'

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PREPARED = 'prepared', 'Prepared'
        SUCCEEDED = 'succeeded', 'Succeeded'
        CANCELED = 'canceled', 'Canceled'
        FAILED = 'failed', 'Failed'
        EXPIRED = 'expired', 'Expired'

    id = models.BigAutoField(primary_key=True)
    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    company = models.ForeignKey(
        'companies.CompanyProfile',
        on_delete=models.PROTECT,
        related_name='payment_transactions',
    )
    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.PROTECT,
        related_name='payment_transactions',
    )
    subscription = models.ForeignKey(
        CompanySubscription,
        on_delete=models.SET_NULL,
        related_name='payment_transactions',
        null=True,
        blank=True,
    )
    provider = models.CharField(max_length=20, choices=Provider.choices)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    merchant_trans_id = models.CharField(max_length=64, unique=True)
    provider_transaction_id = models.CharField(
        max_length=128,
        blank=True,
        default='',
        db_index=True,
    )
    provider_payment_id = models.CharField(max_length=128, blank=True, default='')
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    currency = models.CharField(max_length=3, default='UZS')
    billing_period = models.CharField(
        max_length=20,
        choices=SubscriptionPlan.BillingPeriod.choices,
    )
    prepared_at = models.DateTimeField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    canceled_at = models.DateTimeField(null=True, blank=True)
    error_code = models.CharField(max_length=64, blank=True, default='')
    error_message = models.TextField(blank=True, default='')
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payment_transactions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['company', 'status', 'created_at']),
            models.Index(fields=['provider', 'status', 'created_at']),
            models.Index(fields=['provider', 'provider_transaction_id']),
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(amount__gt=0),
                name='payment_transaction_amount_positive',
            ),
        ]

    def __str__(self):
        return f'{self.provider}:{self.merchant_trans_id}:{self.status}'


class WebhookEvent(models.Model):
    """Immutable provider callback log with idempotent response snapshots."""

    class Status(models.TextChoices):
        RECEIVED = 'received', 'Received'
        PROCESSED = 'processed', 'Processed'
        REJECTED = 'rejected', 'Rejected'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    provider = models.CharField(
        max_length=20,
        choices=PaymentTransaction.Provider.choices,
    )
    event_type = models.CharField(max_length=50)
    provider_event_id = models.CharField(max_length=128)
    action = models.CharField(max_length=20, blank=True, default='')
    transaction = models.ForeignKey(
        PaymentTransaction,
        on_delete=models.SET_NULL,
        related_name='webhook_events',
        null=True,
        blank=True,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.RECEIVED,
    )
    request_payload = models.JSONField(default=dict, blank=True)
    response_payload = models.JSONField(default=dict, blank=True)
    error_code = models.CharField(max_length=64, blank=True, default='')
    error_message = models.TextField(blank=True, default='')
    received_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'webhook_events'
        ordering = ['-received_at']
        constraints = [
            models.UniqueConstraint(
                fields=['provider', 'provider_event_id', 'action'],
                name='unique_provider_webhook_action',
            ),
        ]
        indexes = [
            models.Index(fields=['provider', 'event_type', 'received_at']),
            models.Index(fields=['status', 'received_at']),
        ]

    def __str__(self):
        return f'{self.provider}:{self.provider_event_id}:{self.action}'


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
