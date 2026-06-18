import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q


class TenderParticipant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tender_lot = models.ForeignKey(
        'tenders.TenderLot',
        on_delete=models.CASCADE,
        related_name='participants',
    )
    source_name = models.CharField(max_length=500)
    normalized_name = models.CharField(max_length=500)
    stir = models.CharField(max_length=9, blank=True, default='')
    identity_key = models.CharField(max_length=550)
    source_reference = models.CharField(max_length=255, blank=True, default='')
    raw_data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tender_participants'
        ordering = ['tender_lot_id', 'normalized_name']
        constraints = [
            models.UniqueConstraint(
                fields=['tender_lot', 'identity_key'],
                name='unique_participant_identity_per_lot',
            ),
        ]
        indexes = [
            models.Index(fields=['stir']),
            models.Index(fields=['identity_key']),
        ]

    def __str__(self):
        return f'{self.tender_lot_id} / {self.normalized_name}'

    def clean(self):
        super().clean()
        if self.stir and (len(self.stir) != 9 or not self.stir.isdigit()):
            raise ValidationError({'stir': 'STIR must contain exactly 9 digits.'})

    def save(self, *args, **kwargs):
        from competitors.services.identity import (
            build_identity_key,
            normalize_competitor_name,
        )

        try:
            self.normalized_name = normalize_competitor_name(self.source_name)
            self.identity_key = build_identity_key(
                self.normalized_name,
                self.stir,
            )
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc
        self.full_clean()
        return super().save(*args, **kwargs)


class TenderBid(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    participant = models.ForeignKey(
        TenderParticipant,
        on_delete=models.CASCADE,
        related_name='bids',
    )
    sequence = models.PositiveIntegerField(default=1)
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    currency = models.CharField(max_length=3, default='UZS')
    submitted_at = models.DateTimeField(null=True, blank=True)
    is_valid = models.BooleanField(default=True)
    source_reference = models.CharField(max_length=255, blank=True, default='')
    raw_data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tender_bids'
        ordering = ['participant_id', 'sequence']
        constraints = [
            models.UniqueConstraint(
                fields=['participant', 'sequence'],
                name='unique_bid_sequence_per_participant',
            ),
            models.CheckConstraint(
                condition=Q(amount__gte=0),
                name='tender_bid_amount_non_negative',
            ),
            models.CheckConstraint(
                condition=Q(sequence__gt=0),
                name='tender_bid_sequence_positive',
            ),
        ]

    def __str__(self):
        return f'{self.participant_id} / {self.amount} {self.currency}'

    def save(self, *args, **kwargs):
        self.currency = self.currency.upper()
        self.full_clean()
        return super().save(*args, **kwargs)


class TenderAward(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tender_lot = models.OneToOneField(
        'tenders.TenderLot',
        on_delete=models.CASCADE,
        related_name='award',
    )
    winner = models.ForeignKey(
        TenderParticipant,
        on_delete=models.PROTECT,
        related_name='awards',
    )
    winning_bid = models.ForeignKey(
        TenderBid,
        on_delete=models.PROTECT,
        related_name='winning_awards',
        null=True,
        blank=True,
    )
    awarded_at = models.DateTimeField()
    is_verified = models.BooleanField(default=False)
    source_url = models.URLField(blank=True, default='')
    raw_data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tender_awards'
        indexes = [
            models.Index(fields=['is_verified', 'awarded_at']),
        ]

    def __str__(self):
        return f'{self.tender_lot_id} / {self.winner_id}'

    def clean(self):
        super().clean()
        errors = {}
        if self.winner_id and self.tender_lot_id:
            if self.winner.tender_lot_id != self.tender_lot_id:
                errors['winner'] = 'Winner must participate in the awarded lot.'
        if self.winning_bid_id and self.winner_id:
            if self.winning_bid.participant_id != self.winner_id:
                errors['winning_bid'] = 'Winning bid must belong to the winner.'
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class CompetitorDataQualityIssue(models.Model):
    class Severity(models.TextChoices):
        WARNING = 'warning', 'Warning'
        ERROR = 'error', 'Error'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tender_lot = models.ForeignKey(
        'tenders.TenderLot',
        on_delete=models.CASCADE,
        related_name='competitor_quality_issues',
    )
    code = models.CharField(max_length=80)
    severity = models.CharField(
        max_length=20,
        choices=Severity.choices,
        default=Severity.ERROR,
    )
    fingerprint = models.CharField(max_length=64, unique=True)
    details = models.JSONField(default=dict)
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'competitor_data_quality_issues'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['code', 'resolved_at']),
            models.Index(fields=['tender_lot', '-created_at']),
        ]

    def __str__(self):
        return f'{self.tender_lot_id} / {self.code}'


