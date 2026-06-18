import hashlib
import json
from collections import defaultdict
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

from django.db import transaction
from django.db.models import Prefetch
from django.utils import timezone

from competitors.models import (
    CompetitorAnalytics,
    CompetitorAnalyticsSource,
    CompetitorDataQualityIssue,
    TenderAward,
    TenderBid,
)
from competitors.services.identity import normalize_category
from tenders.models import TenderLot

PERCENT_QUANTUM = Decimal('0.01')
AMOUNT_QUANTUM = Decimal('0.01')
RANKING_FORMULA_VERSION = 'v1'


@dataclass(frozen=True)
class SourceMetric:
    participant: object
    bid: object | None
    award: object
    was_winner: bool
    bid_amount: Decimal | None
    discount_percentage: Decimal | None


def _round_percent(value):
    return value.quantize(PERCENT_QUANTUM, rounding=ROUND_HALF_UP)


def _round_amount(value):
    return value.quantize(AMOUNT_QUANTUM, rounding=ROUND_HALF_UP)


def _quality_fingerprint(award, code, details):
    canonical = json.dumps(details, sort_keys=True, default=str)
    return hashlib.sha256(
        f'{award.tender_lot_id}:{code}:{canonical}'.encode(),
    ).hexdigest()


def _record_quality_issue(award, code, details):
    fingerprint = _quality_fingerprint(award, code, details)
    CompetitorDataQualityIssue.objects.update_or_create(
        fingerprint=fingerprint,
        defaults={
            'tender_lot': award.tender_lot,
            'code': code,
            'severity': CompetitorDataQualityIssue.Severity.ERROR,
            'details': details,
            'resolved_at': None,
        },
    )
    return fingerprint


def _validated_awards(*, category, period_start, period_end, exclude_lot=None):
    analytics_bids = TenderBid.objects.filter(
        is_valid=True,
        currency='UZS',
    ).order_by('-sequence', '-created_at')
    awards = (
        TenderAward.objects.filter(
            is_verified=True,
            tender_lot__status=TenderLot.Status.COMPLETED,
            tender_lot__category__iexact=category,
            awarded_at__date__gte=period_start,
            awarded_at__date__lte=period_end,
        )
        .select_related('tender_lot', 'winner', 'winning_bid')
        .prefetch_related(
            Prefetch(
                'tender_lot__participants__bids',
                queryset=analytics_bids,
                to_attr='analytics_bids',
            ),
        )
        .order_by('awarded_at', 'tender_lot_id')
    )
    if exclude_lot is not None:
        awards = awards.exclude(tender_lot=exclude_lot)

    valid = []
    evaluated_lot_ids = set()
    active_issue_fingerprints = set()
    for award in awards:
        evaluated_lot_ids.add(award.tender_lot_id)
        start_price = award.tender_lot.start_price
        winning_bid = award.winning_bid
        if start_price <= 0:
            active_issue_fingerprints.add(_record_quality_issue(
                award,
                'invalid_start_price',
                {'start_price': str(start_price)},
            ))
            continue
        if winning_bid is None or not winning_bid.is_valid:
            active_issue_fingerprints.add(_record_quality_issue(
                award,
                'missing_winning_bid',
                {},
            ))
            continue
        if winning_bid.currency != 'UZS':
            active_issue_fingerprints.add(_record_quality_issue(
                award,
                'unsupported_currency',
                {'currency': winning_bid.currency},
            ))
            continue
        discount = (
            (start_price - winning_bid.amount) / start_price
        ) * Decimal('100')
        if discount < 0 or discount > 100:
            active_issue_fingerprints.add(_record_quality_issue(
                award,
                'invalid_winning_discount',
                {
                    'start_price': str(start_price),
                    'winning_bid': str(winning_bid.amount),
                    'discount': str(discount),
                },
            ))
            continue
        valid.append((award, _round_percent(discount)))

    issues = CompetitorDataQualityIssue.objects.filter(
        tender_lot_id__in=evaluated_lot_ids,
        resolved_at__isnull=True,
    )
    if active_issue_fingerprints:
        issues = issues.exclude(fingerprint__in=active_issue_fingerprints)
    issues.update(resolved_at=timezone.now())
    return valid


