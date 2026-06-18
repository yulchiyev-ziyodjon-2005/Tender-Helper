from datetime import date

from django.db import IntegrityError, transaction
from django.test import override_settings
from django.utils import timezone
from requests import RequestException
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import Mock, patch

from analysis.models import (
    AITenderAnalysis,
    AnalysisFinding,
    AnalysisRun,
    LegalKnowledgeDocument,
    LegalKnowledgeSource,
    ModelInvocation,
)
from analysis.services.legal_sources import is_allowed_legal_source_url
from companies.models import CompanyProfile
from subscriptions.models import UsageRecord
from tenders.models import TenderDocumentChunk, TenderLot, TenderSource
from users.models import CustomUser


@override_settings(
    CELERY_TASK_ALWAYS_EAGER=True,
    CELERY_TASK_EAGER_PROPAGATES=False,
    CELERY_BROKER_URL='memory://',
    CELERY_RESULT_BACKEND='cache+memory://',
)
class AnalysisFlowTests(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(phone_number='+998901114455')
        self.client.force_authenticate(self.user)
        self.company = CompanyProfile.objects.create(
            user=self.user,
            company_name='Test MChJ',
            company_type='mchj',
            industry='it',
            experience_level='beginner',
        )
        self.tender = TenderLot.objects.create(
            source=TenderSource.objects.get(code='manual'),
            external_id='',
            lot_number='TEST-001',
            platform_source='manual',
            title='Server uskunalarini yetkazib berish',
            buyer_name='Test Buyurtmachi',
            start_price=100000000,
            region='Toshkent shahri',
            category='it',
            posted_date=timezone.now(),
            deadline=timezone.now() + timezone.timedelta(days=5),
        )
        TenderDocumentChunk.objects.create(
            tender_lot=self.tender,
            file_name='manual.txt',
            chunk_index=0,
            raw_text='ISO talabi mavjud. Jarima shartlari bor. Faqat bitta brend.',
        )

    @override_settings(GEMINI_API_KEY='test-key')
    @patch('analysis.providers.gemini.requests.Session.post')
    def test_analysis_start_and_calculate_flow(self, mock_post):
        provider_response = Mock()
        provider_response.raise_for_status.return_value = None
        provider_response.json.return_value = {
            'candidates': [{
                'content': {
                    'parts': [{
                        'text': (
                            '{"eligibility_score": 81, "summary_text": "Mos", '
                            '"missing_documents": [], "red_flags": [{"level": "warning", '
                            '"title": "Muddat", "reason": "Qisqa", "recommendation": "Tekshiring"}], '
                            '"standards": [], "requirements": [], "decision": {}}'
                        ),
                    }],
                },
            }],
        }
        mock_post.return_value = provider_response

        response = self.client.post('/api/v1/analysis/start/', {'lot_id': self.tender.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        run_id = response.data['id']
        analysis_id = response.data['analysis_id']

        status_response = self.client.get(f'/api/v1/analysis/{run_id}/status/')
        self.assertEqual(status_response.status_code, status.HTTP_200_OK)
        self.assertEqual(status_response.data['status'], AnalysisRun.Status.SUCCESS)
        self.assertEqual(status_response.data['analysis_status'], 'completed')
        self.assertGreater(status_response.data['eligibility_score'], 0)

        result_response = self.client.get(f'/api/v1/analysis/{run_id}/result/')
        self.assertEqual(result_response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(result_response.data['red_flags']), 1)
        self.assertEqual(AnalysisFinding.objects.filter(run_id=run_id).count(), 1)
        self.assertEqual(ModelInvocation.objects.filter(run_id=run_id).count(), 1)
        response = self.client.post(
            f'/api/v1/analysis/{analysis_id}/calculate/',
            {
                'raw_material_cost': '40000000',
                'logistics_cost': '5000000',
                'labor_cost': '7000000',
                'other_expenses': '3000000',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(float(response.data['min_safe_price']), 0)

    def test_analysis_endpoints_require_authentication(self):
        self.client.force_authenticate(user=None)
        response = self.client.post('/api/v1/analysis/start/', {'lot_id': self.tender.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @override_settings(GEMINI_API_KEY='test-key')
    @patch('analysis.providers.gemini.requests.Session.post')
    def test_provider_failure_marks_analysis_failed(self, mock_post):
        mock_post.side_effect = RequestException('provider unavailable')

        response = self.client.post('/api/v1/analysis/start/', {'lot_id': self.tender.id}, format='json')

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        status_response = self.client.get(
            f"/api/v1/analysis/{response.data['id']}/status/",
        )
        self.assertEqual(status_response.data['status'], AnalysisRun.Status.FAILED)
        self.assertEqual(status_response.data['analysis_status'], 'failed')
        self.assertEqual(status_response.data['eligibility_score'], 0)
        self.assertNotIn('92', status_response.data['error_message'])

    def test_user_cannot_select_another_users_company(self):
        other_user = CustomUser.objects.create_user(phone_number='+998901119999')
        other_company = CompanyProfile.objects.create(
            user=other_user,
            company_name='Other MChJ',
            company_type='mchj',
            industry='it',
        )

        response = self.client.post(
            '/api/v1/analysis/start/',
            {'lot_id': self.tender.id, 'company_id': other_company.id},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_database_rejects_score_above_one_hundred(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            AITenderAnalysis.objects.create(
                company=self.company,
                tender_lot=self.tender,
                eligibility_score=101,
            )

    @patch('analysis.views.run_analysis_task.delay')
    def test_fifth_free_analysis_is_rejected_by_atomic_quota(self, delay):
        for _ in range(4):
            response = self.client.post(
                '/api/v1/analysis/start/',
                {'lot_id': self.tender.id},
                format='json',
            )
            self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        response = self.client.post(
            '/api/v1/analysis/start/',
            {'lot_id': self.tender.id},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertEqual(response.data['error_code'], 'usage_limit_exceeded')
        self.assertEqual(response.data['details']['limit'], 4)
        self.assertEqual(
            AITenderAnalysis.objects.filter(company=self.company).count(),
            4,
        )
        self.assertEqual(
            UsageRecord.objects.get(
                company=self.company,
                metric=UsageRecord.Metric.AI_ANALYSIS,
            ).used,
            4,
        )
        self.assertEqual(delay.call_count, 4)

    def test_legal_sources_endpoint_exposes_only_active_official_sources_by_default(self):
        response = self.client.get('/api/v1/analysis/legal-sources/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        codes = {item['code'] for item in response.data}
        self.assertIn('lex_uz', codes)
        self.assertIn('gov_uz_procurement', codes)
        self.assertIn('public_procurement_portal', codes)
        self.assertNotIn('technical_standards_verified', codes)

        lex_source = next(item for item in response.data if item['code'] == 'lex_uz')
        self.assertEqual(lex_source['authority_level'], 'primary_normative')
        self.assertTrue(lex_source['requires_effective_date_check'])

    def test_legal_sources_can_include_inactive_manual_review_sources(self):
        response = self.client.get(
            '/api/v1/analysis/legal-sources/',
            {'include_inactive': 'true'},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        sources = {item['code']: item for item in response.data}
        self.assertFalse(sources['technical_standards_verified']['is_active'])
        self.assertTrue(sources['technical_standards_verified']['requires_manual_review'])

    def test_legal_source_url_allowlist_rejects_untrusted_and_non_https_urls(self):
        self.client.get('/api/v1/analysis/legal-sources/')

        self.assertTrue(is_allowed_legal_source_url('https://lex.uz/docs/5382974'))
        self.assertTrue(is_allowed_legal_source_url('https://gov.uz/oz/pages/davlat_xaridlari'))
        self.assertFalse(is_allowed_legal_source_url('http://lex.uz/docs/5382974'))
        self.assertFalse(is_allowed_legal_source_url('https://example.com/legal'))

    def test_legal_document_effective_period_is_validated_by_database(self):
        source = LegalKnowledgeSource.objects.get(code='lex_uz')

        with self.assertRaises(IntegrityError), transaction.atomic():
            LegalKnowledgeDocument.objects.create(
                source=source,
                external_id='lex-test',
                title='Invalid period',
                url='https://lex.uz/docs/5382974',
                version_label='invalid',
                effective_from=date(2026, 6, 1),
                effective_to=date(2026, 5, 1),
            )