class CompetitorAnalytics(models.Model):
    class Scope(models.TextChoices):
        LOT = 'lot', 'Lot'
        CATEGORY = 'category', 'Category'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    scope_type = models.CharField(max_length=20, choices=Scope.choices)
    tender_lot = models.ForeignKey(
        'tenders.TenderLot',
        on_delete=models.CASCADE,
        related_name='competitor_analytics',
        null=True,
        blank=True,
    )
    category = models.CharField(max_length=255, blank=True, default='')
    identity_key = models.CharField(max_length=550)
    competitor_name = models.CharField(max_length=500)
    competitor_stir = models.CharField(max_length=9, blank=True, default='')
    period_start = models.DateField()
    period_end = models.DateField()
    rank = models.PositiveIntegerField()
    total_participations = models.PositiveIntegerField()
    total_wins = models.PositiveIntegerField()
    win_rate = models.DecimalField(max_digits=5, decimal_places=2)
    average_bid_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
    )
    average_discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
    )
    source_count = models.PositiveIntegerField()
    raw_metrics = models.JSONField(default=dict, blank=True)
    calculated_at = models.DateTimeField()

    class Meta:
        db_table = 'competitor_analytics'
        ordering = ['rank', 'identity_key']
        constraints = [
            models.UniqueConstraint(
                fields=[
                    'tender_lot',
                    'identity_key',
                    'period_start',
                    'period_end',
                ],
                condition=Q(scope_type='lot'),
                name='unique_lot_competitor_snapshot',
            ),
            models.UniqueConstraint(
                fields=[
                    'category',
                    'identity_key',
                    'period_start',
                    'period_end',
                ],
                condition=Q(scope_type='category'),
                name='unique_category_competitor_snapshot',
            ),
            models.CheckConstraint(
                condition=Q(period_end__gte=models.F('period_start')),
                name='competitor_period_valid',
            ),
            models.CheckConstraint(
                condition=Q(total_wins__lte=models.F('total_participations')),
                name='competitor_wins_not_above_participations',
            ),
            models.CheckConstraint(
                condition=Q(win_rate__gte=0) & Q(win_rate__lte=100),
                name='competitor_win_rate_range',
            ),
            models.CheckConstraint(
                condition=Q(rank__gt=0),
                name='competitor_rank_positive',
            ),
            models.CheckConstraint(
                condition=Q(source_count__gt=0),
                name='competitor_source_count_positive',
            ),
            models.CheckConstraint(
                condition=Q(average_bid_amount__gte=0),
                name='competitor_average_bid_non_negative',
            ),
            models.CheckConstraint(
                condition=(
                    Q(average_discount_percentage__gte=0)
                    & Q(average_discount_percentage__lte=100)
                ),
                name='competitor_discount_range',
            ),
            models.CheckConstraint(
                condition=(
                    Q(scope_type='lot', tender_lot__isnull=False)
                    | Q(
                        scope_type='category',
                        tender_lot__isnull=True,
                        category__gt='',
                    )
                ),
                name='competitor_scope_fields_valid',
            ),
        ]
        indexes = [
            models.Index(fields=['scope_type', 'tender_lot', 'rank']),
            models.Index(fields=['scope_type', 'category', 'rank']),
            models.Index(fields=['competitor_stir', '-calculated_at']),
            models.Index(fields=['-calculated_at']),
        ]

    def __str__(self):
        return f'{self.scope_type} / {self.competitor_name} / {self.rank}'

    def clean(self):
        super().clean()
        errors = {}
        if self.scope_type == self.Scope.LOT and not self.tender_lot_id:
            errors['tender_lot'] = 'Lot scope requires a tender lot.'
        if self.scope_type == self.Scope.CATEGORY:
            if self.tender_lot_id:
                errors['tender_lot'] = (
                    'Category scope cannot reference a tender lot.'
                )
            if not self.category.strip():
                errors['category'] = 'Category scope requires a category.'
        if self.period_end < self.period_start:
            errors['period_end'] = 'Period end cannot be before period start.'
        if self.total_wins > self.total_participations:
            errors['total_wins'] = 'Wins cannot exceed participations.'
        if errors:
            raise ValidationError(errors)


class CompetitorAnalyticsSource(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    analytics = models.ForeignKey(
        CompetitorAnalytics,
        on_delete=models.CASCADE,
        related_name='sources',
    )
    participant = models.ForeignKey(
        TenderParticipant,
        on_delete=models.PROTECT,
        related_name='analytics_sources',
    )
    bid = models.ForeignKey(
        TenderBid,
        on_delete=models.PROTECT,
        related_name='analytics_sources',
        null=True,
        blank=True,
    )
    award = models.ForeignKey(
        TenderAward,
        on_delete=models.PROTECT,
        related_name='analytics_sources',
    )
    was_winner = models.BooleanField(default=False)
    bid_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
    )
    discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'competitor_analytics_sources'
        constraints = [
            models.UniqueConstraint(
                fields=['analytics', 'participant'],
                name='unique_analytics_participant_source',
            ),
        ]
        indexes = [
            models.Index(fields=['analytics', 'was_winner']),
        ]

    def __str__(self):
        return f'{self.analytics_id} / {self.participant_id}'
