from django.conf import settings
from django.core.checks import Error, register
from django.utils.module_loading import import_string

from documents.services.providers import DocumentGenerationProvider


@register()
def document_settings_check(app_configs, **kwargs):
    errors = []
    try:
        provider_class = import_string(settings.DOCUMENT_GENERATION_PROVIDER)
    except (ImportError, AttributeError) as exc:
        return [
            Error(
                f'Cannot import DOCUMENT_GENERATION_PROVIDER: {exc}',
                id='documents.E001',
            ),
        ]
    if (
        not isinstance(provider_class, type)
        or not issubclass(provider_class, DocumentGenerationProvider)
    ):
        errors.append(Error(
            'DOCUMENT_GENERATION_PROVIDER must inherit '
            'DocumentGenerationProvider.',
            id='documents.E002',
        ))
    if settings.DOCUMENT_GENERATION_TIMEOUT_SECONDS <= 0:
        errors.append(Error(
            'DOCUMENT_GENERATION_TIMEOUT_SECONDS must be greater than zero.',
            id='documents.E003',
        ))
    if settings.DOCUMENT_EXPORT_URL_TTL_SECONDS <= 0:
        errors.append(Error(
            'DOCUMENT_EXPORT_URL_TTL_SECONDS must be greater than zero.',
            id='documents.E004',
        ))
    return errors
