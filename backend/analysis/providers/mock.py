from __future__ import annotations

from analysis.providers.base import AIProviderInterface, AIProviderResponse


class MockAIProvider(AIProviderInterface):
    provider_code = 'mock'

    def analyze_tender(
        self,
        document_payload: dict,
        prompt_version: str,
    ) -> AIProviderResponse:
        return AIProviderResponse(
            content={
                'eligibility_score': 81,
                'summary_text': 'Mock provider analysis result.',
                'missing_documents': [],
                'red_flags': [{
                    'level': 'warning',
                    'title': 'Mock risk',
                    'reason': 'Deterministic unit-test provider response.',
                    'recommendation': 'Replace with Gemini in production.',
                    'citations': ['tender-title-0'],
                }],
                'standards': [],
                'requirements': [],
                'decision': {},
            },
            usage={
                'promptTokenCount': 10,
                'candidatesTokenCount': 10,
                'totalTokenCount': 20,
            },
            metadata={
                'provider': self.provider_code,
                'model': 'mock-analysis',
                'prompt_version': prompt_version,
            },
        )
