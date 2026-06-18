from __future__ import annotations

import logging
from datetime import datetime, time, timedelta
from decimal import Decimal
from typing import Any

from celery import shared_task
from django.conf import settings
from django.db import transaction
from django.db.models import F, Q
from django.utils import timezone

from companies.models import CompanyProfile
from subscriptions.models import CompanySubscription, NotificationLog
from subscriptions.services.notifications import apply_sms_quota_defaults
from tenders.models import TenderDocument, TenderLot
from users.services.otp_service import send_sms_message

logger = logging.getLogger(__name__)

PRO_ALERT_START_HOUR = 8
PRO_ALERT_END_HOUR = 22
SMART_ALERT_PLAN_CODES = ('pro', 'business', 'enterprise')


@shared_task(ignore_result=True)
def match_tender_document_task(tender_document_id: str) -> int:
    tender = (
        TenderDocument.objects.select_related('tender_lot', 'source')
        .filter(pk=tender_document_id)
        .first()
    )
    if tender is None:
        logger.warning('TenderDocument not found for SMS matching: %s', tender_document_id)
        return 0

    scheduled = 0
    subscriptions = (
        CompanySubscription.objects.select_related('company', 'company__user', 'plan')
        .filter(
            status__in=CompanySubscription.EFFECTIVE_CANDIDATE_STATUSES,
            plan__code__in=SMART_ALERT_PLAN_CODES,
            current_period_end__gt=timezone.now(),
        )
        .order_by('company_id', '-created_at')
    )
    for subscription in subscriptions.iterator():
        if subscription.plan.code == 'pro':
            if not _pro_subscription_matches(subscription.company, tender):
                continue
            eta = _next_pro_dispatch_time()
            dispatch_matching_lot_sms_task.apply_async(
                args=[str(subscription.id), str(subscription.company.user_id), str(tender.id)],
                eta=eta,
            )
            scheduled += 1
            continue

        if _business_subscription_matches(subscription.company, tender):
            dispatch_matching_lot_sms_task.delay(
                str(subscription.id),
                str(subscription.company.user_id),
                str(tender.id),
            )
            scheduled += 1

    return scheduled


@shared_task(ignore_result=True)
def dispatch_matching_lot_sms_task(
    subscription_id: str,
    user_id: str,
    tender_document_id: str,
) -> str:
    tender = TenderDocument.objects.filter(pk=tender_document_id).first()
    if tender is None:
        return 'missing_tender'

    reservation = _reserve_matching_lot_sms(
        subscription_id=subscription_id,
        user_id=user_id,
        tender=tender,
    )
    if reservation['status'] == 'queued':
        notification_id = reservation['notification_id']
        transaction.on_commit(
            lambda: deliver_matching_lot_sms_task.delay(str(notification_id))
        )
    return reservation['status']


@shared_task(ignore_result=True)
def deliver_matching_lot_sms_task(notification_id: str) -> str:
    with transaction.atomic():
        notification = (
            NotificationLog.objects.select_for_update()
            .select_related('user')
            .filter(pk=notification_id)
            .first()
        )
        if notification is None:
            return 'missing_notification'
        if notification.status == NotificationLog.Status.DELIVERED:
            return 'already_delivered'
        if notification.status != NotificationLog.Status.PENDING:
            return 'not_pending'

        metadata = dict(notification.metadata)
        phone_number = metadata.get('phone_number', '')
        message = metadata.get('message', '')
        sender = metadata.get('sender', getattr(settings, 'ESKIZ_SMS_FROM', 'TenderHelper'))
        notification.status = NotificationLog.Status.SENDING
        notification.metadata = {
            **metadata,
            'delivery_started_at': timezone.now().isoformat(),
        }
        notification.save(update_fields=['status', 'metadata'])

    if not phone_number or not message:
        return _finalize_notification(
            notification_id,
            status=NotificationLog.Status.FAILED,
            metadata_update={'reason': 'missing_sms_payload'},
        )

    success, provider_message_id = send_sms_message(
        phone_number,
        message,
        sender=sender,
    )
    if not success:
        return _finalize_notification(
            notification_id,
            status=NotificationLog.Status.FAILED,
            metadata_update={'reason': 'provider_failure'},
        )

    return _finalize_notification(
        notification_id,
        status=NotificationLog.Status.DELIVERED,
        provider_message_id=provider_message_id,
    )


