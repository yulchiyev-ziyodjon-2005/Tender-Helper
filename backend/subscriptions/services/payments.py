import hashlib
import uuid
from dataclasses import dataclass
from datetime import timedelta
from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.db import IntegrityError, transaction
from django.utils import timezone

from subscriptions.models import (
    CompanySubscription,
    PaymentTransaction,
    SubscriptionPlan,
    WebhookEvent,
)
from subscriptions.services.billing import activate_subscription


CLICK_SUCCESS = 0
CLICK_SIGN_ERROR = -1
CLICK_AMOUNT_ERROR = -2
CLICK_ACTION_ERROR = -3
CLICK_ALREADY_PAID = -4
CLICK_TRANSACTION_NOT_FOUND = -6
CLICK_UPDATE_ERROR = -7
CLICK_CANCELLED = -9


@dataclass(frozen=True)
class CheckoutResult:
    transaction: PaymentTransaction
    payment: dict


def click_is_configured() -> bool:
    values = (settings.CLICK_SERVICE_ID, settings.CLICK_SECRET_KEY)
    return all(value and not str(value).startswith('<') for value in values)


def _decimal_amount(value) -> Decimal | None:
    try:
        return Decimal(str(value)).quantize(Decimal('0.01'))
    except (InvalidOperation, TypeError, ValueError):
        return None


def _transaction_amount(transaction: PaymentTransaction) -> Decimal:
    return Decimal(transaction.amount).quantize(Decimal('0.01'))


def _period_end_for(plan: SubscriptionPlan, start):
    days = (
        365
        if plan.billing_period == SubscriptionPlan.BillingPeriod.ANNUAL
        else 30
    )
    return start + timedelta(days=days)


def _click_response(payload, *, error, note, transaction=None):
    response = {
        'click_trans_id': payload.get('click_trans_id'),
        'merchant_trans_id': payload.get('merchant_trans_id'),
        'error': error,
        'error_note': note,
    }
    action = str(payload.get('action', ''))
    if action == '0':
        response['merchant_prepare_id'] = (
            transaction.id if transaction is not None else None
        )
    elif action == '1':
        response['merchant_confirm_id'] = (
            transaction.id if transaction is not None else None
        )
    return response


def _click_sign_payload(payload) -> str:
    action = str(payload.get('action', ''))
    parts = [
        str(payload.get('click_trans_id', '')),
        str(payload.get('service_id', '')),
        settings.CLICK_SECRET_KEY,
        str(payload.get('merchant_trans_id', '')),
    ]
    if action == '1':
        parts.append(str(payload.get('merchant_prepare_id', '')))
    parts.extend([
        str(payload.get('amount', '')),
        action,
        str(payload.get('sign_time', '')),
    ])
    return ''.join(parts)


def verify_click_signature(payload) -> bool:
    provided = str(payload.get('sign_string', '')).lower()
    expected = hashlib.md5(  # nosec B324 - CLICK callback contract uses MD5.
        _click_sign_payload(payload).encode('utf-8'),
    ).hexdigest()
    return provided == expected


def create_checkout_transaction(company, plan_code, *, provider):
    if provider != PaymentTransaction.Provider.CLICK:
        raise NotImplementedError('Only CLICK checkout is implemented.')
    if not click_is_configured():
        raise RuntimeError('CLICK provider is not configured.')

    plan = SubscriptionPlan.objects.get(
        code=plan_code,
        is_active=True,
        is_public=True,
    )
    amount = _decimal_amount(plan.price_uzs)
    if amount is None or amount <= 0:
        raise ValueError('Checkout is only available for paid plans.')

    transaction_obj = PaymentTransaction.objects.create(
        company=company,
        plan=plan,
        provider=provider,
        status=PaymentTransaction.Status.PENDING,
        merchant_trans_id=f'th-{uuid.uuid4().hex[:24]}',
        amount=amount,
        currency=plan.currency,
        billing_period=plan.billing_period,
        metadata={
            'service_id': settings.CLICK_SERVICE_ID,
            'plan_code': plan.code,
        },
    )
    payment = {
        'provider': provider,
        'service_id': settings.CLICK_SERVICE_ID,
        'merchant_trans_id': transaction_obj.merchant_trans_id,
        'amount': str(transaction_obj.amount),
        'currency': transaction_obj.currency,
        'status': 'pending_provider_payment',
    }
    return CheckoutResult(transaction=transaction_obj, payment=payment)


