from rest_framework import status
from rest_framework.exceptions import APIException


class SubscriptionAPIException(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_code = 'subscription_access_denied'

    def __init__(self, *, code, message, details=None, status_code=None):
        if status_code is not None:
            self.status_code = status_code
        super().__init__(
            detail={
                'code': code,
                'message': message,
                'details': details or {},
            },
            code=code,
        )


class CompanyAccessDenied(SubscriptionAPIException):
    def __init__(self):
        super().__init__(
            code='company_access_denied',
            message="Bu kompaniya nomidan amal bajarishga ruxsatingiz yo'q.",
        )


class CompanyRoleDenied(SubscriptionAPIException):
    def __init__(self, *, feature, required_roles):
        super().__init__(
            code='company_role_denied',
            message="Kompaniyadagi rolingiz bu amal uchun yetarli emas.",
            details={
                'feature': feature,
                'required_roles': list(required_roles),
            },
        )


class FeatureNotAvailable(SubscriptionAPIException):
    def __init__(self, *, feature, required_plan, requires_stir):
        super().__init__(
            code='feature_not_available',
            message=f'Bu funksiya {required_plan.title()} tarifida mavjud',
            details={
                'feature': feature,
                'requires_stir': requires_stir,
                'required_plan': required_plan,
            },
        )


class StirRequired(SubscriptionAPIException):
    def __init__(self, *, feature, required_plan):
        super().__init__(
            code='stir_required',
            message="Bu funksiya uchun kompaniya STIRini qo'shing.",
            details={
                'feature': feature,
                'requires_stir': True,
                'required_plan': required_plan,
                'action': 'add_stir',
            },
        )


class UsageLimitExceeded(SubscriptionAPIException):
    def __init__(self, *, metric, plan, limit, used, period_end):
        super().__init__(
            code='usage_limit_exceeded',
            message='Joriy hisob davri uchun foydalanish limiti tugagan.',
            details={
                'metric': metric,
                'plan': plan,
                'limit': limit,
                'used': used,
                'period_end': period_end,
            },
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        )
