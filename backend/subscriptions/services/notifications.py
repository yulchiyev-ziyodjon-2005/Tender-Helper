from __future__ import annotations

from datetime import date

from django.utils import timezone

from subscriptions.constants import SMS_QUOTA_MATRIX
from subscriptions.models import CompanySubscription


def sms_quota_for_plan(plan_code: str) -> dict[str, int]:
    return SMS_QUOTA_MATRIX.get(
        plan_code,
        SMS_QUOTA_MATRIX['free'],
    )


def current_sms_counter_period(at=None) -> date:
    local_date = timezone.localdate(at)
    return local_date.replace(day=1)


def apply_sms_quota_defaults(
    subscription: CompanySubscription,
    *,
    persist: bool = False,
    at=None,
) -> CompanySubscription:
    quota = sms_quota_for_plan(subscription.plan.code)
    period_start = current_sms_counter_period(at)
    updates: list[str] = []

    for field in ('sms_allowed_monthly', 'daily_sms_cap'):
        value = quota[field]
        if getattr(subscription, field) != value:
            setattr(subscription, field, value)
            updates.append(field)

    if subscription.sms_counter_period_start != period_start:
        subscription.sms_counter_period_start = period_start
        subscription.sms_sent_this_month = 0
        updates.extend(['sms_counter_period_start', 'sms_sent_this_month'])

    if persist and updates:
        updates.append('updated_at')
        subscription.save(update_fields=sorted(set(updates)))

    return subscription
