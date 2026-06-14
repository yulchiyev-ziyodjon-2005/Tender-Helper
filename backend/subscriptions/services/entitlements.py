from dataclasses import dataclass

from subscriptions.constants import FEATURE_POLICIES, Feature
from subscriptions.exceptions import (
    CompanyRoleDenied,
    FeatureNotAvailable,
    StirRequired,
)
from subscriptions.services.billing import get_effective_subscription
from subscriptions.services.membership import resolve_company_membership


@dataclass(frozen=True)
class Entitlement:
    feature: str
    allowed: bool
    plan: str
    role: str
    required_plan: str
    requires_stir: bool
    denial_code: str | None = None


def _evaluate_feature(membership, effective, feature):
    try:
        policy = FEATURE_POLICIES[feature]
    except KeyError as exc:
        raise ValueError(f'Unknown feature: {feature}') from exc

    if feature not in effective.plan.features:
        raise FeatureNotAvailable(
            feature=feature,
            required_plan=policy.required_plan,
            requires_stir=policy.requires_stir,
        )
    if membership.role not in policy.allowed_roles:
        raise CompanyRoleDenied(
            feature=feature,
            required_roles=policy.allowed_roles,
        )
    if policy.requires_stir and not membership.company.has_stir_identity:
        raise StirRequired(
            feature=feature,
            required_plan=policy.required_plan,
        )
    return Entitlement(
        feature=feature,
        allowed=True,
        plan=effective.plan.code,
        role=membership.role,
        required_plan=policy.required_plan,
        requires_stir=policy.requires_stir,
    )


def authorize_feature(user, company, feature):
    membership = resolve_company_membership(user, company)
    effective = get_effective_subscription(company)
    return _evaluate_feature(membership, effective, feature)


def list_entitlements(user, company):
    membership = resolve_company_membership(user, company)
    effective = get_effective_subscription(company)
    entitlements = []
    for feature in Feature.ALL:
        policy = FEATURE_POLICIES[feature]
        try:
            entitlement = _evaluate_feature(
                membership,
                effective,
                feature,
            )
        except (FeatureNotAvailable, CompanyRoleDenied, StirRequired) as exc:
            entitlements.append(Entitlement(
                feature=feature,
                allowed=False,
                plan=effective.plan.code,
                role=membership.role,
                required_plan=policy.required_plan,
                requires_stir=policy.requires_stir,
                denial_code=str(exc.detail['code']),
            ))
        else:
            entitlements.append(entitlement)
    return effective, entitlements
