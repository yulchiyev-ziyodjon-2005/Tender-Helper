import hashlib
import json
import logging
from dataclasses import dataclass

from django.db import IntegrityError, transaction
from rest_framework.exceptions import APIException

from controlplane.exceptions import AdminConflict
from controlplane.models import AdminActionRequest, AdminAuditEvent

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class MutationOutcome:
    target_type: str
    target_id: str
    before: dict
    after: dict
    response_data: dict
    response_status: int = 200
    metadata: dict | None = None


@dataclass(frozen=True)
class ActionResult:
    data: dict
    status_code: int
    replayed: bool


def _request_hash(action, payload):
    canonical = json.dumps(
        {'action': action, 'payload': payload},
        sort_keys=True,
        separators=(',', ':'),
        default=str,
    )
    return hashlib.sha256(canonical.encode()).hexdigest()


def _json_safe(value):
    return json.loads(json.dumps(value, default=str))


def _request_context(request):
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR', '')
    ip_address = (
        forwarded.split(',')[0].strip()
        if forwarded
        else request.META.get('REMOTE_ADDR')
    )
    return request.headers.get('X-Request-ID', ''), ip_address


def _existing_result(record, request_hash):
    if record.request_hash != request_hash:
        raise AdminConflict(
            code='idempotency_key_reused',
            message='Idempotency key was used with a different request.',
        )
    if record.status == AdminActionRequest.Status.PROCESSING:
        raise AdminConflict(
            code='admin_action_in_progress',
            message='An action with this idempotency key is in progress.',
        )
    return ActionResult(
        data=record.response_data,
        status_code=record.response_status,
        replayed=True,
    )


def _create_action_request(*, actor, key, action, request_hash):
    try:
        with transaction.atomic():
            return AdminActionRequest.objects.create(
                actor=actor,
                idempotency_key=key,
                action=action,
                request_hash=request_hash,
            ), True
    except IntegrityError:
        return AdminActionRequest.objects.get(
            actor=actor,
            idempotency_key=key,
        ), False


def execute_admin_action(
    *,
    request,
    capability,
    action,
    reason,
    idempotency_key,
    payload,
    callback,
):
    request_hash = _request_hash(
        action,
        {'payload': payload, 'reason': reason},
    )
    record, created = _create_action_request(
        actor=request.user,
        key=idempotency_key,
        action=action,
        request_hash=request_hash,
    )
    if not created:
        return _existing_result(record, request_hash)

    request_id, ip_address = _request_context(request)
    try:
        with transaction.atomic():
            outcome = callback()
            safe_before = _json_safe(outcome.before)
            safe_after = _json_safe(outcome.after)
            safe_response = _json_safe(outcome.response_data)
            safe_metadata = _json_safe(outcome.metadata or {})
            AdminAuditEvent.objects.create(
                actor=request.user,
                capability=capability,
                action=action,
                target_type=outcome.target_type,
                target_id=outcome.target_id,
                reason=reason,
                before=safe_before,
                after=safe_after,
                outcome=AdminAuditEvent.Outcome.SUCCESS,
                request_id=request_id,
                ip_address=ip_address,
                metadata=safe_metadata,
            )
            record.status = AdminActionRequest.Status.SUCCEEDED
            record.response_data = safe_response
            record.response_status = outcome.response_status
            record.save(update_fields=[
                'status',
                'response_data',
                'response_status',
                'updated_at',
            ])
            logger.info(
                'Privileged admin action succeeded',
                extra={
                    'admin_action': action,
                    'admin_actor_id': str(request.user.id),
                    'admin_target_type': outcome.target_type,
                    'admin_target_id': outcome.target_id,
                    'request_id': request_id,
                },
            )
    except APIException as exc:
        detail = exc.detail if isinstance(exc.detail, dict) else {
            'code': 'admin_action_failed',
            'message': str(exc.detail),
            'details': {},
        }
        AdminAuditEvent.objects.create(
            actor=request.user,
            capability=capability,
            action=action,
            target_type=str(payload.get('target_type', 'unknown')),
            target_id=str(payload.get('target_id', '')),
            reason=reason,
            outcome=AdminAuditEvent.Outcome.FAILURE,
            request_id=request_id,
            ip_address=ip_address,
            metadata={'error': detail},
        )
        record.status = AdminActionRequest.Status.FAILED
        record.response_data = _json_safe(detail)
        record.response_status = exc.status_code
        record.save(update_fields=[
            'status',
            'response_data',
            'response_status',
            'updated_at',
        ])
        logger.warning(
            'Privileged admin action rejected',
            extra={
                'admin_action': action,
                'admin_actor_id': str(request.user.id),
                'request_id': request_id,
                'error_code': detail.get('code'),
            },
        )
        raise
    except Exception as exc:
        detail = {
            'code': 'admin_action_failed',
            'message': 'The privileged action failed.',
            'details': {},
        }
        AdminAuditEvent.objects.create(
            actor=request.user,
            capability=capability,
            action=action,
            target_type=str(payload.get('target_type', 'unknown')),
            target_id=str(payload.get('target_id', '')),
            reason=reason,
            outcome=AdminAuditEvent.Outcome.FAILURE,
            request_id=request_id,
            ip_address=ip_address,
            metadata={'error_type': type(exc).__name__},
        )
        record.status = AdminActionRequest.Status.FAILED
        record.response_data = detail
        record.response_status = 500
        record.save(update_fields=[
            'status',
            'response_data',
            'response_status',
            'updated_at',
        ])
        logger.exception(
            'Privileged admin action failed',
            extra={
                'admin_action': action,
                'admin_actor_id': str(request.user.id),
                'request_id': request_id,
            },
        )
        raise

    return ActionResult(
        data=safe_response,
        status_code=outcome.response_status,
        replayed=False,
    )
