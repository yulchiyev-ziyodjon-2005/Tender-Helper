from subscriptions.constants import Feature, METRIC_LIMIT_KEYS
from subscriptions.models import UsageRecord
from subscriptions.serializers import EntitlementSerializer
from subscriptions.services.entitlements import list_entitlements
from subscriptions.services.membership import (
    accessible_companies,
    resolve_company_membership,
)
from teams.models import TeamPermission
from users.serializers import UserProfileSerializer


NAVIGATION_ITEMS = (
    {
        'key': 'dashboard',
        'label': 'Dashboard',
        'path': '/dashboard',
        'permissions': (),
        'features': (),
    },
    {
        'key': 'tenders',
        'label': 'Tenderlar',
        'path': '/dashboard/tenders',
        'permissions': (TeamPermission.VIEW_LOTS,),
        'features': (),
    },
    {
        'key': 'analysis',
        'label': 'AI tahlil',
        'path': '/dashboard/analysis',
        'permissions': (
            TeamPermission.RUN_AI_ANALYSIS,
            TeamPermission.USE_ANALYSIS_QUOTAS,
        ),
        'features': (),
    },
    {
        'key': 'documents',
        'label': 'Hujjatlar',
        'path': '/dashboard/documents',
        'permissions': (TeamPermission.GENERATE_DOCUMENTS,),
        'features': (Feature.DOCUMENT_GENERATION,),
    },
    {
        'key': 'competitors',
        'label': 'Raqobatchilar',
        'path': '/dashboard/competitors',
        'permissions': (TeamPermission.VIEW_COMPETITORS,),
        'features': (Feature.COMPETITOR_INTELLIGENCE,),
    },
    {
        'key': 'team',
        'label': 'Jamoa',
        'path': '/dashboard/team',
        'permissions': (TeamPermission.MANAGE_TEAM,),
        'features': (Feature.TEAM_COLLABORATION,),
    },
    {
        'key': 'billing',
        'label': "To'lovlar",
        'path': '/dashboard/billing',
        'permissions': (),
        'features': (),
        'roles': ('owner', 'admin'),
    },
    {
        'key': 'settings',
        'label': 'Sozlamalar',
        'path': '/dashboard/settings',
        'permissions': (),
        'features': (),
    },
    {
        'key': 'telegram',
        'label': 'Telegram',
        'path': '/dashboard/telegram',
        'permissions': (),
        'features': (),
        'planned': True,
    },
)


ACTION_ITEMS = {
    'run_analysis': {
        'permissions': (
            TeamPermission.RUN_AI_ANALYSIS,
            TeamPermission.USE_ANALYSIS_QUOTAS,
        ),
        'features': (),
    },
    'generate_document': {
        'permissions': (TeamPermission.GENERATE_DOCUMENTS,),
        'features': (Feature.DOCUMENT_GENERATION,),
    },
    'export_document': {
        'permissions': (TeamPermission.EXPORT_DOCUMENTS,),
        'features': (Feature.DOCUMENT_EXPORT,),
    },
    'view_competitors': {
        'permissions': (TeamPermission.VIEW_COMPETITORS,),
        'features': (Feature.COMPETITOR_INTELLIGENCE,),
    },
    'manage_team': {
        'permissions': (TeamPermission.MANAGE_TEAM,),
        'features': (Feature.TEAM_COLLABORATION,),
    },
}


def build_session_capabilities(user, *, company_id=None):
    companies = accessible_companies(user).select_related('user')
    company = (
        companies.filter(pk=company_id).first()
        if company_id
        else companies.order_by('-created_at').first()
    )
    if company_id and company is None:
        return None
    if company is None:
        return _empty_company_payload(user)

    membership = resolve_company_membership(user, company)
    effective, entitlements = list_entitlements(user, company)
    entitlement_map = {
        entitlement.feature: EntitlementSerializer(entitlement).data
        for entitlement in entitlements
    }
    permissions = _effective_permissions(membership)
    force_password_change = user.company_memberships.filter(
        company=company,
        is_active=True,
        force_password_change=True,
    ).exists()

    return {
        'user': UserProfileSerializer(user).data,
        'active_company': _company_payload(company),
        'membership': {
            'role': membership.role,
            'permissions': permissions,
            'force_password_change': force_password_change,
            'can_manage_team': (
                membership.role in {'owner', 'admin'}
                or TeamPermission.MANAGE_TEAM in permissions
            ),
        },
        'subscription': {
            'id': effective.subscription.id,
            'plan': effective.plan.code,
            'status': effective.subscription.status,
            'period_start': effective.period_start,
            'period_end': effective.period_end,
            'limits': {
                **effective.plan.limits,
                'sms_allowed_monthly': effective.subscription.sms_allowed_monthly,
                'sms_sent_this_month': effective.subscription.sms_sent_this_month,
                'daily_sms_cap': effective.subscription.daily_sms_cap,
            },
        },
        'usage': _usage_payload(company, effective),
        'entitlements': list(entitlement_map.values()),
        'navigation': [
            _evaluate_item(item, membership.role, permissions, entitlement_map)
            for item in NAVIGATION_ITEMS
        ],
        'actions': {
            key: _evaluate_item(
                {'key': key, **definition},
                membership.role,
                permissions,
                entitlement_map,
            )
            for key, definition in ACTION_ITEMS.items()
        },
        'platform_admin': user.is_staff,
        'blockers': _blockers(company, force_password_change),
    }


