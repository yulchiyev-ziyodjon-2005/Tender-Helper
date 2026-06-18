from datetime import timedelta
from unittest.mock import Mock

import requests
from django.core.cache import cache
from django.core.checks import run_checks
from django.db import IntegrityError, transaction
from django.test import SimpleTestCase, override_settings
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.test import APITestCase

from companies.features import get_company_feature_access, require_company_stir
from companies.models import CompanyProfile, CompanyRegistryDraft
from companies.services.registry import (
    CompanyRegistryProvider,
    ConfiguredHttpRegistryProvider,
    RegistryCompanyData,
    RegistryInvalidResponseError,
    RegistryNotFoundError,
    RegistryProviderResult,
    RegistryUnavailableError,
    normalize_registry_payload,
)
from users.models import CustomUser


class SuccessfulRegistryProvider(CompanyRegistryProvider):
    provider_code = 'test_success'
    source = CompanyProfile.RegistrySource.TAX
    calls = 0

    def lookup(self, stir):
        type(self).calls += 1
        return RegistryProviderResult(
            company=RegistryCompanyData(
                company_name='Registry Company MChJ',
                company_type=CompanyProfile.CompanyType.MCHJ,
                director_name='Registry Director',
                legal_address='Toshkent shahri',
                registration_date='2020-01-15',
                has_vat=True,
                industry='IT',
            ),
            raw_payload={
                'company_name': 'Registry Company MChJ',
                'provider_internal_id': 'internal-42',
            },
        )


class NotFoundRegistryProvider(CompanyRegistryProvider):
    provider_code = 'test_not_found'
    source = CompanyProfile.RegistrySource.TAX
    calls = 0

    def lookup(self, stir):
        type(self).calls += 1
        raise RegistryNotFoundError()


class UnavailableRegistryProvider(CompanyRegistryProvider):
    provider_code = 'test_unavailable'
    source = CompanyProfile.RegistrySource.STATISTICS

    def lookup(self, stir):
        raise RegistryUnavailableError()


class BrokenRegistryProvider(CompanyRegistryProvider):
    provider_code = 'test_broken'
    source = CompanyProfile.RegistrySource.TAX

    def lookup(self, stir):
        raise RuntimeError('unexpected provider bug')


SUCCESS_PROVIDER = 'companies.tests.SuccessfulRegistryProvider'
NOT_FOUND_PROVIDER = 'companies.tests.NotFoundRegistryProvider'
UNAVAILABLE_PROVIDER = 'companies.tests.UnavailableRegistryProvider'
BROKEN_PROVIDER = 'companies.tests.BrokenRegistryProvider'


