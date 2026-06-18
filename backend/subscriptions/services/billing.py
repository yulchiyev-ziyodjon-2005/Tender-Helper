from dataclasses import dataclass
from datetime import datetime, time, timedelta

from django.db import transaction
from django.utils import timezone

from subscriptions.models import CompanySubscription, SubscriptionPlan
from subscriptions.services.notifications import (
    apply_sms_quota_defaults,
    sms_quota_for_plan,
)


@dataclass(frozen=True)
class EffectiveSubscription:
    subscription: CompanySubscription
    plan: SubscriptionPlan

    @property
    def period_start(self):
        return self.subscription.current_period_start

    @property
    def period_end(self):
        return self.subscription.current_period_end


def _calendar_month_period(at):
    local_at = timezone.localtime(at)
    month_start = datetime.combine(
        local_at.date().replace(day=1),
        time.min,
        tzinfo=local_at.tzinfo,
    )
    if local_at.month == 12:
        next_month = local_at.date().replace(
            year=local_at.year + 1,
            month=1,
            day=1,
        )
    else:
        next_month = local_at.date().replace(
            month=local_at.month + 1,
            day=1,
        )
    month_end = datetime.combine(
        next_month,
        time.min,
        tzinfo=local_at.tzinfo,
    )
    return month_start, month_end


def _is_effective(subscription, at):
    if subscription.current_period_end <= at:
        return False
    if subscription.status == CompanySubscription.Status.ACTIVE:
        return True
    return (
        subscription.status == CompanySubscription.Status.TRIALING
        and (
            subscription.trial_ends_at is None
            or subscription.trial_ends_at > at
        )
    )


def _sync_legacy_tariff(company, subscription):
    expires_at = (
        None
        if subscription.plan.code == 'free'
        else subscription.current_period_end
    )
    updates = {}
    if company.current_tariff != subscription.plan.code:
        updates['current_tariff'] = subscription.plan.code
    if company.tariff_expires_at != expires_at:
        updates['tariff_expires_at'] = expires_at
    if updates:
        type(company).objects.filter(pk=company.pk).update(**updates)
        for field, value in updates.items():
            setattr(company, field, value)


def peek_effective_subscription(company, *, at=None):
    at = at or timezone.now()
    subscription = (
        CompanySubscription.objects.select_related('plan', 'scheduled_plan')
        .filter(
            company=company,
            status__in=CompanySubscription.EFFECTIVE_CANDIDATE_STATUSES,
        )
        .order_by('-created_at')
        .first()
    )
    if subscription is None or not _is_effective(subscription, at):
        return None
    return EffectiveSubscription(
        subscription=subscription,
        plan=subscription.plan,
    )


@transaction.atomic
def get_effective_subscription(company, *, at=None):
    at = at or timezone.now()
    locked_company = type(company).objects.select_for_update().get(pk=company.pk)
    subscription = (
        CompanySubscription.objects.select_for_update()
        .select_related('plan')
        .filter(
            company=locked_company,
            status__in=CompanySubscription.EFFECTIVE_CANDIDATE_STATUSES,
        )
        .order_by('-created_at')
        .first()
    )

    if subscription is not None and _is_effective(subscription, at):
        _sync_legacy_tariff(locked_company, subscription)
        return EffectiveSubscription(
            subscription=subscription,
            plan=subscription.plan,
        )

    if subscription is not None:
        subscription.status = CompanySubscription.Status.EXPIRED
        subscription.ended_at = at
        subscription.save(update_fields=['status', 'ended_at', 'updated_at'])
    free_plan = SubscriptionPlan.objects.get(code='free', is_active=True)
    period_start, period_end = _calendar_month_period(at)
    free_sms_quota = sms_quota_for_plan(free_plan.code)
    free_subscription = CompanySubscription.objects.create(
        company=locked_company,
        plan=free_plan,
        status=CompanySubscription.Status.ACTIVE,
        source=CompanySubscription.Source.SYSTEM,
        starts_at=at,
        current_period_start=period_start,
        current_period_end=period_end,
        sms_allowed_monthly=free_sms_quota['sms_allowed_monthly'],
        daily_sms_cap=free_sms_quota['daily_sms_cap'],
        sms_counter_period_start=period_start.date(),
        metadata={'reason': 'free_fallback'},
    )
    _sync_legacy_tariff(locked_company, free_subscription)
    return EffectiveSubscription(
        subscription=free_subscription,
        plan=free_plan,
    )


@transaction.atomic
def activate_subscription(
    company,
    plan,
    *,
    period_start,
    period_end,
    source=CompanySubscription.Source.ADMIN,
    external_reference='',
    metadata=None,
):
    if not plan.is_active:
        raise ValueError('Cannot activate an inactive subscription plan.')
    if period_end <= period_start:
        raise ValueError('Subscription period end must be after its start.')

    locked_company = type(company).objects.select_for_update().get(pk=company.pk)
    now = timezone.now()
    existing = CompanySubscription.objects.select_for_update().filter(
        company=locked_company,
        status__in=CompanySubscription.REPLACEABLE_STATUSES,
    )
    existing.update(
        status=CompanySubscription.Status.CANCELED,
        canceled_at=now,
        ended_at=now,
        scheduled_plan=None,
        scheduled_change_at=None,
        scheduled_period_end=None,
        updated_at=now,
    )
    sms_quota = sms_quota_for_plan(plan.code)
    subscription = CompanySubscription.objects.create(
        company=locked_company,
        plan=plan,
        status=CompanySubscription.Status.ACTIVE,
        source=source,
        starts_at=period_start,
        current_period_start=period_start,
        current_period_end=period_end,
        external_reference=external_reference,
        sms_allowed_monthly=sms_quota['sms_allowed_monthly'],
        daily_sms_cap=sms_quota['daily_sms_cap'],
        sms_counter_period_start=period_start.date(),
        metadata=metadata or {},
    )
    _sync_legacy_tariff(locked_company, subscription)
    return subscription


