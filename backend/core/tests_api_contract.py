from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase
from rest_framework.test import APIClient

from companies.models import CompanyProfile


class FrontendApiContractTests(TestCase):
    """Smoke-test the API surface consumed by the React frontend."""

    def setUp(self):
        cache.clear()
        self.client = APIClient()

    def tearDown(self):
        cache.clear()

    def test_public_contracts_match_frontend_bootstrap(self):
        health = self.client.get('/api/health/')
        self.assertEqual(health.status_code, 200)
        self.assertEqual(health.data['status'], 'ok')

        tenders = self.client.get('/api/v1/tenders/')
        self.assertEqual(tenders.status_code, 200)
        self.assertIn('results', tenders.data)
        self.assertIsInstance(tenders.data['results'], list)

        google = self.client.get('/api/v1/auth/google/config/')
        self.assertEqual(google.status_code, 200)
        self.assertIsInstance(google.data['enabled'], bool)
        self.assertIn('start_url', google.data)

    def test_auth_guard_contract_uses_typed_error_envelope(self):
        protected_paths = [
            '/api/v1/auth/me/',
            '/api/v1/auth/session/',
            '/api/v1/companies/profile/',
            '/api/v1/subscriptions/entitlements/',
            '/api/v1/teams/workspace/',
            '/api/v1/admin/overview/',
        ]
        for path in protected_paths:
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 401)
                self.assert_error_contract(response.data)

        invalid_login = self.client.post(
            '/api/v1/auth/login/',
            {
                'email': 'missing@example.invalid',
                'password': 'not-a-real-password',
            },
            format='json',
        )
        self.assertIn(invalid_login.status_code, {400, 401})
        self.assert_error_contract(invalid_login.data)

    def test_authenticated_frontend_bootstrap_contracts(self):
        user = get_user_model().objects.create_user(
            email='contract-user@example.uz',
            password='Str0ng-contract-pass!',
            full_name='Contract User',
            auth_provider='email',
        )
        CompanyProfile.objects.create(
            user=user,
            company_name='Contract MChJ',
            company_type=CompanyProfile.CompanyType.MCHJ,
            industry='it',
            experience_level=CompanyProfile.ExperienceLevel.BEGINNER,
            stir='123456789',
            registry_status=CompanyProfile.RegistryStatus.MANUAL,
        )

        login = self.client.post(
            '/api/v1/auth/login/',
            {
                'email': 'contract-user@example.uz',
                'password': 'Str0ng-contract-pass!',
            },
            format='json',
        )
        self.assertEqual(login.status_code, 200)
        self.assertIn('tokens', login.data)
        self.assertIn('access', login.data['tokens'])
        self.assertIn('refresh', login.data['tokens'])
        self.assertIn('user', login.data)
        self.assertIsInstance(login.data['force_password_change'], bool)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['tokens']['access']}")

        session = self.client.get('/api/v1/auth/session/')
        self.assertEqual(session.status_code, 200)
        self.assertIn('user', session.data)
        self.assertIn('active_company', session.data)
        self.assertIn('membership', session.data)
        self.assertIn('navigation', session.data)

        profile = self.client.get('/api/v1/companies/profile/')
        self.assertEqual(profile.status_code, 200)
        self.assertEqual(profile.data['company_name'], 'Contract MChJ')
        self.assertIn('feature_access', profile.data)

        entitlements = self.client.get('/api/v1/subscriptions/entitlements/')
        self.assertEqual(entitlements.status_code, 200)
        self.assertEqual(entitlements.data['plan'], 'free')
        self.assertIsInstance(entitlements.data['entitlements'], list)

        team = self.client.get('/api/v1/teams/workspace/')
        self.assertEqual(team.status_code, 200)
        self.assertEqual(team.data['company']['name'], 'Contract MChJ')
        self.assertEqual(team.data['membership']['role'], 'owner')

        admin = self.client.get('/api/v1/admin/overview/')
        self.assertEqual(admin.status_code, 403)
        self.assert_error_contract(admin.data)

    def assert_error_contract(self, data):
        self.assertIsInstance(data, dict)
        self.assertTrue(data.get('code') or data.get('error_code') or data.get('error'))
        self.assertTrue(data.get('message') or data.get('detail'))
