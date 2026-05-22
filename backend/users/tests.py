from django.core.cache import cache
from rest_framework import status
from rest_framework.test import APITestCase

from .models import CustomUser


class AuthFlowTests(APITestCase):
    def setUp(self):
        cache.clear()
        CustomUser.objects.all().delete()

    def test_phone_otp_flow_returns_tokens_and_profile(self):
        phone = '+998901112233'

        response = self.client.post('/api/v1/auth/send-otp/', {'phone_number': phone}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        otp = cache.get('tenderhelper:otp:998901112233')
        self.assertIsNotNone(otp)

        response = self.client.post(
            '/api/v1/auth/verify-otp/',
            {'phone_number': phone, 'otp': otp},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data['tokens'])
        self.assertTrue(response.data['is_new_user'])

        token = response.data['tokens']['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get('/api/v1/auth/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['phone_number'], phone)
