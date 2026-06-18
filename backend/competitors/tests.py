from datetime import timedelta
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from companies.models import CompanyProfile
from competitors.models import (
    CompetitorAnalytics,
    CompetitorDataQualityIssue,
    TenderAward,
    TenderBid,
    TenderParticipant,
)
from competitors.services.aggregation import aggregate_competitors
from competitors.services.identity import (
    build_identity_key,
    normalize_category,
    normalize_competitor_name,
)
from subscriptions.models import SubscriptionPlan, UsageRecord
from subscriptions.services.billing import activate_subscription
from tenders.models import TenderLot, TenderSource
from users.models import CustomUser


class CompetitorDataMixin:
    category = 'IT Services'
    alpha_stir = '301111111'
    beta_stir = '302222222'

    def create_lot(
        self,
        lot_number,
        *,
        category=None,
        start_price='1000.00',
        status_value=TenderLot.Status.COMPLETED,
    ):
        now = timezone.now()
        return TenderLot.objects.create(
            source=TenderSource.objects.get(
                code=TenderLot.PlatformSource.XARID_UZEX,
            ),
            external_id=lot_number,
            lot_number=lot_number,
            platform_source=TenderLot.PlatformSource.XARID_UZEX,
            title=f'Tender {lot_number}',
            buyer_name='Public Buyer',
            start_price=start_price,
            category=category or self.category,
            posted_date=now - timedelta(days=10),
            deadline=now - timedelta(days=5),
            status=status_value,
        )

    def create_result(
        self,
        lot_number,
        *,
        winner='alpha',
        alpha_bid='800.00',
        beta_bid='900.00',
        category=None,
        start_price='1000.00',
        winning_bid=True,
        verified=True,
        status_value=TenderLot.Status.COMPLETED,
        days_ago=1,
    ):
        lot = self.create_lot(
            lot_number,
            category=category,
            start_price=start_price,
            status_value=status_value,
        )
        alpha = TenderParticipant.objects.create(
            tender_lot=lot,
            source_name='  Alpha   Systems MChJ  ',
            stir=self.alpha_stir,
            source_reference=f'{lot_number}:alpha',
        )
        beta = TenderParticipant.objects.create(
            tender_lot=lot,
            source_name='Beta Solutions MChJ',
            stir=self.beta_stir,
            source_reference=f'{lot_number}:beta',
        )
        alpha_offer = TenderBid.objects.create(
            participant=alpha,
            sequence=1,
            amount=alpha_bid,
            currency='uzs',
        )
        beta_offer = TenderBid.objects.create(
            participant=beta,
            sequence=1,
            amount=beta_bid,
            currency='UZS',
        )
        winner_participant = alpha if winner == 'alpha' else beta
        winner_offer = alpha_offer if winner == 'alpha' else beta_offer
        award = TenderAward.objects.create(
            tender_lot=lot,
            winner=winner_participant,
            winning_bid=winner_offer if winning_bid else None,
            awarded_at=timezone.now() - timedelta(days=days_ago),
            is_verified=verified,
            source_url=f'https://example.test/results/{lot_number}',
        )
        return lot, alpha, beta, alpha_offer, beta_offer, award

    def create_baseline_results(self):
        first = self.create_result(
            'COMP-001',
            winner='alpha',
            alpha_bid='800.00',
            beta_bid='900.00',
            days_ago=20,
        )
        second = self.create_result(
            'COMP-002',
            winner='alpha',
            alpha_bid='850.00',
            beta_bid='900.00',
            days_ago=10,
        )
        third = self.create_result(
            'COMP-003',
            winner='beta',
            alpha_bid='900.00',
            beta_bid='700.00',
            days_ago=2,
        )
        return first, second, third

    def aggregate_category(self, category=None, days=365):
        period_end = timezone.localdate()
        period_start = period_end - timedelta(days=days - 1)
        snapshots = aggregate_competitors(
            scope_type=CompetitorAnalytics.Scope.CATEGORY,
            category=category or self.category,
            period_start=period_start,
            period_end=period_end,
        )
        return period_start, period_end, snapshots


