import hashlib
import json
import logging
import time
import traceback as traceback_module
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

import requests
from django.conf import settings
from django.db import IntegrityError, transaction
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from tenders.models import (
    ScrapeError,
    ScrapeRun,
    TenderDocument,
    TenderLot,
    TenderSource,
)

logger = logging.getLogger(__name__)


class PortalAdapterError(Exception):
    """Raised when an external portal cannot be read or normalized."""


@dataclass(frozen=True)
class NormalizedTenderPayload:
    tender_id: str
    title: str
    organization_name: str
    total_amount: Decimal
    category: str
    published_at: object
    deadline_at: object
    raw_payload: dict
    raw_portal_url: str = ''


class PortalAdapter:
    source_code = TenderLot.PlatformSource.XARID_UZEX

    def fetch_latest(self, *, limit=100):
        raise NotImplementedError

    def normalize(self, payload):
        raise NotImplementedError


class HttpJsonPortalAdapter(PortalAdapter):
    """Generic JSON adapter for approved portal API contracts."""

    def __init__(self, *, source_code, base_url, session=None):
        self.source_code = source_code
        self.base_url = base_url
        self.session = session or requests.Session()
        self.session.trust_env = False

    def fetch_latest(self, *, limit=100):
        if not self.base_url:
            raise PortalAdapterError('Portal API URL is not configured.')
        response = self.session.get(
            self.base_url,
            params={'limit': limit},
            timeout=getattr(settings, 'SCRAPER_TIMEOUT_SECONDS', 15),
            headers={'Accept': 'application/json'},
        )
        response.raise_for_status()
        payload = response.json()
        if isinstance(payload, list):
            return payload[:limit]
        if isinstance(payload, dict):
            rows = payload.get('results') or payload.get('data') or payload.get('items')
            if isinstance(rows, list):
                return rows[:limit]
        raise PortalAdapterError('Portal response does not contain a list.')

    def normalize(self, payload):
        if not isinstance(payload, dict):
            raise PortalAdapterError('Portal payload must be an object.')
        tender_id = str(
            payload.get('tender_id')
            or payload.get('external_id')
            or payload.get('lot_number')
            or payload.get('id')
            or ''
        ).strip()
        if not tender_id:
            raise PortalAdapterError('Portal payload is missing tender_id.')

        title = str(payload.get('title') or payload.get('name') or '').strip()
        if not title:
            raise PortalAdapterError('Portal payload is missing title.')

        published_at = _parse_datetime(
            payload.get('published_at')
            or payload.get('posted_date')
            or payload.get('created_at')
            or timezone.now(),
            'published_at',
        )
        deadline_at = _parse_datetime(
            payload.get('deadline_at')
            or payload.get('deadline')
            or payload.get('end_date'),
            'deadline_at',
        )
        if deadline_at <= published_at:
            raise PortalAdapterError('Portal deadline must follow publish time.')

        return NormalizedTenderPayload(
            tender_id=tender_id,
            title=title,
            organization_name=str(
                payload.get('organization_name')
                or payload.get('buyer_name')
                or payload.get('customer')
                or ''
            ).strip(),
            total_amount=_parse_decimal(
                payload.get('total_amount')
                or payload.get('start_price')
                or payload.get('amount')
                or 0,
            ),
            category=str(payload.get('category') or '').strip(),
            published_at=published_at,
            deadline_at=deadline_at,
            raw_payload=payload,
            raw_portal_url=str(
                payload.get('raw_portal_url')
                or payload.get('url')
                or ''
            ).strip(),
        )


