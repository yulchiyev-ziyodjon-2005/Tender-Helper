from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

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

    def test_analysis_start_and_calculate_flow(self):
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