class CompetitorIdentityAndModelTests(CompetitorDataMixin, TestCase):
    def test_identity_normalization_is_stable(self):
        name = normalize_competitor_name('  Alpha\u00a0 Systems   MChJ ')

        self.assertEqual(name, 'Alpha Systems MChJ')
        self.assertEqual(
            build_identity_key(name, self.alpha_stir),
            f'stir:{self.alpha_stir}',
        )
        self.assertEqual(normalize_category('  IT   SERVICES '), 'it services')

    def test_participant_derives_normalized_identity(self):
        lot = self.create_lot('IDENTITY-001')

        participant = TenderParticipant.objects.create(
            tender_lot=lot,
            source_name='  Alpha   Systems MChJ ',
            stir=self.alpha_stir,
        )

        self.assertEqual(participant.normalized_name, 'Alpha Systems MChJ')
        self.assertEqual(participant.identity_key, f'stir:{self.alpha_stir}')

    def test_award_rejects_winner_from_another_lot(self):
        first = self.create_result('INTEGRITY-001')
        second_lot = self.create_lot('INTEGRITY-002')

        with self.assertRaises(ValidationError):
            TenderAward.objects.create(
                tender_lot=second_lot,
                winner=first[1],
                winning_bid=first[3],
                awarded_at=timezone.now(),
                is_verified=True,
            )

    def test_database_rejects_zero_rank_and_source_count(self):
        today = timezone.localdate()
        with self.assertRaises(IntegrityError), transaction.atomic():
            CompetitorAnalytics.objects.create(
                scope_type=CompetitorAnalytics.Scope.CATEGORY,
                category='it',
                identity_key='stir:123456789',
                competitor_name='Invalid Analytics',
                period_start=today,
                period_end=today,
                rank=0,
                total_participations=1,
                total_wins=0,
                win_rate=0,
                average_bid_amount=0,
                average_discount_percentage=0,
                source_count=0,
                calculated_at=timezone.now(),
            )


class CompetitorAggregationTests(CompetitorDataMixin, TestCase):
    def test_ranking_metrics_traceability_and_idempotency(self):
        self.create_baseline_results()

        period_start, period_end, first_run = self.aggregate_category(
            category='  IT SERVICES ',
        )
        first_ids = {snapshot.identity_key: snapshot.id for snapshot in first_run}
        _, _, second_run = self.aggregate_category(category='it services')

        self.assertEqual(len(first_run), 2)
        self.assertEqual(
            first_ids,
            {snapshot.identity_key: snapshot.id for snapshot in second_run},
        )
        alpha = CompetitorAnalytics.objects.get(
            scope_type=CompetitorAnalytics.Scope.CATEGORY,
            category='it services',
            competitor_stir=self.alpha_stir,
            period_start=period_start,
            period_end=period_end,
        )
        beta = CompetitorAnalytics.objects.get(
            competitor_stir=self.beta_stir,
            period_start=period_start,
            period_end=period_end,
        )
        self.assertEqual(alpha.rank, 1)
        self.assertEqual(alpha.total_participations, 3)
        self.assertEqual(alpha.total_wins, 2)
        self.assertEqual(alpha.win_rate, Decimal('66.67'))
        self.assertEqual(alpha.average_bid_amount, Decimal('850.00'))
        self.assertEqual(
            alpha.average_discount_percentage,
            Decimal('17.50'),
        )
        self.assertEqual(alpha.source_count, 3)
        self.assertEqual(alpha.sources.count(), 3)
        self.assertEqual(beta.rank, 2)
        self.assertEqual(beta.total_wins, 1)
        self.assertEqual(
            beta.average_discount_percentage,
            Decimal('30.00'),
        )
        self.assertEqual(
            alpha.raw_metrics['ranking_formula_version'],
            'v1',
        )

    def test_invalid_discount_is_logged_excluded_and_then_resolved(self):
        result = self.create_result(
            'QUALITY-001',
            winner='alpha',
            alpha_bid='1100.00',
        )

        _, _, snapshots = self.aggregate_category()

        self.assertEqual(snapshots, [])
        issue = CompetitorDataQualityIssue.objects.get(
            code='invalid_winning_discount',
        )
        self.assertIsNone(issue.resolved_at)

        result[3].amount = Decimal('700.00')
        result[3].save(update_fields=['amount'])
        _, _, snapshots = self.aggregate_category()

        issue.refresh_from_db()
        self.assertIsNotNone(issue.resolved_at)
        self.assertEqual(len(snapshots), 2)

    def test_invalid_start_price_and_missing_winning_bid_are_logged(self):
        self.create_result(
            'QUALITY-START',
            start_price='0.00',
            alpha_bid='0.00',
        )
        self.create_result('QUALITY-BID', winning_bid=False)

        self.aggregate_category()

        self.assertSetEqual(
            set(CompetitorDataQualityIssue.objects.values_list(
                'code',
                flat=True,
            )),
            {'invalid_start_price', 'missing_winning_bid'},
        )
        self.assertFalse(CompetitorAnalytics.objects.exists())

    def test_lot_scope_excludes_the_target_lot_from_its_sources(self):
        baseline = self.create_baseline_results()
        target_lot = baseline[0][0]
        period_end = timezone.localdate()
        period_start = period_end - timedelta(days=364)

        snapshots = aggregate_competitors(
            scope_type=CompetitorAnalytics.Scope.LOT,
            category=target_lot.category,
            tender_lot=target_lot,
            period_start=period_start,
            period_end=period_end,
        )

        alpha = next(
            item for item in snapshots
            if item.competitor_stir == self.alpha_stir
        )
        self.assertEqual(alpha.source_count, 2)
        self.assertNotIn(
            target_lot.id,
            set(alpha.sources.values_list('award__tender_lot_id', flat=True)),
        )