class UzExScraper:
    """Idempotent tender ingestion service with retry/backoff."""

    def __init__(self, adapter=None, *, source_code=TenderLot.PlatformSource.XARID_UZEX):
        self.source_code = source_code
        self.source = TenderSource.objects.get(code=source_code)
        self.adapter = adapter or HttpJsonPortalAdapter(
            source_code=source_code,
            base_url=self.source.configuration.get('api_url')
            or getattr(settings, 'TENDER_PORTALS', {}).get(source_code, ''),
        )

    def fetch_latest_tenders(self, limit=100):
        run = ScrapeRun.objects.create(source=self.source)
        try:
            payloads = self._fetch_with_retry(limit=limit)
            processed_count = 0
            for payload in payloads:
                normalized = self.adapter.normalize(payload)
                if ingest_tender_payload(
                    source=self.source,
                    normalized=normalized,
                    scrape_run=run,
                ):
                    processed_count += 1
            run.status = ScrapeRun.Status.SUCCESS
            run.processed_count = processed_count
            run.completed_at = timezone.now()
            run.save(update_fields=[
                'status',
                'processed_count',
                'completed_at',
            ])
            return processed_count
        except Exception as exc:
            logger.exception('Tender scrape failed source=%s', self.source.code)
            run.status = ScrapeRun.Status.FAILED
            run.completed_at = timezone.now()
            run.save(update_fields=['status', 'completed_at'])
            ScrapeError.objects.create(
                scrape_run=run,
                source=self.source,
                error_message=str(exc),
                traceback=traceback_module.format_exc(),
            )
            raise

    def _fetch_with_retry(self, *, limit):
        attempts = int(getattr(settings, 'SCRAPER_RETRY_COUNT', 3))
        base_delay = float(getattr(settings, 'SCRAPER_RETRY_BASE_SECONDS', 0.5))
        last_error = None
        for attempt in range(max(attempts, 1)):
            try:
                return self.adapter.fetch_latest(limit=limit)
            except (requests.RequestException, PortalAdapterError) as exc:
                last_error = exc
                if attempt + 1 >= attempts:
                    break
                delay = base_delay * (2 ** attempt)
                logger.warning(
                    'Portal fetch failed source=%s attempt=%s retry_in=%ss',
                    self.source.code,
                    attempt + 1,
                    delay,
                )
                time.sleep(delay)
        raise PortalAdapterError('Portal fetch failed after retries.') from last_error


def ingest_tender_payload(*, source, normalized, scrape_run=None):
    hash_sum = payload_hash(normalized.raw_payload)
    if TenderDocument.objects.filter(hash_sum=hash_sum).exists():
        return False

    with transaction.atomic():
        tender_lot, _ = TenderLot.objects.update_or_create(
            source=source,
            external_id=normalized.tender_id,
            defaults={
                'lot_number': normalized.tender_id,
                'platform_source': source.code,
                'title': normalized.title,
                'buyer_name': normalized.organization_name,
                'start_price': normalized.total_amount,
                'zakalat_amount': normalized.total_amount
                * Decimal(str(getattr(settings, 'ZAKALAT_RATE', 0.03))),
                'category': normalized.category,
                'posted_date': normalized.published_at,
                'deadline': normalized.deadline_at,
                'status': TenderLot.Status.ACTIVE,
                'raw_portal_url': normalized.raw_portal_url,
                'raw_json': normalized.raw_payload,
            },
        )
        try:
            document = TenderDocument.objects.create(
                scrape_run=scrape_run,
                source=source,
                tender_id=normalized.tender_id,
                tender_lot=tender_lot,
                title=normalized.title,
                organization_name=normalized.organization_name,
                total_amount=normalized.total_amount,
                category=normalized.category,
                published_at=normalized.published_at,
                deadline_at=normalized.deadline_at,
                raw_payload=normalized.raw_payload,
                hash_sum=hash_sum,
            )
        except IntegrityError:
            return False
        transaction.on_commit(lambda: _schedule_tender_matching(document.id))
    return True


def _schedule_tender_matching(tender_document_id):
    from tenders.tasks import match_tender_document_task

    match_tender_document_task.delay(str(tender_document_id))


def payload_hash(payload):
    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(',', ':'),
        ensure_ascii=False,
        default=str,
    )
    return hashlib.sha256(canonical.encode('utf-8')).hexdigest()


def _parse_decimal(value):
    try:
        return Decimal(str(value).replace('_', '').replace(',', ''))
    except (InvalidOperation, ValueError) as exc:
        raise PortalAdapterError('Portal amount is invalid.') from exc


def _parse_datetime(value, field):
    if value is None or value == '':
        raise PortalAdapterError(f'Portal payload is missing {field}.')
    if hasattr(value, 'tzinfo'):
        result = value
    else:
        result = parse_datetime(str(value))
    if result is None:
        raise PortalAdapterError(f'Portal {field} is invalid.')
    if timezone.is_naive(result):
        result = timezone.make_aware(result, timezone.get_current_timezone())
    return result


def run_scraper_task():
    scraper = UzExScraper()
    return scraper.fetch_latest_tenders()
