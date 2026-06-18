from __future__ import annotations

from django.conf import settings
from django.utils.module_loading import import_string

from analysis.providers.base import AIProviderInterface


def get_analysis_provider() -> AIProviderInterface:
    provider_class = import_string(settings.ANALYSIS_PROVIDER)
    if (
        not isinstance(provider_class, type)
        or not issubclass(provider_class, AIProviderInterface)
    ):
        raise TypeError('ANALYSIS_PROVIDER must inherit AIProviderInterface.')
    return provider_class()
