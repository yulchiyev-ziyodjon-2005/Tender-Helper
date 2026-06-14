from django.conf import settings
from django.core.checks import Error, register
from django.utils.module_loading import import_string

from companies.models import CompanyProfile
from companies.services.registry import (
    CompanyRegistryProvider,
    ConfiguredHttpRegistryProvider,
)


@register()
def company_registry_settings_check(app_configs, **kwargs):
    errors = []
    try:
        provider_class = import_string(settings.COMPANY_REGISTRY_PROVIDER)
    except (ImportError, AttributeError) as exc:
        return [
            Error(
                f'Cannot import COMPANY_REGISTRY_PROVIDER: {exc}',
                id='companies.E001',
            ),
        ]

    provider_is_valid = (
        isinstance(provider_class, type)
        and issubclass(provider_class, CompanyRegistryProvider)
    )
    if not provider_is_valid:
        errors.append(Error(
            'COMPANY_REGISTRY_PROVIDER must inherit CompanyRegistryProvider.',
            id='companies.E002',
        ))

    if (
        provider_is_valid
        and issubclass(provider_class, ConfiguredHttpRegistryProvider)
        and not settings.COMPANY_REGISTRY_API_URL
    ):
        errors.append(Error(
            'COMPANY_REGISTRY_API_URL is required for the HTTP provider.',
            id='companies.E003',
        ))

    if settings.COMPANY_REGISTRY_SOURCE not in {
        CompanyProfile.RegistrySource.TAX,
        CompanyProfile.RegistrySource.STATISTICS,
    }:
        errors.append(Error(
            'COMPANY_REGISTRY_SOURCE must be tax or statistics.',
            id='companies.E004',
        ))

    numeric_settings = {
        'COMPANY_REGISTRY_TIMEOUT_SECONDS': (
            settings.COMPANY_REGISTRY_TIMEOUT_SECONDS,
            0,
        ),
        'COMPANY_REGISTRY_CACHE_SECONDS': (
            settings.COMPANY_REGISTRY_CACHE_SECONDS,
            0,
        ),
        'COMPANY_REGISTRY_DRAFT_TTL_SECONDS': (
            settings.COMPANY_REGISTRY_DRAFT_TTL_SECONDS,
            0,
        ),
    }
    for name, (value, minimum) in numeric_settings.items():
        if value <= minimum:
            errors.append(Error(
                f'{name} must be greater than {minimum}.',
                id='companies.E005',
            ))

    if settings.COMPANY_REGISTRY_RETRY_COUNT not in range(0, 4):
        errors.append(Error(
            'COMPANY_REGISTRY_RETRY_COUNT must be between 0 and 3.',
            id='companies.E006',
        ))
    return errors