def _build_metrics(valid_awards):
    grouped = defaultdict(list)
    for award, winning_discount in valid_awards:
        for participant in award.tender_lot.participants.all():
            bid = (
                participant.analytics_bids[0]
                if participant.analytics_bids
                else None
            )
            was_winner = participant.id == award.winner_id
            grouped[participant.identity_key].append(SourceMetric(
                participant=participant,
                bid=bid,
                award=award,
                was_winner=was_winner,
                bid_amount=bid.amount if bid else None,
                discount_percentage=winning_discount if was_winner else None,
            ))

    metrics = []
    for identity_key, sources in grouped.items():
        participations = len(sources)
        wins = sum(1 for source in sources if source.was_winner)
        bid_amounts = [
            source.bid_amount
            for source in sources
            if source.bid_amount is not None
        ]
        discounts = [
            source.discount_percentage
            for source in sources
            if source.discount_percentage is not None
        ]
        win_rate = _round_percent(
            Decimal(wins) / Decimal(participations) * Decimal('100')
        )
        average_bid = (
            _round_amount(sum(bid_amounts) / len(bid_amounts))
            if bid_amounts
            else Decimal('0.00')
        )
        average_discount = (
            _round_percent(sum(discounts) / len(discounts))
            if discounts
            else Decimal('0.00')
        )
        representative = sorted(
            sources,
            key=lambda item: (
                item.award.awarded_at,
                str(item.participant.id),
            ),
            reverse=True,
        )[0].participant
        metrics.append({
            'identity_key': identity_key,
            'competitor_name': representative.normalized_name,
            'competitor_stir': representative.stir,
            'total_participations': participations,
            'total_wins': wins,
            'win_rate': win_rate,
            'average_bid_amount': average_bid,
            'average_discount_percentage': average_discount,
            'source_count': participations,
            'raw_metrics': {
                'ranking_formula_version': RANKING_FORMULA_VERSION,
                'bid_source_count': len(bid_amounts),
                'winning_source_count': len(discounts),
            },
            'sources': sources,
        })

    metrics.sort(
        key=lambda item: (
            -item['total_wins'],
            -item['win_rate'],
            -item['total_participations'],
            -item['average_discount_percentage'],
            item['identity_key'],
        ),
    )
    for rank, metric in enumerate(metrics, start=1):
        metric['rank'] = rank
    return metrics


@transaction.atomic
def aggregate_competitors(
    *,
    scope_type,
    category,
    period_start,
    period_end,
    tender_lot=None,
):
    if period_end < period_start:
        raise ValueError('period_end cannot be before period_start.')
    if scope_type not in CompetitorAnalytics.Scope.values:
        raise ValueError(f'Unsupported competitor scope: {scope_type}')
    category = normalize_category(category)
    if scope_type == CompetitorAnalytics.Scope.LOT:
        if tender_lot is None:
            raise ValueError('Lot scope requires tender_lot.')
        lot_category = normalize_category(tender_lot.category)
        if lot_category != category:
            raise ValueError('Tender lot category does not match category.')
    elif tender_lot is not None:
        raise ValueError('Category scope cannot reference tender_lot.')

    valid_awards = _validated_awards(
        category=category,
        period_start=period_start,
        period_end=period_end,
        exclude_lot=(
            tender_lot
            if scope_type == CompetitorAnalytics.Scope.LOT
            else None
        ),
    )
    metrics = _build_metrics(valid_awards)
    calculated_at = timezone.now()
    scope_filter = {
        'scope_type': scope_type,
        'period_start': period_start,
        'period_end': period_end,
    }
    if scope_type == CompetitorAnalytics.Scope.LOT:
        scope_filter['tender_lot'] = tender_lot
    else:
        scope_filter['category'] = category

    active_keys = set()
    snapshots = []
    for metric in metrics:
        active_keys.add(metric['identity_key'])
        lookup = {
            **scope_filter,
            'identity_key': metric['identity_key'],
        }
        snapshot, _ = CompetitorAnalytics.objects.update_or_create(
            **lookup,
            defaults={
                'tender_lot': (
                    tender_lot
                    if scope_type == CompetitorAnalytics.Scope.LOT
                    else None
                ),
                'category': category,
                'competitor_name': metric['competitor_name'],
                'competitor_stir': metric['competitor_stir'],
                'rank': metric['rank'],
                'total_participations': metric['total_participations'],
                'total_wins': metric['total_wins'],
                'win_rate': metric['win_rate'],
                'average_bid_amount': metric['average_bid_amount'],
                'average_discount_percentage': (
                    metric['average_discount_percentage']
                ),
                'source_count': metric['source_count'],
                'raw_metrics': metric['raw_metrics'],
                'calculated_at': calculated_at,
            },
        )
        snapshot.sources.all().delete()
        CompetitorAnalyticsSource.objects.bulk_create([
            CompetitorAnalyticsSource(
                analytics=snapshot,
                participant=source.participant,
                bid=source.bid,
                award=source.award,
                was_winner=source.was_winner,
                bid_amount=source.bid_amount,
                discount_percentage=source.discount_percentage,
            )
            for source in metric['sources']
        ])
        snapshots.append(snapshot)

    stale = CompetitorAnalytics.objects.filter(**scope_filter)
    if active_keys:
        stale = stale.exclude(identity_key__in=active_keys)
    stale.delete()
    return snapshots
