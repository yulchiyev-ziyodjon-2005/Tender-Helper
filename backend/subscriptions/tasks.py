import logging

from celery import shared_task
from django.utils import timezone

from subscriptions.models import CompanySubscription
from subscriptions.services.billing import apply_scheduled_plan_change
from subscriptions.services.notifications import (
    apply_sms_quota_defaults,
    current_sms_counter_period,
)

logger = logging.getLogger(__name__)


@shared_task(ignore_result=True)
def apply_scheduled_subscription_changes_task():
    now = timezone.now()
    due_ids = CompanySubscription.objects.filter(
        status__in=CompanySubscription.EFFECTIVE_CANDIDATE_STATUSES,
        scheduled_plan__isnull=False,
        scheduled_change_at__lte=now,
    ).values_list('id', flat=True)
    applied = 0
    for subscription_id in due_ids.iterator():
        try:
            changed = apply_scheduled_plan_change(subscription_id, at=now)
        except ValueError:
            logger.exception(
                'Scheduled subscription change rejected subscription=%s',
                subscription_id,
            )
        else:
            if changed is not None:
                applied += 1
    return applied


@shared_task(ignore_result=True)
def reset_monthly_sms_counters_task():
    period_start = current_sms_counter_period()
    subscriptions = CompanySubscription.objects.select_related('plan').exclude(
        sms_counter_period_start=period_start,
    )
    reset_count = 0
    for subscription in subscriptions.iterator():
        apply_sms_quota_defaults(subscription, persist=True)
        reset_count += 1
    logger.info('Monthly SMS counters reset for %s subscriptions', reset_count)
    return reset_count
