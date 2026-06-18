from __future__ import annotations

import json

import requests
from django.conf import settings

from analysis.providers.base import (
    AIProviderInterface,
    AIProviderInvalidResponse,
    AIProviderResponse,
    AIProviderUnavailable,
)


class GeminiAnalysisProvider(AIProviderInterface):
    provider_code = 'google_gemini'

    def __init__(self, session=None):
        self.session = session or requests.Session()
        self.session.trust_env = False

    def analyze_tender(
        self,
        document_payload: dict,
        prompt_version: str,
    ) -> AIProviderResponse:
        if not settings.GEMINI_API_KEY:
            raise AIProviderUnavailable('Gemini API key is not configured.')

        response = self.session.post(
            _generate_content_url(),
            params={'key': settings.GEMINI_API_KEY},
            json={
                'contents': [{
                    'role': 'user',
                    'parts': [{
                        'text': json.dumps(document_payload, ensure_ascii=False),
                    }],
                }],
                'generationConfig': {
                    'temperature': 0.2,
                    'responseMimeType': 'application/json',
                },
            },
            headers={'Content-Type': 'application/json'},
            timeout=settings.GEMINI_TIMEOUT,
        )
        try:
            response.raise_for_status()
            payload = response.json()
            raw_content = payload['candidates'][0]['content']['parts'][0]['text']
            content = _parse_json_content(raw_content)
        except requests.RequestException as exc:
            raise AIProviderUnavailable(str(exc)) from exc
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            raise AIProviderInvalidResponse() from exc

        return AIProviderResponse(
            content=content,
            usage=payload.get('usageMetadata', {}),
            metadata={
                'provider': self.provider_code,
                'model': settings.GEMINI_MODEL_ANALYSIS,
                'prompt_version': prompt_version,
            },
        )


def _generate_content_url() -> str:
    return (
        'https://generativelanguage.googleapis.com/v1beta/models/'
        f'{settings.GEMINI_MODEL_ANALYSIS}:generateContent'
    )


def _parse_json_content(raw_content: str) -> dict:
    if raw_content.startswith('```json'):
        raw_content = raw_content[7:-3].strip()
    elif raw_content.startswith('```'):
        raw_content = raw_content[3:-3].strip()
    return json.loads(raw_content)
