from django.utils import timezone
from requests import RequestException
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import Mock, patch

from companies.models import CompanyProfile
from tenders.models import TenderDocumentChunk, TenderLot
from users.models import CustomUser


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

    @patch('analysis.views.requests.Session.post')
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
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['analysis_status'], 'completed')
        self.assertGreater(response.data['eligibility_score'], 0)
        self.assertGreaterEqual(len(response.data['red_flags']), 1)

        analysis_id = response.data['id']
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

    @patch('analysis.views.requests.Session.post')
    def test_provider_failure_marks_analysis_failed(self, mock_post):
        mock_post.side_effect = RequestException('provider unavailable')

        response = self.client.post('/api/v1/analysis/start/', {'lot_id': self.tender.id}, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['analysis_status'], 'failed')
        self.assertEqual(response.data['eligibility_score'], 0)
        self.assertNotIn('92', response.data['error_message'])

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
