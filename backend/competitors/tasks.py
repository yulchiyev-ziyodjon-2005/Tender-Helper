import logging
from datetime import date, timedelta

from celery import shared_task
from django.conf import settings
from django.utils import timezone

from competitors.models import CompetitorAnalytics
from competitors.services.aggregation import aggregate_competitors
from competitors.services.identity import normalize_category
from tenders.models import TenderLot

logger = logging.getLogger(__name__)


@shared_task(ignore_result=True)
def aggregate_category_competitors_task(category, period_start, period_end):
    snapshots = aggregate_competitors(
        scope_type=CompetitorAnalytics.Scope.CATEGORY,
        category=category,
        period_start=date.fromisoformat(period_start),
        period_end=date.fromisoformat(period_end),
    )
    return len(snapshots)


@shared_task(ignore_result=True)
def aggregate_lot_competitors_task(lot_id, period_start, period_end):
    lot = TenderLot.objects.get(pk=lot_id)
    snapshots = aggregate_competitors(
        scope_type=CompetitorAnalytics.Scope.LOT,
        category=lot.category,
        tender_lot=lot,
        period_start=date.fromisoformat(period_start),
        period_end=date.fromisoformat(period_end),
    )
    return len(snapshots)


@shared_task(ignore_result=True)
def refresh_competitor_analytics_task():
    period_end = timezone.localdate()
    categories = {
        normalize_category(value)
        for value in TenderLot.objects.filter(
            status=TenderLot.Status.COMPLETED,
        ).exclude(category='').values_list('category', flat=True)
    }
    target_lots = list(
        TenderLot.objects.filter(
            status=TenderLot.Status.ACTIVE,
        ).exclude(category='').only('id', 'category')
    )
    snapshot_count = 0
    for days in settings.COMPETITOR_PERIOD_DAYS:
        period_start = period_end - timedelta(days=days - 1)
        for category in sorted(categories):
            snapshot_count += len(aggregate_competitors(
                scope_type=CompetitorAnalytics.Scope.CATEGORY,
                category=category,
                period_start=period_start,
                period_end=period_end,
            ))
        for lot in target_lots:
            snapshot_count += len(aggregate_competitors(
                scope_type=CompetitorAnalytics.Scope.LOT,
                category=lot.category,
                tender_lot=lot,
                period_start=period_start,
                period_end=period_end,
            ))
    logger.info(
        'Competitor analytics refresh completed.',
        extra={
            'category_count': len(categories),
            'target_lot_count': len(target_lots),
            'period_count': len(settings.COMPETITOR_PERIOD_DAYS),
            'snapshot_count': snapshot_count,
        },
    )
    return snapshot_count
