import logging
import time
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from datetime import date, timedelta

import requests
from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone
from django.utils.module_loading import import_string

from companies.models import CompanyProfile, CompanyRegistryDraft

logger = logging.getLogger(__name__)

CACHE_VERSION = 'v1'
CONFIRMABLE_FIELDS = {
    'company_name',
    'company_type',
    'industry',
    'director_name',
    'legal_address',
    'registration_date',
    'has_vat',
    'experience_level',
}


class RegistryError(Exception):
    code = 'registry_error'
    public_message = 'Registry lookup failed'

    def __init__(self, message=None, *, cache_hit=False):
        super().__init__(message or self.public_message)
        self.cache_hit = cache_hit


class RegistryNotFoundError(RegistryError):
    code = 'registry_not_found'
    public_message = 'Company was not found in the registry'


class RegistryUnavailableError(RegistryError):
    code = 'registry_unavailable'
    public_message = 'Company registry is temporarily unavailable'


class RegistryInvalidResponseError(RegistryError):
    code = 'registry_invalid_response'
    public_message = 'Company registry returned an invalid response'


class DraftStateError(Exception):
    code = 'invalid_draft_state'
    public_message = 'Registry draft cannot be confirmed'


class DraftExpiredError(DraftStateError):
    code = 'draft_expired'
    public_message = 'Registry draft has expired'


class StirAlreadyUsedError(DraftStateError):
    code = 'stir_already_used'
    public_message = 'This STIR is already linked to another company'


@dataclass(frozen=True)
class RegistryCompanyData:
    company_name: str
    company_type: str
    director_name: str = ''
    legal_address: str = ''
    registration_date: str | None = None
    has_vat: bool = False
    industry: str = ''


@dataclass(frozen=True)
class RegistryProviderResult:
    company: RegistryCompanyData
    raw_payload: dict


@dataclass(frozen=True)
class CachedRegistryResult:
    company: RegistryCompanyData
    raw_payload: dict
    provider: str
    source: str
    cache_hit: bool


class CompanyRegistryProvider(ABC):
    provider_code = 'base'
    source = CompanyProfile.RegistrySource.MANUAL

    @abstractmethod
    def lookup(self, stir: str) -> RegistryProviderResult:
        raise NotImplementedError


class DisabledCompanyRegistryProvider(CompanyRegistryProvider):
    provider_code = 'disabled'

    def lookup(self, stir: str) -> RegistryProviderResult:
        raise RegistryUnavailableError(
            'Company registry provider is not configured'
        )


class ConfiguredHttpRegistryProvider(CompanyRegistryProvider):
    provider_code = 'configured_http'

    def __init__(self, session=None):
        self.session = session or requests.Session()
        self.source = _registry_source_from_settings()

    def lookup(self, stir: str) -> RegistryProviderResult:
        if not settings.COMPANY_REGISTRY_API_URL:
            raise RegistryUnavailableError('Company registry URL is not configured')

        headers = {'Accept': 'application/json'}
        if settings.COMPANY_REGISTRY_API_TOKEN:
            headers['Authorization'] = (
                f'Bearer {settings.COMPANY_REGISTRY_API_TOKEN}'
            )

        attempts = settings.COMPANY_REGISTRY_RETRY_COUNT + 1
        last_error = None
        for attempt in range(attempts):
            try:
                response = self.session.get(
                    settings.COMPANY_REGISTRY_API_URL,
                    params={'stir': stir},
                    headers=headers,
                    timeout=settings.COMPANY_REGISTRY_TIMEOUT_SECONDS,
                )
                if response.status_code == 404:
                    raise RegistryNotFoundError()
                if response.status_code == 429 or response.status_code >= 500:
                    response.raise_for_status()
                if response.status_code >= 400:
                    raise RegistryUnavailableError(
                        f'Registry rejected request with HTTP {response.status_code}'
                    )

                try:
                    payload = response.json()
                except ValueError as exc:
                    raise RegistryInvalidResponseError() from exc

                return RegistryProviderResult(
                    company=normalize_registry_payload(payload),
                    raw_payload=payload,
                )
            except RegistryNotFoundError:
                raise
            except RegistryInvalidResponseError:
                raise
            except RegistryUnavailableError:
                raise
            except requests.RequestException as exc:
                last_error = exc
                if attempt + 1 >= attempts:
                    break

        raise RegistryUnavailableError() from last_error


def validate_stir_format(stir):
    value = str(stir or '').strip()
    if len(value) != 9 or not value.isdigit():
        raise ValueError("STIR 9 ta raqamdan iborat bo'lishi kerak")
    return value


