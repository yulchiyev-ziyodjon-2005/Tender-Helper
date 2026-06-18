import io
import json
from datetime import datetime, timedelta
from decimal import Decimal
from unittest import skipUnless
from unittest.mock import patch

from django.core.management import call_command
from django.db import IntegrityError, connection, transaction
from django.test import override_settings
from django.test.utils import CaptureQueriesContext
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from companies.models import CompanyProfile
from subscriptions.models import (
    NotificationLog,
    SubscriptionPlan,
)
from subscriptions.services.billing import activate_subscription
from tenders.models import (
    ScrapeRun,
    TenderDocument,
    TenderDocumentChunk,
    TenderLot,
    TenderSource,
)
from tenders.services.scraper import (
    NormalizedTenderPayload,
    PortalAdapterError,
    UzExScraper,
)
from tenders.tasks import (
    deliver_matching_lot_sms_task,
    dispatch_matching_lot_sms_task,
    match_tender_document_task,
)
from users.models import CustomUser


class TenderFactoryMixin:
    def create_tender(
        self,
        lot_number,
        *,
        title='Server equipment supply',
        buyer_name='Digital Ministry',
        category='IT Services',
        region='Toshkent',
        start_price='1000000.00',
        platform_source=TenderLot.PlatformSource.XARID_UZEX,
        status_value=TenderLot.Status.ACTIVE,
        deadline_days=7,
    ):
        now = timezone.now()
        source = TenderSource.objects.get(code=platform_source)
        return TenderLot.objects.create(
            source=source,
            external_id=(
                ''
                if platform_source == TenderLot.PlatformSource.MANUAL
                else lot_number
            ),
            lot_number=lot_number,
            platform_source=platform_source,
            title=title,
            buyer_name=buyer_name,
            start_price=start_price,
            region=region,
            category=category,
            posted_date=now,
            deadline=now + timedelta(days=deadline_days),
            status=status_value,
        )