@transaction.atomic
def _reserve_matching_lot_sms(
    *,
    subscription_id: str,
    user_id: str,
    tender: TenderDocument,
) -> dict[str, Any]:
    subscription = (
        CompanySubscription.objects.select_for_update()
        .select_related('company', 'company__user', 'plan')
        .filter(pk=subscription_id)
        .first()
    )
    if subscription is None:
        return {'status': 'missing_subscription'}

    apply_sms_quota_defaults(subscription, persist=True)
    if not _subscription_can_send_sms(subscription):
        _log_notification(
            user_id=user_id,
            tender=tender,
            status=NotificationLog.Status.THROTTLED,
            metadata={'reason': 'monthly_sms_cap'},
        )
        return {'status': 'monthly_throttled'}

    if _daily_reserved_count(user_id=user_id) >= subscription.daily_sms_cap:
        _log_notification(
            user_id=user_id,
            tender=tender,
            status=NotificationLog.Status.THROTTLED,
            metadata={'reason': 'daily_sms_cap'},
        )
        return {'status': 'daily_throttled'}

    if not subscription.company.user.phone_number:
        _log_notification(
            user_id=user_id,
            tender=tender,
            status=NotificationLog.Status.FAILED,
            metadata={'reason': 'missing_phone_number'},
        )
        return {'status': 'failed'}

    subscription.sms_sent_this_month = F('sms_sent_this_month') + 1
    subscription.save(update_fields=['sms_sent_this_month', 'updated_at'])
    notification = _log_notification(
        user_id=user_id,
        tender=tender,
        status=NotificationLog.Status.PENDING,
        metadata={
            'phone_number': subscription.company.user.phone_number,
            'message': _build_alert_message(tender),
            'sender': getattr(settings, 'ESKIZ_SMS_FROM', 'TenderHelper'),
            'reserved_at': timezone.now().isoformat(),
            'subscription_id': str(subscription.id),
        },
    )
    return {
        'status': 'queued',
        'notification_id': notification.id,
    }


def _subscription_can_send_sms(subscription: CompanySubscription) -> bool:
    return (
        subscription.sms_allowed_monthly > 0
        and subscription.daily_sms_cap > 0
        and subscription.sms_sent_this_month < subscription.sms_allowed_monthly
    )


def _daily_reserved_count(*, user_id: str) -> int:
    now = timezone.localtime()
    day_start = datetime.combine(now.date(), time.min, tzinfo=now.tzinfo)
    return NotificationLog.objects.filter(
        user_id=user_id,
        status__in=[
            NotificationLog.Status.PENDING,
            NotificationLog.Status.SENDING,
            NotificationLog.Status.DELIVERED,
        ],
        sent_at__gte=day_start,
    ).count()


def _finalize_notification(
    notification_id: str,
    *,
    status: str,
    provider_message_id: str = '',
    metadata_update: dict[str, Any] | None = None,
) -> str:
    with transaction.atomic():
        notification = NotificationLog.objects.select_for_update().get(
            pk=notification_id,
        )
        metadata = dict(notification.metadata)
        metadata.update(metadata_update or {})
        metadata['delivery_completed_at'] = timezone.now().isoformat()
        notification.status = status
        notification.provider_message_id = provider_message_id
        notification.metadata = metadata
        notification.save(update_fields=[
            'status',
            'provider_message_id',
            'metadata',
        ])
    if status == NotificationLog.Status.DELIVERED:
        return 'delivered'
    return 'failed'


