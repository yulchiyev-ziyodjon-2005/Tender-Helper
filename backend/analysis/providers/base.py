from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


class AIProviderError(Exception):
    code = 'ai_provider_failed'


class AIProviderUnavailable(AIProviderError):
    code = 'ai_provider_unavailable'


class AIProviderInvalidResponse(AIProviderError):
    code = 'ai_provider_invalid_response'


@dataclass(frozen=True)
class AIProviderResponse:
    content: dict
    usage: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)


class AIProviderInterface(ABC):
    provider_code = 'base'

    @abstractmethod
    def analyze_tender(
        self,
        document_payload: dict,
        prompt_version: str,
    ) -> AIProviderResponse:
        raise NotImplementedError