class CompanyRegistryApiTests(APITestCase):
    lookup_url = '/api/v1/companies/registry/lookup/'
    skip_url = '/api/v1/companies/onboarding/skip-stir/'

    def setUp(self):
        cache.clear()
        SuccessfulRegistryProvider.calls = 0
        NotFoundRegistryProvider.calls = 0
        self.user = CustomUser.objects.create_user(
            phone_number='+998901110001',
        )
        self.client.force_authenticate(self.user)

    def confirm_payload(self, **overrides):
        payload = {
            'company_name': 'User Edited Company MChJ',
            'company_type': CompanyProfile.CompanyType.MCHJ,
            'industry': 'Software',
            'experience_level': CompanyProfile.ExperienceLevel.INTERMEDIATE,
            'director_name': 'User Edited Director',
            'legal_address': 'User Edited Address',
            'registration_date': '2021-02-03',
            'has_vat': True,
        }
        payload.update(overrides)
        return payload

    def test_registry_endpoints_require_authentication(self):
        self.client.force_authenticate(user=None)

        response = self.client.post(
            self.lookup_url,
            {'stir': '123456789'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_lookup_rejects_invalid_stir_before_provider_access(self):
        response = self.client.post(
            self.lookup_url,
            {'stir': '12345ABC'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_database_rejects_invalid_company_stir(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            CompanyProfile.objects.create(
                user=self.user,
                stir='12345ABC',
                company_name='Invalid STIR Company',
                company_type=CompanyProfile.CompanyType.MCHJ,
                industry='IT',
            )

        self.assertFalse(CompanyRegistryDraft.objects.exists())

    @override_settings(COMPANY_REGISTRY_PROVIDER=SUCCESS_PROVIDER)
    def test_lookup_creates_editable_draft_without_writing_profile(self):
        response = self.client.post(
            self.lookup_url,
            {'stir': '123456789'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'ready')
        self.assertEqual(
            response.data['normalized_data']['company_name'],
            'Registry Company MChJ',
        )
        self.assertNotIn('raw_payload', response.data)
        self.assertFalse(CompanyProfile.objects.filter(user=self.user).exists())

    @override_settings(COMPANY_REGISTRY_PROVIDER=SUCCESS_PROVIDER)
    def test_successful_lookup_uses_cache(self):
        first = self.client.post(
            self.lookup_url,
            {'stir': '123456789'},
            format='json',
        )
        second = self.client.post(
            self.lookup_url,
            {'stir': '123456789'},
            format='json',
        )

        self.assertEqual(first.status_code, status.HTTP_201_CREATED)
        self.assertEqual(second.status_code, status.HTTP_201_CREATED)
        self.assertFalse(first.data['cache_hit'])
        self.assertTrue(second.data['cache_hit'])
        self.assertEqual(SuccessfulRegistryProvider.calls, 1)

    @override_settings(COMPANY_REGISTRY_PROVIDER=NOT_FOUND_PROVIDER)
    def test_not_found_result_is_cached_and_manual_entry_is_allowed(self):
        first = self.client.post(
            self.lookup_url,
            {'stir': '123456789'},
            format='json',
        )
        second = self.client.post(
            self.lookup_url,
            {'stir': '123456789'},
            format='json',
        )

        self.assertEqual(first.data['status'], 'failed')
        self.assertEqual(first.data['error_code'], 'registry_not_found')
        self.assertTrue(first.data['manual_entry_allowed'])
        self.assertTrue(second.data['cache_hit'])
        self.assertEqual(NotFoundRegistryProvider.calls, 1)

    @override_settings(COMPANY_REGISTRY_PROVIDER=UNAVAILABLE_PROVIDER)
    def test_provider_failure_does_not_block_manual_onboarding(self):
        lookup = self.client.post(
            self.lookup_url,
            {'stir': '123456789'},
            format='json',
        )
        onboarding = self.client.post(
            '/api/v1/companies/onboarding/',
            {
                'stir': '123456789',
                'company_name': 'Manual Company MChJ',
                'company_type': 'mchj',
                'industry': 'Services',
                'experience_level': 'beginner',
                'has_vat': False,
            },
            format='json',
        )

        self.assertEqual(lookup.status_code, status.HTTP_201_CREATED)
        self.assertEqual(lookup.data['status'], 'failed')
        self.assertEqual(lookup.data['error_code'], 'registry_unavailable')
        self.assertEqual(onboarding.status_code, status.HTTP_200_OK)
        self.assertEqual(onboarding.data['registry_status'], 'manual')

    @override_settings(COMPANY_REGISTRY_PROVIDER=BROKEN_PROVIDER)
    def test_unexpected_provider_error_is_converted_to_failed_draft(self):
        response = self.client.post(
            self.lookup_url,
            {'stir': '123456789'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'failed')
        self.assertEqual(response.data['error_code'], 'registry_unavailable')
        self.assertTrue(response.data['manual_entry_allowed'])

    @override_settings(COMPANY_REGISTRY_PROVIDER=SUCCESS_PROVIDER)
    def test_confirm_saves_user_edits_and_preserves_raw_audit_payload(self):
        lookup = self.client.post(
            self.lookup_url,
            {'stir': '123456789'},
            format='json',
        )

        response = self.client.post(
            f"/api/v1/companies/registry/drafts/{lookup.data['id']}/confirm/",
            self.confirm_payload(),
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        profile = CompanyProfile.objects.get(user=self.user)
        draft = CompanyRegistryDraft.objects.get(id=lookup.data['id'])
        self.assertEqual(profile.company_name, 'User Edited Company MChJ')
        self.assertEqual(profile.director_name, 'User Edited Director')
        self.assertEqual(profile.stir, '123456789')
        self.assertEqual(profile.registry_status, 'verified')
        self.assertEqual(profile.registry_source, 'tax')
        self.assertEqual(
            profile.raw_tax_data['provider_internal_id'],
            'internal-42',
        )
        self.assertEqual(
            draft.normalized_data['company_name'],
            'Registry Company MChJ',
        )
        self.assertEqual(
            draft.confirmed_data['company_name'],
            'User Edited Company MChJ',
        )
        self.assertEqual(draft.confirmed_data['registration_date'], '2021-02-03')
        self.assertNotIn('raw_tax_data', response.data['profile'])

    @override_settings(COMPANY_REGISTRY_PROVIDER=SUCCESS_PROVIDER)
    def test_another_user_cannot_read_or_confirm_draft(self):
        lookup = self.client.post(
            self.lookup_url,
            {'stir': '123456789'},
            format='json',
        )
        other_user = CustomUser.objects.create_user(
            phone_number='+998901110002',
        )
        self.client.force_authenticate(other_user)
        draft_url = f"/api/v1/companies/registry/drafts/{lookup.data['id']}/"

        read_response = self.client.get(draft_url)
        confirm_response = self.client.post(
            f'{draft_url}confirm/',
            self.confirm_payload(),
            format='json',
        )

        self.assertEqual(read_response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(confirm_response.status_code, status.HTTP_404_NOT_FOUND)

    @override_settings(COMPANY_REGISTRY_PROVIDER=SUCCESS_PROVIDER)
    def test_expired_draft_cannot_be_confirmed(self):
        lookup = self.client.post(
            self.lookup_url,
            {'stir': '123456789'},
            format='json',
        )
        draft = CompanyRegistryDraft.objects.get(id=lookup.data['id'])
        draft.expires_at = timezone.now() - timedelta(seconds=1)
        draft.save(update_fields=['expires_at'])

        response = self.client.post(
            f"/api/v1/companies/registry/drafts/{draft.id}/confirm/",
            self.confirm_payload(),
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data['error'], 'draft_expired')
        draft.refresh_from_db()
        self.assertEqual(draft.status, CompanyRegistryDraft.Status.EXPIRED)

    @override_settings(COMPANY_REGISTRY_PROVIDER=SUCCESS_PROVIDER)
    def test_confirm_rejects_stir_owned_by_another_profile(self):
        CompanyProfile.objects.create(
            user=CustomUser.objects.create_user(
                phone_number='+998901110003',
            ),
            stir='123456789',
            company_name='Existing Company',
            company_type='mchj',
            industry='Trade',
        )
        lookup = self.client.post(
            self.lookup_url,
            {'stir': '123456789'},
            format='json',
        )

        response = self.client.post(
            f"/api/v1/companies/registry/drafts/{lookup.data['id']}/confirm/",
            self.confirm_payload(),
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data['error'], 'stir_already_used')

    def test_skip_stir_creates_profile_and_keeps_gated_features_closed(self):
        response = self.client.post(
            self.skip_url,
            {
                'company_name': 'STIRsiz Company',
                'company_type': 'mchj',
                'industry': 'Consulting',
                'onboarding_answers': {'business_type': 'supplier'},
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['stir_skipped'])
        self.assertFalse(response.data['feature_access']['official_documents'])
        profile = CompanyProfile.objects.get(user=self.user)
        with self.assertRaises(PermissionDenied):
            require_company_stir(profile)

    def test_skip_does_not_remove_existing_stir(self):
        CompanyProfile.objects.create(
            user=self.user,
            stir='123456789',
            company_name='Existing Company',
            company_type='mchj',
            industry='Trade',
        )

        response = self.client.post(self.skip_url, {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data['error'], 'stir_already_present')

    @override_settings(COMPANY_REGISTRY_PROVIDER=SUCCESS_PROVIDER)
    def test_confirm_after_skip_opens_stir_feature_gate(self):
        self.client.post(
            self.skip_url,
            {
                'company_name': 'Initial Company',
                'company_type': 'mchj',
                'industry': 'Consulting',
            },
            format='json',
        )
        lookup = self.client.post(
            self.lookup_url,
            {'stir': '123456789'},
            format='json',
        )
        response = self.client.post(
            f"/api/v1/companies/registry/drafts/{lookup.data['id']}/confirm/",
            self.confirm_payload(),
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['profile']['stir_skipped'])
        self.assertTrue(
            response.data['profile']['feature_access']['official_documents']
        )
        profile = CompanyProfile.objects.get(user=self.user)
        self.assertIs(require_company_stir(profile), profile)

    @override_settings(COMPANY_REGISTRY_PROVIDER=SUCCESS_PROVIDER)
    def test_registry_refresh_bypasses_cache(self):
        CompanyProfile.objects.create(
            user=self.user,
            stir='123456789',
            company_name='Existing Company',
            company_type='mchj',
            industry='Trade',
            registry_status=CompanyProfile.RegistryStatus.MANUAL,
        )

        first = self.client.post(
            '/api/v1/companies/profile/registry-refresh/',
            {},
            format='json',
        )
        second = self.client.post(
            '/api/v1/companies/profile/registry-refresh/',
            {},
            format='json',
        )

        self.assertEqual(first.status_code, status.HTTP_201_CREATED)
        self.assertEqual(second.status_code, status.HTTP_201_CREATED)
        self.assertFalse(first.data['cache_hit'])
        self.assertFalse(second.data['cache_hit'])
        self.assertEqual(SuccessfulRegistryProvider.calls, 2)


class RegistryProviderContractTests(SimpleTestCase):
    def test_normalization_rejects_missing_company_name(self):
        with self.assertRaises(RegistryInvalidResponseError):
            normalize_registry_payload({'data': {'company_type': 'mchj'}})

    def test_normalization_maps_canonical_values(self):
        result = normalize_registry_payload({
            'data': {
                'company_name': 'Test Company',
                'company_type': 'LLC',
                'registration_date': '2024-05-06',
                'has_vat': 'true',
            },
        })

        self.assertEqual(result.company_type, CompanyProfile.CompanyType.MCHJ)
        self.assertEqual(result.registration_date, '2024-05-06')
        self.assertTrue(result.has_vat)

    @override_settings(
        COMPANY_REGISTRY_API_URL='https://registry.example.test/company',
        COMPANY_REGISTRY_API_TOKEN='test-token',
        COMPANY_REGISTRY_SOURCE='tax',
        COMPANY_REGISTRY_RETRY_COUNT=1,
        COMPANY_REGISTRY_TIMEOUT_SECONDS=5,
    )
    def test_http_provider_retries_timeout_once(self):
        response = Mock()
        response.status_code = 200
        response.json.return_value = {
            'company_name': 'Retry Company',
            'company_type': 'mchj',
        }
        session = Mock()
        session.get.side_effect = [requests.Timeout(), response]
        provider = ConfiguredHttpRegistryProvider(session=session)

        result = provider.lookup('123456789')

        self.assertEqual(result.company.company_name, 'Retry Company')
        self.assertEqual(session.get.call_count, 2)

    @override_settings(
        COMPANY_REGISTRY_API_URL='https://registry.example.test/company',
        COMPANY_REGISTRY_SOURCE='tax',
        COMPANY_REGISTRY_RETRY_COUNT=1,
    )
    def test_http_provider_maps_404_without_retry(self):
        response = Mock()
        response.status_code = 404
        session = Mock()
        session.get.return_value = response
        provider = ConfiguredHttpRegistryProvider(session=session)

        with self.assertRaises(RegistryNotFoundError):
            provider.lookup('123456789')

        self.assertEqual(session.get.call_count, 1)

    @override_settings(
        COMPANY_REGISTRY_API_URL='https://registry.example.test/company',
        COMPANY_REGISTRY_SOURCE='tax',
        COMPANY_REGISTRY_RETRY_COUNT=1,
    )
    def test_http_provider_maps_exhausted_timeouts_to_unavailable(self):
        session = Mock()
        session.get.side_effect = requests.Timeout()
        provider = ConfiguredHttpRegistryProvider(session=session)

        with self.assertRaises(RegistryUnavailableError):
            provider.lookup('123456789')

        self.assertEqual(session.get.call_count, 2)


class CompanyFeatureGateTests(SimpleTestCase):
    def test_verified_badge_requires_verified_registry_status(self):
        profile = CompanyProfile(
            stir='123456789',
            stir_skipped=False,
            registry_status=CompanyProfile.RegistryStatus.MANUAL,
        )

        access = get_company_feature_access(profile)

        self.assertTrue(access.official_documents)
        self.assertFalse(access.verified_company_badge)


class RegistrySettingsCheckTests(SimpleTestCase):
    @override_settings(COMPANY_REGISTRY_SOURCE='unknown')
    def test_invalid_registry_source_is_reported(self):
        error_ids = {error.id for error in run_checks()}

        self.assertIn('companies.E004', error_ids)
