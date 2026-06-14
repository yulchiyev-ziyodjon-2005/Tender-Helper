from rest_framework import status
from rest_framework.test import APITestCase

from users.models import CustomUser


class ManualTenderSecurityTests(APITestCase):
    payload = {
        'title': 'Manual tender',
        'tender_text': 'Tender talablari',
        'buyer_name': 'Buyurtmachi',
    }

    def test_manual_tender_requires_authentication(self):
        response = self.client.post('/api/v1/tenders/manual/', self.payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_manual_tender_records_owner(self):
        user = CustomUser.objects.create_user(phone_number='+998901110011')
        self.client.force_authenticate(user)

        response = self.client.post('/api/v1/tenders/manual/', self.payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(str(user.manual_tenders.get().id), response.data['id'])
