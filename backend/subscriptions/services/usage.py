from django.db import IntegrityError, transaction
from django.db.models import F

from subscriptions.constants import METRIC_LIMIT_KEYS
from subscriptions.exceptions import UsageLimitExceeded
from subscriptions.models import UsageRecord
from subscriptions.services.billing import get_effective_subscription


def _usage_limit(plan, metric):
    limit_key = METRIC_LIMIT_KEYS.get(metric)
    if limit_key is None:
        raise ValueError(f'Unsupported usage metric: {metric}')
    value = plan.limits.get(limit_key)
    return None if value is None else int(value)


def _get_or_create_usage_record(effective, company, metric, limit):
    lookup = {
        'company': company,
        'metric': metric,
        'period_start': effective.period_start,
        'period_end': effective.period_end,
    }
    defaults = {
        'subscription': effective.subscription,
        'limit_snapshot': limit,
    }
    try:
        return UsageRecord.objects.get_or_create(**lookup, defaults=defaults)[0]
    except IntegrityError:
        return UsageRecord.objects.get(**lookup)


@transaction.atomic
def consume_usage(company, metric, *, amount=1):
    if amount <= 0:
        raise ValueError('Usage amount must be greater than zero.')

    effective = get_effective_subscription(company)
    limit = _usage_limit(effective.plan, metric)
    record = _get_or_create_usage_record(
        effective,
        company,
        metric,
        limit,
    )

    records = UsageRecord.objects.filter(pk=record.pk)
    if limit is None:
        records.update(used=F('used') + amount)
    else:
        updated = records.filter(used__lte=limit - amount).update(
            used=F('used') + amount,
        )
        if not updated:
            record.refresh_from_db(fields=['used'])
            raise UsageLimitExceeded(
                metric=metric,
                plan=effective.plan.code,
                limit=limit,
                used=record.used,
                period_end=effective.period_end,
            )

    record.refresh_from_db()
    return record