def _empty_company_payload(user):
    return {
        'user': UserProfileSerializer(user).data,
        'active_company': None,
        'membership': None,
        'subscription': None,
        'usage': {},
        'entitlements': [],
        'navigation': [
            {
                **_navigation_shape(item),
                'enabled': False,
                'reason': 'profile_required',
            }
            for item in NAVIGATION_ITEMS
        ],
        'actions': {
            key: {
                'key': key,
                'enabled': False,
                'reason': 'profile_required',
                'required_permissions': list(definition['permissions']),
                'required_features': list(definition['features']),
            }
            for key, definition in ACTION_ITEMS.items()
        },
        'platform_admin': user.is_staff,
        'blockers': [
            {
                'code': 'profile_required',
                'action': 'complete_onboarding',
            },
        ],
    }


def _company_payload(company):
    return {
        'id': company.id,
        'name': company.company_name,
        'stir': company.stir,
        'stir_verified': company.has_stir_identity,
        'stir_skipped': company.stir_skipped,
        'registry_status': company.registry_status,
        'current_tariff': company.current_tariff,
    }


def _effective_permissions(membership):
    if membership.role == 'owner':
        return list(TeamPermission.ALL)
    return list(membership.permissions)


def _usage_payload(company, effective):
    records = {
        record.metric: record
        for record in UsageRecord.objects.filter(
            company=company,
            period_start=effective.period_start,
            period_end=effective.period_end,
        )
    }
    usage = {}
    for metric, limit_key in METRIC_LIMIT_KEYS.items():
        record = records.get(metric)
        limit = effective.plan.limits.get(limit_key)
        used = record.used if record is not None else 0
        usage[metric] = {
            'used': used,
            'limit': limit,
            'remaining': None if limit is None else max(int(limit) - used, 0),
            'period_start': effective.period_start,
            'period_end': effective.period_end,
        }
    return usage


def _evaluate_item(item, role, permissions, entitlement_map):
    result = _navigation_shape(item)
    if item.get('planned'):
        result.update({'enabled': False, 'reason': 'planned_later'})
        return result

    roles = item.get('roles')
    if roles and role not in roles:
        result.update({'enabled': False, 'reason': 'role_denied'})
        return result

    missing_permission = next(
        (
            permission
            for permission in item.get('permissions', ())
            if permission not in permissions
        ),
        None,
    )
    if missing_permission:
        result.update({
            'enabled': False,
            'reason': 'permission_denied',
            'missing_permission': missing_permission,
        })
        return result

    for feature in item.get('features', ()):
        entitlement = entitlement_map.get(feature)
        if not entitlement or not entitlement['allowed']:
            result.update({
                'enabled': False,
                'reason': (
                    entitlement['denial_code']
                    if entitlement
                    else 'feature_not_available'
                ),
                'feature': feature,
            })
            return result

    result.update({'enabled': True, 'reason': None})
    return result


def _navigation_shape(item):
    return {
        'key': item['key'],
        'label': item.get('label', item['key']),
        'path': item.get('path'),
        'required_permissions': list(item.get('permissions', ())),
        'required_features': list(item.get('features', ())),
    }


def _blockers(company, force_password_change):
    blockers = []
    if force_password_change:
        blockers.append({
            'code': 'password_change_required',
            'action': 'change_password',
        })
    if not company.has_stir_identity and not company.stir_skipped:
        blockers.append({
            'code': 'stir_required_for_business_features',
            'action': 'add_or_skip_stir',
        })
    return blockers
