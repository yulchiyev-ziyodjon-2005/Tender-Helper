from django.core.cache import cache
from django.core import signing
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

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

    @patch('users.views.verify_google_token')
    def test_google_auth_flow_returns_tokens(self, mock_verify_google_token):
        mock_verify_google_token.return_value = {
            'email': 'google.user@example.com',
            'name': 'Google User',
            'picture': '',
            'google_id': 'google-user-id',
        }

        response = self.client.post('/api/v1/auth/google/', {'token': 'valid-id-token'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data['tokens'])
        self.assertTrue(response.data['is_new_user'])
        self.assertEqual(response.data['user']['email'], 'google.user@example.com')
        self.assertEqual(response.data['user']['auth_provider'], 'google')

    @override_settings(
        GOOGLE_CLIENT_ID='1234567890-test.apps.googleusercontent.com',
        GOOGLE_CLIENT_SECRET='test-secret',
        FRONTEND_BASE_URL='http://localhost:5173',
    )
    def test_google_oauth_start_redirects_to_google_account_chooser(self):
        response = self.client.get('/api/v1/auth/google/start/?next=/dashboard')

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        location = response['Location']
        self.assertTrue(location.startswith('https://accounts.google.com/o/oauth2/v2/auth'))
        params = parse_qs(urlparse(location).query)
        self.assertEqual(params['client_id'][0], '1234567890-test.apps.googleusercontent.com')
        self.assertEqual(params['prompt'][0], 'select_account')
        self.assertEqual(params['response_type'][0], 'code')

    @override_settings(
        GOOGLE_CLIENT_ID='1234567890-test.apps.googleusercontent.com',
        GOOGLE_CLIENT_SECRET='test-secret',
    )
    def test_google_oauth_config_reports_enabled(self):
        response = self.client.get('/api/v1/auth/google/config/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['enabled'])

    @override_settings(
        GOOGLE_CLIENT_ID='1234567890-test.apps.googleusercontent.com',
        GOOGLE_CLIENT_SECRET='test-secret',
        FRONTEND_BASE_URL='http://localhost:5173',
    )
    @patch('users.views.exchange_code_for_user_info')
    def test_google_oauth_callback_uses_one_time_exchange_code(self, mock_exchange_code):
        mock_exchange_code.return_value = {
            'email': 'redirect.user@example.com',
            'name': 'Redirect User',
            'picture': '',
            'google_id': 'redirect-user-id',
        }
        state = signing.dumps({'next': '/dashboard'}, salt='google-oauth-state')

        response = self.client.get('/api/v1/auth/google/callback/', {'code': 'auth-code', 'state': state})

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        location = response['Location']
        self.assertTrue(location.startswith('http://localhost:5173/auth/google/callback'))
        params = parse_qs(urlparse(location).query)
        self.assertIn('code', params)
        self.assertNotIn('access', params)
        self.assertNotIn('refresh', params)

        response = self.client.post(
            '/api/v1/auth/google/exchange/',
            {'code': params['code'][0]},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data['tokens'])
        self.assertTrue(response.data['is_new_user'])

        replay = self.client.post(
            '/api/v1/auth/google/exchange/',
            {'code': params['code'][0]},
            format='json',
        )
        self.assertEqual(replay.status_code, status.HTTP_400_BAD_REQUEST)