def process_click_callback(payload):
    action = str(payload.get('action', ''))
    provider_event_id = str(payload.get('click_trans_id', ''))
    event_type = 'prepare' if action == '0' else 'complete' if action == '1' else 'unknown'

    try:
        event, created = WebhookEvent.objects.get_or_create(
            provider=PaymentTransaction.Provider.CLICK,
            provider_event_id=provider_event_id,
            action=action,
            defaults={
                'event_type': event_type,
                'request_payload': dict(payload),
            },
        )
    except IntegrityError:
        event = WebhookEvent.objects.get(
            provider=PaymentTransaction.Provider.CLICK,
            provider_event_id=provider_event_id,
            action=action,
        )
        created = False

    if not created and event.response_payload:
        return event.response_payload

    with transaction.atomic():
        event = WebhookEvent.objects.select_for_update().get(pk=event.pk)
        if event.response_payload:
            return event.response_payload

        response, transaction_obj, status_value = _process_click_callback_locked(
            payload,
        )
        event.transaction = transaction_obj
        event.status = status_value
        event.response_payload = response
        if response['error'] != CLICK_SUCCESS:
            event.error_code = str(response['error'])
            event.error_message = response['error_note']
        event.processed_at = timezone.now()
        event.save(update_fields=[
            'transaction',
            'status',
            'response_payload',
            'error_code',
            'error_message',
            'processed_at',
        ])
        return response


def _process_click_callback_locked(payload):
    action = str(payload.get('action', ''))
    if action not in {'0', '1'}:
        return (
            _click_response(
                payload,
                error=CLICK_ACTION_ERROR,
                note='Action not found',
            ),
            None,
            WebhookEvent.Status.REJECTED,
        )

    if not click_is_configured() or str(payload.get('service_id')) != str(settings.CLICK_SERVICE_ID):
        return (
            _click_response(
                payload,
                error=CLICK_TRANSACTION_NOT_FOUND,
                note='Service is not configured',
            ),
            None,
            WebhookEvent.Status.REJECTED,
        )

    if not verify_click_signature(payload):
        return (
            _click_response(
                payload,
                error=CLICK_SIGN_ERROR,
                note='Sign check failed',
            ),
            None,
            WebhookEvent.Status.REJECTED,
        )

    transaction_obj = (
        PaymentTransaction.objects.select_for_update()
        .select_related('company', 'plan')
        .filter(
            provider=PaymentTransaction.Provider.CLICK,
            merchant_trans_id=str(payload.get('merchant_trans_id', '')),
        )
        .first()
    )
    if transaction_obj is None:
        return (
            _click_response(
                payload,
                error=CLICK_TRANSACTION_NOT_FOUND,
                note='Transaction not found',
            ),
            None,
            WebhookEvent.Status.REJECTED,
        )

    amount = _decimal_amount(payload.get('amount'))
    if amount != _transaction_amount(transaction_obj):
        return (
            _click_response(
                payload,
                error=CLICK_AMOUNT_ERROR,
                note='Incorrect amount',
                transaction=transaction_obj,
            ),
            transaction_obj,
            WebhookEvent.Status.REJECTED,
        )

    if action == '0':
        return _prepare_click_payment(payload, transaction_obj)
    return _complete_click_payment(payload, transaction_obj)


