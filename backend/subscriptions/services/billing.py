from dataclasses import dataclass
from datetime import datetime, time

from django.db import transaction
from django.utils import timezone

from subscriptions.models import CompanySubscription, SubscriptionPlan


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
        return EffectiveSubscription(subscription=subscription, plan=subscription.plan)

    if subscription is not None and subscription.current_period_end <= at:
        subscription.status = CompanySubscription.Status.EXPIRED
        subscription.ended_at = at
        subscription.save(update_fields=['status', 'ended_at', 'updated_at'])
    free_plan = SubscriptionPlan.objects.get(code='free', is_active=True)
    period_start, period_end = _calendar_month_period(at)
    free_subscription = CompanySubscription.objects.create(
        company=locked_company,
        plan=free_plan,
        status=CompanySubscription.Status.ACTIVE,
        source=CompanySubscription.Source.SYSTEM,
        starts_at=at,
        current_period_start=period_start,
        current_period_end=period_end,
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
        updated_at=now,
    )
    subscription = CompanySubscription.objects.create(
        company=locked_company,
        plan=plan,
        status=CompanySubscription.Status.ACTIVE,
        source=source,
        starts_at=period_start,
        current_period_start=period_start,
        current_period_end=period_end,
        external_reference=external_reference,
        metadata=metadata or {},
    )
    _sync_legacy_tariff(locked_company, subscription)
    return subscription