def normalize_registry_payload(payload):
    if not isinstance(payload, dict):
        raise RegistryInvalidResponseError()

    data = payload.get('data', payload)
    if not isinstance(data, dict):
        raise RegistryInvalidResponseError()

    company_name = str(data.get('company_name') or '').strip()
    if not company_name:
        raise RegistryInvalidResponseError('Registry company name is missing')

    registration_date = _normalize_date(data.get('registration_date'))
    return RegistryCompanyData(
        company_name=company_name,
        company_type=_normalize_company_type(data.get('company_type')),
        director_name=str(data.get('director_name') or '').strip(),
        legal_address=str(data.get('legal_address') or '').strip(),
        registration_date=registration_date,
        has_vat=_normalize_boolean(data.get('has_vat')),
        industry=str(data.get('industry') or '').strip(),
    )


def get_registry_provider():
    provider_class = import_string(settings.COMPANY_REGISTRY_PROVIDER)
    provider = provider_class()
    if not isinstance(provider, CompanyRegistryProvider):
        raise TypeError(
            'COMPANY_REGISTRY_PROVIDER must inherit CompanyRegistryProvider'
        )
    return provider


def lookup_registry(stir, *, force_refresh=False, provider=None):
    stir = validate_stir_format(stir)
    provider = provider or get_registry_provider()
    cache_key = _cache_key(provider.provider_code, provider.source, stir)

    if not force_refresh:
        cached = cache.get(cache_key)
        if cached:
            try:
                if cached['kind'] == 'not_found':
                    raise RegistryNotFoundError(cache_hit=True)
                return CachedRegistryResult(
                    company=RegistryCompanyData(**cached['company']),
                    raw_payload=cached['raw_payload'],
                    provider=provider.provider_code,
                    source=provider.source,
                    cache_hit=True,
                )
            except RegistryNotFoundError:
                raise
            except (KeyError, TypeError, ValueError):
                logger.warning(
                    'Discarding invalid registry cache entry provider=%s '
                    'stir_suffix=%s',
                    provider.provider_code,
                    stir[-4:],
                )
                cache.delete(cache_key)

    try:
        result = provider.lookup(stir)
    except RegistryNotFoundError:
        cache.set(
            cache_key,
            {'kind': 'not_found'},
            timeout=settings.COMPANY_REGISTRY_CACHE_SECONDS,
        )
        raise
    except RegistryError:
        raise
    except Exception as exc:
        logger.exception(
            'Unexpected registry provider error provider=%s stir_suffix=%s',
            provider.provider_code,
            stir[-4:],
        )
        raise RegistryUnavailableError() from exc

    cached_value = {
        'kind': 'success',
        'company': asdict(result.company),
        'raw_payload': result.raw_payload,
    }
    cache.set(
        cache_key,
        cached_value,
        timeout=settings.COMPANY_REGISTRY_CACHE_SECONDS,
    )
    return CachedRegistryResult(
        company=result.company,
        raw_payload=result.raw_payload,
        provider=provider.provider_code,
        source=provider.source,
        cache_hit=False,
    )


def create_registry_draft(user, stir, *, profile=None, force_refresh=False):
    stir = validate_stir_format(stir)
    if profile is not None and profile.user_id != user.id:
        raise ValueError('Registry draft profile must belong to the user')
    started_at = time.monotonic()
    provider = get_registry_provider()
    draft = CompanyRegistryDraft.objects.create(
        user=user,
        profile=profile,
        stir=stir,
        provider=provider.provider_code,
        source=provider.source,
        status=CompanyRegistryDraft.Status.PENDING,
        expires_at=timezone.now() + timedelta(
            seconds=settings.COMPANY_REGISTRY_DRAFT_TTL_SECONDS
        ),
    )
    _update_profile_registry_state(
        profile,
        status=CompanyProfile.RegistryStatus.PENDING,
    )

    try:
        result = lookup_registry(
            stir,
            force_refresh=force_refresh,
            provider=provider,
        )
    except RegistryError as exc:
        duration_ms = round((time.monotonic() - started_at) * 1000)
        draft.status = CompanyRegistryDraft.Status.FAILED
        draft.error_code = exc.code
        draft.error_message = exc.public_message
        draft.cache_hit = exc.cache_hit
        draft.lookup_metadata = {'duration_ms': duration_ms}
        draft.save(update_fields=[
            'status',
            'error_code',
            'error_message',
            'cache_hit',
            'lookup_metadata',
            'updated_at',
        ])
        profile_status = (
            CompanyProfile.RegistryStatus.NOT_FOUND
            if isinstance(exc, RegistryNotFoundError)
            else CompanyProfile.RegistryStatus.FAILED
        )
        _update_profile_registry_state(
            profile,
            status=profile_status,
            fetched_at=timezone.now(),
        )
        logger.info(
            'Registry lookup failed provider=%s stir_suffix=%s code=%s '
            'cache_hit=%s duration_ms=%s',
            provider.provider_code,
            stir[-4:],
            exc.code,
            exc.cache_hit,
            duration_ms,
        )
        return draft

    duration_ms = round((time.monotonic() - started_at) * 1000)
    draft.provider = result.provider
    draft.source = result.source
    draft.normalized_data = asdict(result.company)
    draft.raw_payload = result.raw_payload
    draft.status = CompanyRegistryDraft.Status.READY
    draft.cache_hit = result.cache_hit
    draft.lookup_metadata = {'duration_ms': duration_ms}
    draft.save(update_fields=[
        'provider',
        'source',
        'normalized_data',
        'raw_payload',
        'status',
        'cache_hit',
        'lookup_metadata',
        'updated_at',
    ])
    _update_profile_registry_state(
        profile,
        status=CompanyProfile.RegistryStatus.PENDING,
        fetched_at=timezone.now(),
    )
    logger.info(
        'Registry lookup completed provider=%s stir_suffix=%s cache_hit=%s '
        'duration_ms=%s',
        result.provider,
        stir[-4:],
        result.cache_hit,
        duration_ms,
    )
    return draft


