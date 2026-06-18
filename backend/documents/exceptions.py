from rest_framework import status
from rest_framework.exceptions import APIException


class DocumentAPIException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = 'document_error'

    def __init__(self, *, code, message, details=None, status_code=None):
        if status_code is not None:
            self.status_code = status_code
        super().__init__(detail=message, code=code)
        self.detail = {
            'code': code,
            'message': message,
            'details': details or {},
        }


class RequiredCompanyFieldsMissing(DocumentAPIException):
    def __init__(self, fields):
        super().__init__(
            code='template_required_fields_missing',
            message='Template uchun majburiy kompaniya maʼlumotlari yetishmaydi.',
            details={'fields': sorted(fields)},
        )


class DocumentStateConflict(DocumentAPIException):
    def __init__(self, *, current_status, allowed_statuses):
        super().__init__(
            code='document_state_conflict',
            message='Hujjat joriy holatida bu amalni bajarib bo‘lmaydi.',
            details={
                'current_status': current_status,
                'allowed_statuses': list(allowed_statuses),
            },
            status_code=status.HTTP_409_CONFLICT,
        )


class EditVersionConflict(DocumentAPIException):
    def __init__(self, *, expected, current):
        super().__init__(
            code='edit_version_conflict',
            message='Hujjat boshqa oynada yangilangan. Yangi versiyani yuklang.',
            details={
                'expected_edit_version': expected,
                'current_edit_version': current,
            },
            status_code=status.HTTP_409_CONFLICT,
        )


class InvalidDocumentContent(DocumentAPIException):
    def __init__(self, errors):
        super().__init__(
            code='invalid_document_content',
            message='Canonical hujjat tarkibi noto‘g‘ri.',
            details={'errors': errors},
        )


class TemplateUnavailable(DocumentAPIException):
    def __init__(self):
        super().__init__(
            code='template_unavailable',
            message='Template faol yoki nashr qilingan emas.',
            status_code=status.HTTP_404_NOT_FOUND,
        )


class ExportNotReady(DocumentAPIException):
    def __init__(self):
        super().__init__(
            code='export_not_ready',
            message='Eksport fayli hali tayyor emas.',
            status_code=status.HTTP_409_CONFLICT,
        )


class InvalidDownloadToken(DocumentAPIException):
    def __init__(self):
        super().__init__(
            code='invalid_download_token',
            message='Yuklab olish havolasi yaroqsiz yoki muddati tugagan.',
            status_code=status.HTTP_403_FORBIDDEN,
        )
