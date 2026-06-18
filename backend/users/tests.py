from datetime import timedelta
from django.core.cache import cache
from django.core import signing
from django.core import mail
from django.db import IntegrityError, transaction
from django.test import override_settings
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import Mock, patch
from urllib.parse import parse_qs, urlparse

from companies.models import CompanyProfile
from subscriptions.models import SubscriptionPlan
from subscriptions.services.billing import activate_subscription
from teams.models import CompanyMember, TeamPermission
from .models import CustomUser


@override_settings(SMS_PROVIDER='console')
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

    def test_email_registration_requires_verified_phone(self):
        payload = {
            'email': 'verified@example.com',
            'password': 'StrongPassword123!',
            'full_name': 'Verified User',
            'phone_number': '+998901112244',
            'company_name': 'Verified Company',
            'company_type': 'mchj',
            'industry': 'IT',
            'experience_level': 'beginner',
        }

        response = self.client.post('/api/v1/auth/register/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.client.post(
            '/api/v1/auth/send-otp/',
            {'phone_number': payload['phone_number']},
            format='json',
        )
        otp = cache.get('tenderhelper:otp:998901112244')
        verification = self.client.post(
            '/api/v1/auth/verify-phone/',
            {'phone_number': payload['phone_number'], 'otp': otp},
            format='json',
        )
        self.assertEqual(verification.status_code, status.HTTP_200_OK)

        payload['phone_verification_token'] = verification.data['verification_token']
        response = self.client.post('/api/v1/auth/register/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user']['phone_number'], payload['phone_number'])

    def test_phone_verification_token_cannot_be_used_for_another_number(self):
        phone = '+998901112255'
        self.client.post('/api/v1/auth/send-otp/', {'phone_number': phone}, format='json')
        otp = cache.get('tenderhelper:otp:998901112255')
        verification = self.client.post(
            '/api/v1/auth/verify-phone/',
            {'phone_number': phone, 'otp': otp},
            format='json',
        )
        response = self.client.post(
            '/api/v1/auth/register/',
            {
                'email': 'mismatch@example.com',
                'password': 'StrongPassword123!',
                'full_name': 'Mismatch User',
                'phone_number': '+998901112266',
                'phone_verification_token': verification.data['verification_token'],
                'company_name': 'Mismatch Company',
                'company_type': 'mchj',
                'industry': 'IT',
                'experience_level': 'beginner',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_password_reset_flow_changes_password_and_hides_unknown_email(self):
        user = CustomUser.objects.create_user(
            email='reset@example.com',
            password='OldStrongPassword123!',
        )
        response = self.client.post(
            '/api/v1/auth/forgot-password/',
            {'email': user.email},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)
        reset_url = mail.outbox[0].body.splitlines()[2]
        query = parse_qs(urlparse(reset_url).query)

        response = self.client.post(
            '/api/v1/auth/reset-password/',
            {
                'uid': query['uid'][0],
                'token': query['token'][0],
                'new_password': 'NewStrongPassword123!',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertTrue(user.check_password('NewStrongPassword123!'))

        unknown = self.client.post(
            '/api/v1/auth/forgot-password/',
            {'email': 'unknown@example.com'},
            format='json',
        )
        self.assertEqual(unknown.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)

    def test_database_requires_phone_or_email_identity(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            CustomUser.objects.create()

    def test_database_enforces_case_insensitive_email_uniqueness(self):
        CustomUser.objects.create_user(
            email='CaseSensitive@example.com',
            password='StrongPassword123!',
        )

        with self.assertRaises(IntegrityError), transaction.atomic():
            CustomUser.objects.create_user(
                email='casesensitive@example.com',
                password='StrongPassword123!',
            )

    @override_settings(
        SMS_PROVIDER='eskiz',
        ESKIZ_API_URL='https://notify.eskiz.uz/api',
        ESKIZ_EMAIL='sms@example.test',
        ESKIZ_SECRET_KEY='sms-secret',
        ESKIZ_TOKEN_CACHE_SECONDS=3600,
    )
    @patch('requests.post')
    def test_eskiz_sms_uses_cached_token(self, post_mock):
        auth_response = Mock()
        auth_response.status_code = 200
        auth_response.json.return_value = {'data': {'token': 'eskiz-token'}}
        sms_response = Mock()
        sms_response.status_code = 200
        sms_response.json.return_value = {'id': 'sms-001'}
        post_mock.side_effect = [auth_response, sms_response, sms_response]

        from users.services.otp_service import send_sms_message

        first = send_sms_message('+998901112277', 'Birinchi xabar')
        second = send_sms_message('+998901112277', 'Ikkinchi xabar')

        self.assertEqual(first, (True, 'sms-001'))
        self.assertEqual(second, (True, 'sms-001'))
        self.assertEqual(post_mock.call_count, 3)
        self.assertEqual(
            post_mock.call_args_list[0].args[0],
            'https://notify.eskiz.uz/api/auth/login',
        )
        self.assertEqual(
            post_mock.call_args_list[1].kwargs['headers']['Authorization'],
            'Bearer eskiz-token',
        )

    @override_settings(
        SMS_PROVIDER='eskiz',
        ESKIZ_API_URL='https://notify.eskiz.uz/api',
        ESKIZ_EMAIL='<eskiz-account-email>',
        ESKIZ_SECRET_KEY='<eskiz-account-secret-key>',
    )
    @patch('requests.post')
    def test_eskiz_sms_rejects_placeholder_credentials(self, post_mock):
        from users.services.otp_service import send_sms_message

        self.assertEqual(send_sms_message('+998901112288', 'Xabar'), (False, ''))
        post_mock.assert_not_called()

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

    def test_session_capabilities_require_authentication(self):
        response = self.client.get('/api/v1/auth/session/')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_session_capabilities_report_onboarding_blocker_without_company(self):
        user = CustomUser.objects.create_user(
            email='session.empty@example.com',
            password='StrongPassword123!',
        )
        self.client.force_authenticate(user)

        response = self.client.get('/api/v1/auth/session/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.data['active_company'])
        self.assertEqual(response.data['blockers'][0]['code'], 'profile_required')
        self.assertTrue(all(
            item['enabled'] is False
            and item['reason'] == 'profile_required'
            for item in response.data['navigation']
        ))

    def test_session_capabilities_expose_owner_navigation_usage_and_denials(self):
        user = CustomUser.objects.create_user(
            email='session.owner@example.com',
            password='StrongPassword123!',
        )
        company = CompanyProfile.objects.create(
            user=user,
            company_name='Owner Session MChJ',
            company_type=CompanyProfile.CompanyType.MCHJ,
            industry='IT',
        )
        self.client.force_authenticate(user)

        response = self.client.get('/api/v1/auth/session/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(str(response.data['active_company']['id']), str(company.id))
        self.assertEqual(response.data['membership']['role'], 'owner')
        self.assertIn(TeamPermission.MANAGE_TEAM, response.data['membership']['permissions'])
        navigation = {
            item['key']: item
            for item in response.data['navigation']
        }
        self.assertTrue(navigation['dashboard']['enabled'])
        self.assertTrue(navigation['analysis']['enabled'])
        self.assertFalse(navigation['documents']['enabled'])
        self.assertEqual(navigation['documents']['reason'], 'feature_not_available')
        self.assertEqual(navigation['telegram']['reason'], 'planned_later')
        self.assertEqual(response.data['usage']['ai_analysis']['limit'], 4)

    def test_session_capabilities_are_company_scoped_for_member_roles(self):
        owner = CustomUser.objects.create_user(
            email='session.company.owner@example.com',
            password='StrongPassword123!',
        )
        employee = CustomUser.objects.create_user(
            email='session.analyst@example.com',
            password='StrongPassword123!',
        )
        company = CompanyProfile.objects.create(
            user=owner,
            company_name='Business Session MChJ',
            company_type=CompanyProfile.CompanyType.MCHJ,
            industry='IT',
            stir='309123999',
        )
        now = timezone.now()
        activate_subscription(
            company,
            SubscriptionPlan.objects.get(code='business'),
            period_start=now,
            period_end=now + timedelta(days=30),
        )
        CompanyMember.objects.create(
            company=company,
            user=employee,
            role=CompanyMember.Role.ANALYST,
        )
        self.client.force_authenticate(employee)

        response = self.client.get(
            '/api/v1/auth/session/',
            {'company_id': str(company.id)},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['subscription']['plan'], 'business')
        self.assertEqual(response.data['membership']['role'], 'analyst')
        navigation = {
            item['key']: item
            for item in response.data['navigation']
        }
        self.assertTrue(navigation['competitors']['enabled'])
        self.assertFalse(navigation['documents']['enabled'])
        self.assertEqual(navigation['documents']['reason'], 'company_role_denied')
        self.assertFalse(navigation['team']['enabled'])
        self.assertIn(
            response.data['actions']['manage_team']['reason'],
            {'permission_denied', 'company_role_denied'},
        )
