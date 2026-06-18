from rest_framework import status
from rest_framework.exceptions import APIException


class AdminAPIException(APIException):
    status_code = status.HTTP_403_FORBIDDEN

    def __init__(self, *, code, message, details=None, status_code=None):
        if status_code is not None:
            self.status_code = status_code
        self.detail = {
            'code': code,
            'message': message,
            'details': details or {},
        }


class AdminAccessDenied(AdminAPIException):
    def __init__(self, code='admin_access_denied', message=None):
        super().__init__(
            code=code,
            message=message or 'Superadmin access is denied.',
        )


class AdminMFARequired(AdminAPIException):
    def __init__(self):
        super().__init__(
            code='admin_mfa_required',
            message='A recent administrator MFA verification is required.',
        )


class AdminStepUpRequired(AdminAPIException):
    def __init__(self):
        super().__init__(
            code='admin_step_up_required',
            message='This action requires recent step-up authentication.',
        )


class AdminConflict(AdminAPIException):
    def __init__(self, *, code, message, details=None):
        super().__init__(
            code=code,
            message=message,
            details=details,
            status_code=status.HTTP_409_CONFLICT,
        )
