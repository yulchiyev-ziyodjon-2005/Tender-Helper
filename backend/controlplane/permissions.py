from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from rest_framework.permissions import BasePermission

from controlplane.exceptions import (
    AdminAccessDenied,
    AdminMFARequired,
    AdminStepUpRequired,
)


def get_admin_principal(user):
    if not user or not user.is_authenticated or not user.is_staff:
        raise AdminAccessDenied()
    try:
        principal = user.admin_principal
    except AttributeError as exc:
        raise AdminAccessDenied() from exc
    if not principal.is_active:
        raise AdminAccessDenied(
            code='admin_principal_inactive',
            message='Administrator access has been deactivated.',
        )
    return principal


def require_admin_capability(user, capability, *, step_up=False):
    principal = get_admin_principal(user)
    if not principal.has_capability(capability):
        raise AdminAccessDenied(
            code='admin_capability_denied',
            message='Required administrator capability is missing.',
        )
    now = timezone.now()
    mfa_cutoff = now - timedelta(seconds=settings.ADMIN_MFA_SESSION_SECONDS)
    if (
        principal.mfa_verified_at is None
        or principal.mfa_verified_at < mfa_cutoff
    ):
        raise AdminMFARequired()
    if step_up:
        step_up_cutoff = now - timedelta(seconds=settings.ADMIN_STEP_UP_SECONDS)
        if principal.step_up_at is None or principal.step_up_at < step_up_cutoff:
            raise AdminStepUpRequired()
    return principal


class AdminCapabilityPermission(BasePermission):
    def has_permission(self, request, view):
        require_admin_capability(
            request.user,
            view.required_capability,
            step_up=getattr(view, 'requires_step_up', False),
        )
        return True