@transaction.atomic
def pause_subscription(subscription):
    locked = CompanySubscription.objects.select_for_update().get(
        pk=subscription.pk,
    )
    if locked.status not in {
        CompanySubscription.Status.TRIALING,
        CompanySubscription.Status.ACTIVE,
        CompanySubscription.Status.PAST_DUE,
    }:
        raise ValueError('Only a live subscription can be paused.')
    locked.status = CompanySubscription.Status.PAUSED
    locked.scheduled_plan = None
    locked.scheduled_change_at = None
    locked.scheduled_period_end = None
    locked.save(update_fields=[
        'status',
        'scheduled_plan',
        'scheduled_change_at',
        'scheduled_period_end',
        'updated_at',
    ])
    return locked


@transaction.atomic
def cancel_subscription(subscription):
    locked = CompanySubscription.objects.select_for_update().get(
        pk=subscription.pk,
    )
    if locked.status in {
        CompanySubscription.Status.CANCELED,
        CompanySubscription.Status.EXPIRED,
    }:
        raise ValueError('Subscription is already inactive.')
    now = timezone.now()
    locked.status = CompanySubscription.Status.CANCELED
    locked.canceled_at = now
    locked.ended_at = now
    locked.scheduled_plan = None
    locked.scheduled_change_at = None
    locked.scheduled_period_end = None
    locked.save(update_fields=[
        'status',
        'canceled_at',
        'ended_at',
        'scheduled_plan',
        'scheduled_change_at',
        'scheduled_period_end',
        'updated_at',
    ])
    return locked


@transaction.atomic
def extend_subscription(subscription, period_end):
    locked = CompanySubscription.objects.select_for_update().get(
        pk=subscription.pk,
    )
    if locked.status == CompanySubscription.Status.CANCELED:
        raise ValueError('Canceled subscription cannot be extended.')
    if period_end <= locked.current_period_end:
        raise ValueError('New period end must extend the current period.')
    locked.current_period_end = period_end
    if locked.status == CompanySubscription.Status.EXPIRED:
        locked.status = CompanySubscription.Status.ACTIVE
        locked.ended_at = None
    apply_sms_quota_defaults(locked)
    locked.save(update_fields=[
        'current_period_end',
        'status',
        'ended_at',
        'sms_allowed_monthly',
        'daily_sms_cap',
        'sms_counter_period_start',
        'sms_sent_this_month',
        'updated_at',
    ])
    _sync_legacy_tariff(locked.company, locked)
    return locked


@transaction.atomic
def schedule_plan_change(
    subscription,
    plan,
    effective_at,
    *,
    period_end=None,
    require_period_end=False,
):
    locked = CompanySubscription.objects.select_for_update().get(
        pk=subscription.pk,
    )
    if locked.status not in CompanySubscription.EFFECTIVE_CANDIDATE_STATUSES:
        raise ValueError('Only an active subscription can be scheduled.')
    if effective_at <= timezone.now():
        raise ValueError('Scheduled change time must be in the future.')
    if require_period_end and effective_at < locked.current_period_end:
        raise ValueError(
            'Scheduled downgrade cannot precede the current period end.'
        )
    if period_end is not None and period_end <= effective_at:
        raise ValueError(
            'Scheduled period end must follow the effective time.'
        )
    locked.scheduled_plan = plan
    locked.scheduled_change_at = effective_at
    locked.scheduled_period_end = period_end
    locked.full_clean()
    locked.save(update_fields=[
        'scheduled_plan',
        'scheduled_change_at',
        'scheduled_period_end',
        'updated_at',
    ])
    return locked


@transaction.atomic
def apply_scheduled_plan_change(subscription_id, *, at=None):
    at = at or timezone.now()
    subscription = (
        CompanySubscription.objects.select_for_update(of=('self',))
        .select_related('company', 'scheduled_plan')
        .filter(pk=subscription_id)
        .first()
    )
    if (
        subscription is None
        or subscription.status
        not in CompanySubscription.EFFECTIVE_CANDIDATE_STATUSES
        or subscription.scheduled_plan_id is None
        or subscription.scheduled_change_at is None
        or subscription.scheduled_change_at > at
    ):
        return None

    duration = max(
        subscription.current_period_end - subscription.current_period_start,
        timedelta(days=1),
    )
    period_end = subscription.scheduled_period_end or (at + duration)
    if period_end <= at:
        metadata = dict(subscription.metadata)
        metadata['scheduled_change_skipped'] = {
            'reason': 'scheduled_period_end_elapsed',
            'at': at.isoformat(),
            'plan': subscription.scheduled_plan.code,
        }
        subscription.scheduled_plan = None
        subscription.scheduled_change_at = None
        subscription.scheduled_period_end = None
        subscription.metadata = metadata
        subscription.save(update_fields=[
            'scheduled_plan',
            'scheduled_change_at',
            'scheduled_period_end',
            'metadata',
            'updated_at',
        ])
        return None
    return activate_subscription(
        subscription.company,
        subscription.scheduled_plan,
        period_start=at,
        period_end=period_end,
        metadata={
            'reason': 'scheduled_admin_plan_change',
            'previous_subscription_id': str(subscription.id),
        },
    )