def _prepare_click_payment(payload, transaction_obj):
    if transaction_obj.status == PaymentTransaction.Status.SUCCEEDED:
        return (
            _click_response(
                payload,
                error=CLICK_ALREADY_PAID,
                note='Transaction already paid',
                transaction=transaction_obj,
            ),
            transaction_obj,
            WebhookEvent.Status.PROCESSED,
        )
    if transaction_obj.status in {
        PaymentTransaction.Status.CANCELED,
        PaymentTransaction.Status.FAILED,
        PaymentTransaction.Status.EXPIRED,
    }:
        return (
            _click_response(
                payload,
                error=CLICK_CANCELLED,
                note='Transaction is not payable',
                transaction=transaction_obj,
            ),
            transaction_obj,
            WebhookEvent.Status.REJECTED,
        )

    transaction_obj.status = PaymentTransaction.Status.PREPARED
    transaction_obj.provider_transaction_id = str(payload.get('click_trans_id', ''))
    transaction_obj.provider_payment_id = str(payload.get('click_paydoc_id', ''))
    transaction_obj.prepared_at = timezone.now()
    transaction_obj.save(update_fields=[
        'status',
        'provider_transaction_id',
        'provider_payment_id',
        'prepared_at',
        'updated_at',
    ])
    return (
        _click_response(
            payload,
            error=CLICK_SUCCESS,
            note='Success',
            transaction=transaction_obj,
        ),
        transaction_obj,
        WebhookEvent.Status.PROCESSED,
    )


def _complete_click_payment(payload, transaction_obj):
    if str(payload.get('merchant_prepare_id', '')) != str(transaction_obj.id):
        return (
            _click_response(
                payload,
                error=CLICK_TRANSACTION_NOT_FOUND,
                note='Prepare transaction not found',
                transaction=transaction_obj,
            ),
            transaction_obj,
            WebhookEvent.Status.REJECTED,
        )

    try:
        provider_error = int(payload.get('error') or 0)
    except (TypeError, ValueError):
        provider_error = CLICK_UPDATE_ERROR
    if provider_error < 0:
        transaction_obj.status = PaymentTransaction.Status.CANCELED
        transaction_obj.canceled_at = timezone.now()
        transaction_obj.error_code = str(provider_error)
        transaction_obj.error_message = str(payload.get('error_note', ''))
        transaction_obj.save(update_fields=[
            'status',
            'canceled_at',
            'error_code',
            'error_message',
            'updated_at',
        ])
        return (
            _click_response(
                payload,
                error=CLICK_CANCELLED,
                note='Transaction cancelled',
                transaction=transaction_obj,
            ),
            transaction_obj,
            WebhookEvent.Status.PROCESSED,
        )

    if transaction_obj.status == PaymentTransaction.Status.SUCCEEDED:
        return (
            _click_response(
                payload,
                error=CLICK_SUCCESS,
                note='Success',
                transaction=transaction_obj,
            ),
            transaction_obj,
            WebhookEvent.Status.PROCESSED,
        )

    if transaction_obj.status != PaymentTransaction.Status.PREPARED:
        return (
            _click_response(
                payload,
                error=CLICK_UPDATE_ERROR,
                note='Transaction is not prepared',
                transaction=transaction_obj,
            ),
            transaction_obj,
            WebhookEvent.Status.REJECTED,
        )

    now = timezone.now()
    subscription = activate_subscription(
        transaction_obj.company,
        transaction_obj.plan,
        period_start=now,
        period_end=_period_end_for(transaction_obj.plan, now),
        source=CompanySubscription.Source.PAYMENT,
        external_reference=str(payload.get('click_trans_id', '')),
        metadata={
            'provider': PaymentTransaction.Provider.CLICK,
            'payment_transaction_id': transaction_obj.id,
            'merchant_trans_id': transaction_obj.merchant_trans_id,
            'click_paydoc_id': str(payload.get('click_paydoc_id', '')),
        },
    )
    transaction_obj.status = PaymentTransaction.Status.SUCCEEDED
    transaction_obj.subscription = subscription
    transaction_obj.provider_transaction_id = str(payload.get('click_trans_id', ''))
    transaction_obj.provider_payment_id = str(payload.get('click_paydoc_id', ''))
    transaction_obj.paid_at = now
    transaction_obj.save(update_fields=[
        'status',
        'subscription',
        'provider_transaction_id',
        'provider_payment_id',
        'paid_at',
        'updated_at',
    ])
    return (
        _click_response(
            payload,
            error=CLICK_SUCCESS,
            note='Success',
            transaction=transaction_obj,
        ),
        transaction_obj,
        WebhookEvent.Status.PROCESSED,
    )