def _log_notification(
    *,
    user_id: str,
    tender: TenderDocument,
    status: str,
    provider_message_id: str = '',
    metadata: dict[str, Any] | None = None,
) -> NotificationLog:
    return NotificationLog.objects.create(
        user_id=user_id,
        tender=tender,
        status=status,
        provider_message_id=provider_message_id,
        metadata=metadata or {},
    )


def _pro_subscription_matches(
    company: CompanyProfile,
    tender: TenderDocument,
) -> bool:
    keywords = _extract_keywords(company.onboarding_answers)[:3]
    if not keywords:
        return False

    query = Q()
    for keyword in keywords:
        query |= Q(title__icontains=keyword)
        query |= Q(buyer_name__icontains=keyword)
        query |= Q(category__icontains=keyword)
        query |= Q(lot_number__icontains=keyword)

    if tender.tender_lot_id:
        return TenderLot.objects.filter(pk=tender.tender_lot_id).filter(query).exists()

    document_query = Q()
    for keyword in keywords:
        document_query |= Q(title__icontains=keyword)
        document_query |= Q(organization_name__icontains=keyword)
        document_query |= Q(category__icontains=keyword)
    return TenderDocument.objects.filter(pk=tender.pk).filter(document_query).exists()


def _business_subscription_matches(
    company: CompanyProfile,
    tender: TenderDocument,
) -> bool:
    industry_terms = _normalize_terms([
        company.industry,
        *_as_list(company.onboarding_answers.get('industries')),
        *_as_list(company.onboarding_answers.get('industry_classifications')),
    ])
    competitor_terms = _normalize_terms([
        *_as_list(company.onboarding_answers.get('competitor_tracking_targets')),
        *_as_list(company.onboarding_answers.get('competitors')),
    ])
    haystack = _document_haystack(tender)

    industry_match = not industry_terms or any(term in haystack for term in industry_terms)
    competitor_match = not competitor_terms or any(
        term in haystack for term in competitor_terms
    )
    return industry_match and competitor_match


def _extract_keywords(answers: dict[str, Any]) -> list[str]:
    return _normalize_terms([
        *_as_list(answers.get('keyword_alerts')),
        *_as_list(answers.get('notification_keywords')),
        *_as_list(answers.get('sms_keywords')),
        *_as_list(answers.get('keywords')),
    ])


def _normalize_terms(values: list[Any]) -> list[str]:
    terms: list[str] = []
    seen: set[str] = set()
    for value in values:
        term = str(value or '').strip().lower()
        if len(term) < 2 or term in seen:
            continue
        seen.add(term)
        terms.append(term)
    return terms


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list | tuple | set):
        return list(value)
    return [value]


def _document_haystack(tender: TenderDocument) -> str:
    parts = [
        tender.title,
        tender.organization_name,
        tender.category,
        tender.tender_id,
    ]
    if tender.tender_lot:
        parts.extend([
            tender.tender_lot.title,
            tender.tender_lot.buyer_name,
            tender.tender_lot.category,
            tender.tender_lot.lot_number,
        ])
    raw_values = tender.raw_payload.values() if isinstance(tender.raw_payload, dict) else []
    parts.extend(str(value) for value in raw_values if isinstance(value, str | int | Decimal))
    return ' '.join(str(part or '').lower() for part in parts)


def _next_pro_dispatch_time():
    now = timezone.localtime()
    if PRO_ALERT_START_HOUR <= now.hour < PRO_ALERT_END_HOUR:
        return None

    target_date = now.date()
    if now.hour >= PRO_ALERT_END_HOUR:
        target_date += timedelta(days=1)
    return datetime.combine(
        target_date,
        time(hour=PRO_ALERT_START_HOUR),
        tzinfo=now.tzinfo,
    )


def _build_alert_message(tender: TenderDocument) -> str:
    amount = f"{tender.total_amount:,.0f}".replace(',', ' ')
    return (
        f"TenderHelper: yangi mos lot - {tender.title[:80]}. "
        f"Summa: {amount} UZS. Muddat: {tender.deadline_at:%Y-%m-%d}."
    )