@override_settings(COMPETITOR_MIN_SAMPLE_SIZE=3)
class CompetitorApiTests(CompetitorDataMixin, APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            phone_number='+998901113301',
        )
        self.company = CompanyProfile.objects.create(
            user=self.user,
            company_name='Competitor Client MChJ',
            company_type=CompanyProfile.CompanyType.MCHJ,
            industry='IT',
        )
        now = timezone.now()
        activate_subscription(
            self.company,
            SubscriptionPlan.objects.get(code='business'),
            period_start=now,
            period_end=now + timedelta(days=30),
        )
        self.client.force_authenticate(self.user)
        self.baseline = self.create_baseline_results()
        self.period_start, self.period_end, _ = self.aggregate_category()
        self.target_lot = self.create_lot(
            'TARGET-001',
            status_value=TenderLot.Status.ACTIVE,
        )
        aggregate_competitors(
            scope_type=CompetitorAnalytics.Scope.LOT,
            category=self.target_lot.category,
            tender_lot=self.target_lot,
            period_start=self.period_start,
            period_end=self.period_end,
        )

    def test_category_top_returns_rank_sample_freshness_and_usage(self):
        response = self.client.get(
            '/api/v1/competitors/top/',
            {'category': ' IT SERVICES ', 'period': '365d'},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'ready')
        self.assertEqual(response.data['source_lot_count'], 3)
        self.assertEqual(response.data['results'][0]['rank'], 1)
        self.assertEqual(response.data['results'][0]['source_count'], 3)
        self.assertIsNotNone(response.data['calculated_at'])
        usage = UsageRecord.objects.get(
            company=self.company,
            metric=UsageRecord.Metric.COMPETITOR_QUERY,
        )
        self.assertEqual(usage.used, 1)

    def test_lot_scope_and_history_endpoints(self):
        lot_response = self.client.get(
            '/api/v1/competitors/top/',
            {'lot_id': self.target_lot.id, 'period': '365d'},
        )
        history_response = self.client.get(
            f'/api/v1/competitors/{self.alpha_stir}/history/',
            {'category': self.category},
        )

        self.assertEqual(lot_response.status_code, status.HTTP_200_OK)
        self.assertEqual(lot_response.data['scope']['type'], 'lot')
        self.assertEqual(lot_response.data['status'], 'ready')
        self.assertEqual(history_response.status_code, status.HTTP_200_OK)
        self.assertEqual(history_response.data['status'], 'ready')
        self.assertEqual(
            history_response.data['results'][0]['competitor_stir'],
            self.alpha_stir,
        )

    def test_insufficient_data_has_explicit_state(self):
        self.create_result(
            'SMALL-001',
            category='Construction',
        )
        self.aggregate_category(category='Construction')

        response = self.client.get(
            '/api/v1/competitors/top/',
            {'category': 'construction', 'period': '365d'},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'insufficient_data')
        self.assertEqual(response.data['minimum_source_count'], 3)
        self.assertEqual(response.data['results'], [])

    def test_authentication_plan_and_company_ownership_are_enforced(self):
        self.client.force_authenticate(user=None)
        unauthenticated = self.client.get(
            '/api/v1/competitors/top/',
            {'category': self.category},
        )

        free_user = CustomUser.objects.create_user(
            phone_number='+998901113302',
        )
        other_company = CompanyProfile.objects.create(
            user=free_user,
            company_name='Free Client MChJ',
            company_type=CompanyProfile.CompanyType.MCHJ,
            industry='IT',
        )
        self.client.force_authenticate(free_user)
        free_response = self.client.get(
            '/api/v1/competitors/top/',
            {'category': self.category},
        )
        ownership_response = self.client.get(
            '/api/v1/competitors/freshness/',
            {'company_id': self.company.id},
        )

        self.assertEqual(
            unauthenticated.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
        self.assertEqual(free_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            free_response.data['code'],
            'feature_not_available',
        )
        self.assertEqual(
            ownership_response.status_code,
            status.HTTP_404_NOT_FOUND,
        )
        self.assertEqual(other_company.current_tariff, 'free')

    @override_settings(COMPETITOR_FRESHNESS_SECONDS=60)
    def test_freshness_reports_stale_data_and_quality_issue_count(self):
        CompetitorAnalytics.objects.update(
            calculated_at=timezone.now() - timedelta(hours=2),
        )
        invalid = self.create_result(
            'STALE-QUALITY',
            alpha_bid='1200.00',
        )
        self.aggregate_category()
        CompetitorAnalytics.objects.update(
            calculated_at=timezone.now() - timedelta(hours=2),
        )
        self.assertIsNotNone(invalid)

        response = self.client.get('/api/v1/competitors/freshness/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'stale')
        self.assertGreaterEqual(response.data['open_data_quality_issues'], 1)

    def test_invalid_query_does_not_consume_usage(self):
        response = self.client.get('/api/v1/competitors/top/')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(
            UsageRecord.objects.filter(
                company=self.company,
                metric=UsageRecord.Metric.COMPETITOR_QUERY,
            ).exists()
        )

    def test_manual_competitor_crud_is_not_exposed(self):
        response = self.client.post(
            '/api/v1/competitors/',
            {'name': 'Manual competitor'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