@transaction.atomic
def confirm_registry_draft(user, draft_id, confirmed_data):
    draft = (
        CompanyRegistryDraft.objects.select_for_update()
        .filter(user=user, id=draft_id)
        .first()
    )
    if draft is None:
        return None
    if draft.is_expired:
        raise DraftExpiredError()
    if draft.status != CompanyRegistryDraft.Status.READY:
        raise DraftStateError()

    profile = draft.profile
    if profile is not None:
        profile = CompanyProfile.objects.select_for_update().get(id=profile.id)
    else:
        profile = (
            CompanyProfile.objects.select_for_update()
            .filter(user=user)
            .order_by('-created_at')
            .first()
        )

    duplicate = CompanyProfile.objects.filter(stir=draft.stir)
    if profile is not None:
        duplicate = duplicate.exclude(id=profile.id)
    if duplicate.exists():
        raise StirAlreadyUsedError()

    values = {
        key: value
        for key, value in confirmed_data.items()
        if key in CONFIRMABLE_FIELDS
    }
    if profile is None:
        profile = CompanyProfile(user=user)
    for field, value in values.items():
        setattr(profile, field, value)

    profile.stir = draft.stir
    profile.stir_skipped = False
    profile.registry_source = draft.source
    profile.registry_status = CompanyProfile.RegistryStatus.VERIFIED
    profile.registry_fetched_at = timezone.now()
    profile.raw_tax_data = draft.raw_payload
    profile.full_clean(validate_unique=False)
    try:
        profile.save()
    except (IntegrityError, ValidationError) as exc:
        raise StirAlreadyUsedError() from exc

    draft.profile = profile
    draft.confirmed_data = {
        key: value.isoformat() if isinstance(value, date) else value
        for key, value in values.items()
    }
    draft.status = CompanyRegistryDraft.Status.CONFIRMED
    draft.confirmed_at = timezone.now()
    draft.save(update_fields=[
        'profile',
        'confirmed_data',
        'status',
        'confirmed_at',
        'updated_at',
    ])
    return draft


def expire_registry_draft(draft):
    if draft.is_expired:
        draft.status = CompanyRegistryDraft.Status.EXPIRED
        draft.save(update_fields=['status', 'updated_at'])
    return draft


def _update_profile_registry_state(profile, *, status, fetched_at=None):
    if profile is None:
        return
    profile.registry_status = status
    update_fields = ['registry_status', 'updated_at']
    if fetched_at is not None:
        profile.registry_fetched_at = fetched_at
        update_fields.append('registry_fetched_at')
    profile.save(update_fields=update_fields)


def _registry_source_from_settings():
    valid_sources = {
        CompanyProfile.RegistrySource.TAX,
        CompanyProfile.RegistrySource.STATISTICS,
    }
    if settings.COMPANY_REGISTRY_SOURCE not in valid_sources:
        raise RegistryUnavailableError('Invalid registry source configuration')
    return settings.COMPANY_REGISTRY_SOURCE


def _cache_key(provider_code, source, stir):
    return (
        f'tenderhelper:company-registry:{CACHE_VERSION}:'
        f'{provider_code}:{source}:{stir}'
    )


def _normalize_company_type(value):
    normalized = str(value or '').strip().lower()
    mapping = {
        'mchj': CompanyProfile.CompanyType.MCHJ,
        'ooo': CompanyProfile.CompanyType.MCHJ,
        'llc': CompanyProfile.CompanyType.MCHJ,
        'yatt': CompanyProfile.CompanyType.YATT,
        'ip': CompanyProfile.CompanyType.YATT,
        'aj': CompanyProfile.CompanyType.AJ,
        'jsc': CompanyProfile.CompanyType.AJ,
        'tt': CompanyProfile.CompanyType.TT,
    }
    return mapping.get(normalized, '')


def _normalize_boolean(value):
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return str(value).strip().lower() in {'1', 'true', 'yes', 'ha', 'active'}


def _normalize_date(value):
    if value in (None, ''):
        return None
    try:
        return date.fromisoformat(str(value)).isoformat()
    except ValueError as exc:
        raise RegistryInvalidResponseError(
            'Registry registration date is invalid'
        ) from exc