class ManualTenderSecurityTests(TenderFactoryMixin, APITestCase):
    payload = {
        'title': 'Manual tender',
        'tender_text': 'Tender talablari',
        'buyer_name': 'Buyurtmachi',
    }

    def test_manual_tender_requires_authentication(self):
        response = self.client.post(
            '/api/v1/tenders/manual/',
            self.payload,
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_manual_tender_records_owner(self):
        user = CustomUser.objects.create_user(
            phone_number='+998901110011',
        )
        self.client.force_authenticate(user)

        response = self.client.post(
            '/api/v1/tenders/manual/',
            self.payload,
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            str(user.manual_tenders.get().id),
            response.data['id'],
        )
        self.assertEqual(response.data['source'], 'manual')
        self.assertEqual(response.data['external_id'], '')


class TenderDatabaseIntegrityTests(TenderFactoryMixin, APITestCase):
    def test_source_external_id_is_canonical_unique_identity(self):
        first = self.create_tender('SHARED-001')
        other_source = TenderSource.objects.get(
            code=TenderLot.PlatformSource.DXARID_UZEX,
        )
        second = TenderLot.objects.create(
            source=other_source,
            external_id=first.external_id,
            lot_number=first.lot_number,
            platform_source=TenderLot.PlatformSource.DXARID_UZEX,
            title='Same external identifier in another source',
            posted_date=timezone.now(),
            deadline=timezone.now() + timedelta(days=7),
        )

        self.assertNotEqual(first.source_id, second.source_id)
        with self.assertRaises(IntegrityError), transaction.atomic():
            TenderLot.objects.create(
                source=first.source,
                external_id=first.external_id,
                lot_number='DISPLAY-ALIAS',
                platform_source=first.platform_source,
                title='Duplicate source identity',
                posted_date=timezone.now(),
                deadline=timezone.now() + timedelta(days=7),
            )

    def test_database_rejects_invalid_tender_amounts_and_dates(self):
        source = TenderSource.objects.get(
            code=TenderLot.PlatformSource.XARID_UZEX,
        )
        now = timezone.now()

        with self.assertRaises(IntegrityError), transaction.atomic():
            TenderLot.objects.create(
                source=source,
                external_id='INVALID-PRICE',
                lot_number='INVALID-PRICE',
                platform_source=source.code,
                title='Invalid price',
                start_price=-1,
                posted_date=now,
                deadline=now + timedelta(days=1),
            )

        with self.assertRaises(IntegrityError), transaction.atomic():
            TenderLot.objects.create(
                source=source,
                external_id='INVALID-DEADLINE',
                lot_number='INVALID-DEADLINE',
                platform_source=source.code,
                title='Invalid deadline',
                posted_date=now,
                deadline=now,
            )


class TenderSearchApiTests(TenderFactoryMixin, APITestCase):
    def setUp(self):
        self.server = self.create_tender(
            'UZ-IT-2026-001',
            title='High performance SERVER cluster',
            buyer_name='Digital Ministry',
            category='Infrastructure IT',
            region='Toshkent',
            start_price='90000000.00',
        )
        self.office = self.create_tender(
            'OFFICE-2026-002',
            title='Office furniture procurement 100%',
            buyer_name='Central Bank',
            category='Furniture',
            region='Samarqand',
            start_price='20000000.00',
            platform_source=TenderLot.PlatformSource.DXARID_UZEX,
        )
        self.completed = self.create_tender(
            'OLD-SERVER-003',
            title='Old server lot',
            status_value=TenderLot.Status.COMPLETED,
        )

    def test_search_is_case_insensitive_across_all_contract_fields(self):
        cases = (
            ('server', self.server.id),
            ('digital ministry', self.server.id),
            ('uz-it-2026', self.server.id),
            ('infrastructure', self.server.id),
        )

        for query, expected_id in cases:
            with self.subTest(query=query):
                response = self.client.get(
                    '/api/v1/tenders/',
                    {'search': query},
                )
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertEqual(response.data['count'], 1)
                self.assertEqual(
                    response.data['results'][0]['id'],
                    str(expected_id),
                )

    def test_search_and_filters_and_ordering_work_together(self):
        response = self.client.get(
            '/api/v1/tenders/',
            {
                'search': 'office',
                'category': 'FURNITURE',
                'region': 'samarqand',
                'platform_source': TenderLot.PlatformSource.DXARID_UZEX,
                'min_price': '10000000',
                'max_price': '30000000',
                'ordering': 'start_price',
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(
            response.data['results'][0]['id'],
            str(self.office.id),
        )

    def test_whitespace_search_returns_only_active_paginated_lots(self):
        response = self.client.get(
            '/api/v1/tenders/',
            {'search': '   '},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        self.assertNotIn(
            str(self.completed.id),
            {item['id'] for item in response.data['results']},
        )

    def test_like_wildcards_are_treated_as_literal_user_input(self):
        response = self.client.get(
            '/api/v1/tenders/',
            {'search': '100%'},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(
            response.data['results'][0]['id'],
            str(self.office.id),
        )

    def test_quoted_phrase_is_kept_as_one_search_term(self):
        response = self.client.get(
            '/api/v1/tenders/',
            {'search': '"performance server"'},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(
            response.data['results'][0]['id'],
            str(self.server.id),
        )

    def test_search_query_length_is_bounded(self):
        response = self.client.get(
            '/api/v1/tenders/',
            {'search': 'x' * 201},
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error_code'], 'validation_error')
        self.assertIn('search', response.data['details'])

    def test_page_size_is_capped_at_one_hundred(self):
        source = TenderSource.objects.get(
            code=TenderLot.PlatformSource.XARID_UZEX,
        )
        TenderLot.objects.bulk_create([
            TenderLot(
                source=source,
                external_id=f'PAGE-{index:03d}',
                lot_number=f'PAGE-{index:03d}',
                platform_source=TenderLot.PlatformSource.XARID_UZEX,
                title=f'Pagination tender {index}',
                posted_date=timezone.now(),
                deadline=timezone.now() + timedelta(days=7),
                status=TenderLot.Status.ACTIVE,
            )
            for index in range(105)
        ])

        response = self.client.get(
            '/api/v1/tenders/',
            {'page_size': 1000},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 107)
        self.assertEqual(len(response.data['results']), 100)

    def test_list_chunk_count_does_not_create_n_plus_one_queries(self):
        TenderDocumentChunk.objects.create(
            tender_lot=self.server,
            file_name='requirements.txt',
            chunk_index=0,
            raw_text='Server requirements',
        )
        TenderDocumentChunk.objects.create(
            tender_lot=self.server,
            file_name='requirements.txt',
            chunk_index=1,
            raw_text='Network requirements',
        )

        with CaptureQueriesContext(connection) as queries:
            response = self.client.get('/api/v1/tenders/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        server_result = next(
            item for item in response.data['results']
            if item['id'] == str(self.server.id)
        )
        self.assertEqual(server_result['chunks_count'], 2)
        self.assertLessEqual(len(queries), 3)


class TenderSearchBenchmarkTests(TenderFactoryMixin, APITestCase):
    def test_sqlite_contract_smoke_benchmark(self):
        self.create_tender('BENCH-001', title='Benchmark server lot')
        stdout = io.StringIO()

        call_command(
            'benchmark_tender_search',
            query='server',
            iterations=2,
            warmup=1,
            limit=20,
            allow_sqlite=True,
            stdout=stdout,
        )

        report = json.loads(stdout.getvalue().strip().splitlines()[-1])
        self.assertEqual(report['database_vendor'], connection.vendor)
        self.assertEqual(report['result_count'], 1)
        self.assertEqual(report['iterations'], 2)

    @override_settings(APP_ENV='test')
    def test_benchmark_seeder_is_deterministic_and_scoped(self):
        call_command(
            'seed_tender_search_benchmark',
            count=10,
            batch_size=4,
            reset=True,
            stdout=io.StringIO(),
        )

        rows = TenderLot.objects.filter(
            lot_number__startswith='BENCH-SEARCH-',
        )
        self.assertEqual(rows.count(), 10)
        self.assertEqual(
            rows.filter(title__icontains='specialized server').count(),
            1,
        )


class ScraperIngestionTests(APITestCase):
    def test_scraper_skips_duplicate_payload_hashes(self):
        source = TenderSource.objects.get(code=TenderLot.PlatformSource.XARID_UZEX)
        now = timezone.now()
        payload = {
            'tender_id': 'PORTAL-001',
            'title': 'Portal server tender',
            'organization_name': 'Digital Ministry',
            'total_amount': '1000000.00',
            'category': 'IT',
            'published_at': now.isoformat(),
            'deadline_at': (now + timedelta(days=5)).isoformat(),
        }
        adapter = StaticAdapter(source.code, [payload, dict(payload)])
        scraper = UzExScraper(adapter=adapter, source_code=source.code)

        processed = scraper.fetch_latest_tenders(limit=10)

        self.assertEqual(processed, 1)
        self.assertEqual(TenderDocument.objects.count(), 1)
        self.assertEqual(TenderLot.objects.filter(external_id='PORTAL-001').count(), 1)
        run = ScrapeRun.objects.get()
        self.assertEqual(run.status, ScrapeRun.Status.SUCCESS)
        self.assertEqual(run.processed_count, 1)

    def test_scraper_retries_transient_portal_failure(self):
        source = TenderSource.objects.get(code=TenderLot.PlatformSource.XARID_UZEX)
        now = timezone.now()
        payload = {
            'tender_id': 'PORTAL-RETRY-001',
            'title': 'Retry tender',
            'organization_name': 'Digital Ministry',
            'total_amount': '2000000.00',
            'category': 'IT',
            'published_at': now.isoformat(),
            'deadline_at': (now + timedelta(days=5)).isoformat(),
        }
        adapter = FlakyAdapter(source.code, [payload])
        with override_settings(SCRAPER_RETRY_BASE_SECONDS=0):
            processed = UzExScraper(
                adapter=adapter,
                source_code=source.code,
            ).fetch_latest_tenders(limit=10)

        self.assertEqual(processed, 1)
        self.assertEqual(adapter.calls, 2)


class TenderNotificationQuotaTests(APITestCase):
    def setUp(self):
        self.source = TenderSource.objects.get(
            code=TenderLot.PlatformSource.XARID_UZEX,
        )
        self.now = timezone.now()

    def create_company_subscription(self, *, plan_code, phone_number, answers=None):
        user = CustomUser.objects.create_user(phone_number=phone_number)
        company = CompanyProfile.objects.create(
            user=user,
            company_name=f'{plan_code.title()} Notify MChJ',
            company_type=CompanyProfile.CompanyType.MCHJ,
            industry='IT',
            onboarding_answers=answers or {},
        )
        subscription = activate_subscription(
            company,
            SubscriptionPlan.objects.get(code=plan_code),
            period_start=self.now,
            period_end=self.now + timedelta(days=30),
        )
        return user, company, subscription

    def create_tender_document(self):
        lot = TenderLot.objects.create(
            source=self.source,
            external_id='SMS-PORTAL-001',
            lot_number='SMS-PORTAL-001',
            platform_source=self.source.code,
            title='Server infrastructure tender',
            buyer_name='Digital Ministry',
            start_price=Decimal('1000000.00'),
            category='IT',
            posted_date=self.now,
            deadline=self.now + timedelta(days=5),
            status=TenderLot.Status.ACTIVE,
        )
        return TenderDocument.objects.create(
            source=self.source,
            tender_id='SMS-PORTAL-001',
            tender_lot=lot,
            title=lot.title,
            organization_name=lot.buyer_name,
            total_amount=lot.start_price,
            category=lot.category,
            published_at=lot.posted_date,
            deadline_at=lot.deadline,
            raw_payload={'title': lot.title},
            hash_sum='a' * 64,
        )

    @patch('tenders.tasks.send_sms_message')
    def test_free_user_never_triggers_sms_task(self, sms_mock):
        self.create_company_subscription(
            plan_code='free',
            phone_number='+998901119001',
            answers={'keyword_alerts': ['server']},
        )
        tender = self.create_tender_document()

        scheduled = match_tender_document_task(str(tender.id))

        self.assertEqual(scheduled, 0)
        sms_mock.assert_not_called()
        self.assertFalse(NotificationLog.objects.exists())

    @patch('tenders.tasks.send_sms_message', return_value=(True, 'eskiz-001'))
    def test_pro_user_is_throttled_on_sixth_same_day_sms(self, sms_mock):
        user, _company, subscription = self.create_company_subscription(
            plan_code='pro',
            phone_number='+998901119002',
            answers={'keyword_alerts': ['server']},
        )
        tender = self.create_tender_document()

        results = [
            dispatch_matching_lot_sms_task(
                str(subscription.id),
                str(user.id),
                str(tender.id),
            )
            for _ in range(6)
        ]

        subscription.refresh_from_db()
        self.assertEqual(results[:5], ['queued'] * 5)
        self.assertEqual(results[5], 'daily_throttled')
        for notification_id in NotificationLog.objects.filter(
            user=user,
            status=NotificationLog.Status.PENDING,
        ).values_list('id', flat=True):
            deliver_matching_lot_sms_task(str(notification_id))

        subscription.refresh_from_db()
        self.assertEqual(subscription.sms_sent_this_month, 5)
        self.assertEqual(sms_mock.call_count, 5)
        self.assertEqual(
            NotificationLog.objects.filter(
                user=user,
                status=NotificationLog.Status.DELIVERED,
            ).count(),
            5,
        )
        self.assertEqual(
            NotificationLog.objects.filter(
                user=user,
                status=NotificationLog.Status.THROTTLED,
            ).count(),
            1,
        )


class StaticAdapter:
    def __init__(self, source_code, payloads):
        self.source_code = source_code
        self.payloads = payloads

    def fetch_latest(self, *, limit=100):
        return self.payloads[:limit]

    def normalize(self, payload):
        return NormalizedTenderPayload(
            tender_id=payload['tender_id'],
            title=payload['title'],
            organization_name=payload['organization_name'],
            total_amount=Decimal(payload['total_amount']),
            category=payload['category'],
            published_at=datetime.fromisoformat(payload['published_at']),
            deadline_at=datetime.fromisoformat(payload['deadline_at']),
            raw_payload=payload,
        )


class FlakyAdapter(StaticAdapter):
    def __init__(self, source_code, payloads):
        super().__init__(source_code, payloads)
        self.calls = 0

    def fetch_latest(self, *, limit=100):
        self.calls += 1
        if self.calls == 1:
            raise PortalAdapterError('timeout')
        return super().fetch_latest(limit=limit)


@skipUnless(
    connection.vendor == 'postgresql',
    'PostgreSQL search infrastructure test.',
)
class PostgreSQLSearchInfrastructureTests(APITestCase):
    def test_pg_trgm_and_functional_gin_indexes_exist(self):
        expected = {
            'tender_title_upper_trgm_gin',
            'tender_buyer_upper_trgm_gin',
            'tender_lot_no_upper_trgm_gin',
            'tender_category_upper_trgm_gin',
        }
        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT EXISTS ('
                'SELECT 1 FROM pg_extension WHERE extname = %s'
                ')',
                ['pg_trgm'],
            )
            extension_exists = cursor.fetchone()[0]
            cursor.execute(
                'SELECT indexname, indexdef FROM pg_indexes '
                'WHERE tablename = %s AND indexname = ANY(%s)',
                ['tender_lots', list(expected)],
            )
            indexes = dict(cursor.fetchall())

        self.assertTrue(extension_exists)
        self.assertSetEqual(set(indexes), expected)
        for definition in indexes.values():
            self.assertIn('USING gin', definition)
            self.assertIn('gin_trgm_ops', definition)
            self.assertIn('upper(', definition.lower())
