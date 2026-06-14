from dataclasses import dataclass

from subscriptions.constants import CompanyRole
from subscriptions.exceptions import CompanyAccessDenied


@dataclass(frozen=True)
class CompanyMembership:
    company: object
    user: object
    role: str


def resolve_company_membership(user, company):
    """
    Resolve company access behind one boundary.

    WP2 uses CompanyProfile.user as the owner relation. A future CompanyMember
    model can replace this implementation without changing entitlement callers.
    """
    if (
        user is None
        or not user.is_authenticated
        or company is None
        or company.user_id != user.id
    ):
        raise CompanyAccessDenied()
    return CompanyMembership(
        company=company,
        user=user,
        role=CompanyRole.OWNER,
    )
