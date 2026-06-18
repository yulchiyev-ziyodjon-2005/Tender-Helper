from dataclasses import dataclass

from django.db import models

from subscriptions.constants import CompanyRole
from subscriptions.exceptions import CompanyAccessDenied, CompanyPermissionDenied


@dataclass(frozen=True)
class CompanyMembership:
    company: object
    user: object
    role: str
    permissions: tuple[str, ...] = ()


def accessible_companies(user):
    from companies.models import CompanyProfile

    if user is None or not user.is_authenticated:
        return CompanyProfile.objects.none()
    return CompanyProfile.objects.filter(
        models.Q(user=user)
        | models.Q(memberships__user=user, memberships__is_active=True),
    ).distinct()


def resolve_company_membership(user, company):
    """
    Resolve company access behind one boundary.

    CompanyProfile.user remains the owner during the additive membership
    migration. Employee access resolves through CompanyMember.
    """
    if user is None or not user.is_authenticated or company is None:
        raise CompanyAccessDenied()
    if company.user_id == user.id:
        return CompanyMembership(
            company=company,
            user=user,
            role=CompanyRole.OWNER,
            permissions=(),
        )
    from teams.models import CompanyMember

    member = CompanyMember.objects.filter(
        company=company,
        user=user,
        is_active=True,
    ).first()
    if member is None:
        raise CompanyAccessDenied()
    return CompanyMembership(
        company=company,
        user=user,
        role=member.role,
        permissions=tuple(member.permissions),
    )


def require_company_permission(user, company, permission):
    membership = resolve_company_membership(user, company)
    if (
        membership.role == CompanyRole.OWNER
        or permission in membership.permissions
    ):
        return membership
    raise CompanyPermissionDenied(permission=permission)
