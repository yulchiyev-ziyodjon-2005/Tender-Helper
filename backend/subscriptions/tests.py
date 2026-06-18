import hashlib
from datetime import timedelta
from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import override_settings
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from companies.models import CompanyProfile
from subscriptions.constants import CompanyRole, Feature
from subscriptions.exceptions import (
    CompanyAccessDenied,
    CompanyRoleDenied,
    UsageLimitExceeded,
)
from subscriptions.models import (
    CompanySubscription,
    PaymentTransaction,
    SubscriptionPlan,
    UsageRecord,
    WebhookEvent,
)
from subscriptions.services.billing import (
    activate_subscription,
    cancel_subscription,
    extend_subscription,
    get_effective_subscription,
)
from subscriptions.services.entitlements import authorize_feature
from subscriptions.services.membership import (
    CompanyMembership,
    resolve_company_membership,
)
from subscriptions.services.usage import consume_usage
from users.models import CustomUser


class SubscriptionApiTests(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            phone_number='+998901112201',
        )
        self.client.force_authenticate(self.user)
        self.company = CompanyProfile.objects.create(
            user=self.user,
            company_name='Subscription Test MChJ',
            company_type=CompanyProfile.CompanyType.MCHJ,
            industry='IT',
        )

    def activate(self, plan_code, *, company=None, start=None, end=None):
        now = timezone.now()
        return activate_subscription(
            company or self.company,
            SubscriptionPlan.objects.get(code=plan_code),
            period_start=start or now,
            period_end=end or (now + timedelta(days=30)),
        )

    def test_seeded_plan_catalog_has_authoritative_limits(self):
        plans = {
            plan.code: plan
            for plan in SubscriptionPlan.objects.order_by('rank')
        }

        self.assertEqual(list(plans), ['free', 'pro', 'business', 'enterprise'])
        self.assertEqual(plans['free'].limits['ai_analysis_monthly'], 4)
        self.assertEqual(plans['pro'].limits['ai_analysis_monthly'], 100)
        self.assertEqual(plans['business'].limits['ai_analysis_monthly'], 250)
        self.assertEqual(plans['enterprise'].limits['ai_analysis_monthly'], 500)
        self.assertEqual(plans['free'].price_uzs, 0)
        self.assertEqual(plans['pro'].price_uzs, 350000)
        self.assertEqual(plans['business'].price_uzs, 950000)

    def test_plan_configuration_rejects_unknown_features_and_bad_limits(self):
        plan = SubscriptionPlan(
            code='invalid',
            name='Invalid',
            features=['unknown_feature'],
            limits={'ai_analysis_monthly': -1},
        )

        with self.assertRaises(ValidationError) as context:
            plan.full_clean()

        self.assertIn('features', context.exception.message_dict)
        self.assertIn('limits', context.exception.message_dict)

    def test_plan_catalog_requires_authentication(self):
        self.client.force_authenticate(user=None)

        response = self.client.get('/api/v1/subscriptions/plans/')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_current_endpoint_creates_free_subscription_for_new_company(self):
        response = self.client.get('/api/v1/subscriptions/current/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['plan']['code'], 'free')
        self.assertEqual(response.data['status'], CompanySubscription.Status.ACTIVE)
        self.assertEqual(
            CompanySubscription.objects.filter(
                company=self.company,
                status=CompanySubscription.Status.ACTIVE,
            ).count(),
            1,
        )

    def test_legacy_and_canonical_status_routes_use_same_source(self):
        self.activate('pro')

        canonical = self.client.get('/api/v1/subscriptions/status/')
        legacy = self.client.get('/api/v1/subscription/status/')

        self.assertEqual(canonical.status_code, status.HTTP_200_OK)
        self.assertEqual(legacy.status_code, status.HTTP_200_OK)
        self.assertEqual(canonical.data['current_tariff'], 'pro')
        self.assertEqual(legacy.data['current_tariff'], 'pro')
        self.assertEqual(canonical.data['analysis_per_month'], 100)

    def test_direct_feature_url_cannot_bypass_plan_gate(self):
        response = self.client.post(
            f'/api/v1/subscriptions/features/{Feature.DOCUMENT_GENERATION}/check/',
            {'company_id': self.company.id},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['code'], 'feature_not_available')
        self.assertEqual(
            response.data['details'],
            {
                'feature': Feature.DOCUMENT_GENERATION,
                'requires_stir': True,
                'required_plan': 'business',
            },
        )

    def test_business_document_feature_requires_stir(self):
        self.activate('business')

        denied = self.client.post(
            f'/api/v1/subscriptions/features/{Feature.DOCUMENT_GENERATION}/check/',
            {'company_id': self.company.id},
            format='json',
        )
        self.assertEqual(denied.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(denied.data['code'], 'stir_required')

        self.company.stir = '309123456'
        self.company.save(update_fields=['stir', 'updated_at'])
        allowed = self.client.post(
            f'/api/v1/subscriptions/features/{Feature.DOCUMENT_GENERATION}/check/',
            {'company_id': self.company.id},
            format='json',
        )

        self.assertEqual(allowed.status_code, status.HTTP_200_OK)
        self.assertTrue(allowed.data['allowed'])
        self.assertEqual(allowed.data['plan'], 'business')

    def test_enterprise_inherits_every_business_feature(self):
        self.company.stir = '309123457'
        self.company.save(update_fields=['stir', 'updated_at'])
        self.activate('enterprise')

        for feature in Feature.ALL:
            with self.subTest(feature=feature):
                response = self.client.post(
                    f'/api/v1/subscriptions/features/{feature}/check/',
                    {'company_id': self.company.id},
                    format='json',
                )
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertTrue(response.data['allowed'])

    def test_expired_paid_subscription_falls_back_to_free(self):
        now = timezone.now()
        paid = self.activate(
            'business',
            start=now - timedelta(days=31),
            end=now - timedelta(days=1),
        )

        response = self.client.post(
            f'/api/v1/subscriptions/features/{Feature.TEAM_COLLABORATION}/check/',
            {'company_id': self.company.id},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['code'], 'feature_not_available')
        paid.refresh_from_db()
        self.assertEqual(paid.status, CompanySubscription.Status.EXPIRED)
        self.assertEqual(
            get_effective_subscription(self.company).plan.code,
            'free',
        )

    def test_trial_past_its_trial_end_is_not_effective(self):
        now = timezone.now()
        business = SubscriptionPlan.objects.get(code='business')
        trial = CompanySubscription.objects.create(
            company=self.company,
            plan=business,
            status=CompanySubscription.Status.TRIALING,
            starts_at=now - timedelta(days=10),
            trial_ends_at=now - timedelta(minutes=1),
            current_period_start=now - timedelta(days=10),
            current_period_end=now + timedelta(days=20),
        )

        effective = get_effective_subscription(self.company)

        self.assertEqual(effective.plan.code, 'free')
        trial.refresh_from_db()
        self.assertEqual(trial.status, CompanySubscription.Status.EXPIRED)

    def test_other_company_is_not_selectable(self):
        other_user = CustomUser.objects.create_user(
            phone_number='+998901112202',
        )
        other_company = CompanyProfile.objects.create(
            user=other_user,
            company_name='Other Company',
            company_type=CompanyProfile.CompanyType.MCHJ,
            industry='Trade',
        )

        response = self.client.post(
            f'/api/v1/subscriptions/features/{Feature.TEAM_COLLABORATION}/check/',
            {'company_id': other_company.id},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_entitlements_endpoint_reports_denial_reasons(self):
        response = self.client.get('/api/v1/subscriptions/entitlements/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['plan'], 'free')
        self.assertEqual(len(response.data['entitlements']), len(Feature.ALL))
        self.assertTrue(all(
            item['denial_code'] == 'feature_not_available'
            for item in response.data['entitlements']
        ))

    @override_settings(CLICK_SERVICE_ID='', CLICK_SECRET_KEY='')
    def test_checkout_does_not_activate_plan_without_payment_provider(self):
        response = self.client.post(
            '/api/v1/subscriptions/checkout/',
            {'company_id': self.company.id, 'plan_code': 'business'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_501_NOT_IMPLEMENTED)
        self.assertEqual(response.data['code'], 'payment_not_configured')
        self.assertFalse(
            CompanySubscription.objects.filter(company=self.company).exists()
        )

    @override_settings(CLICK_SERVICE_ID='98765', CLICK_SECRET_KEY='click-secret')
    def test_click_checkout_creates_pending_payment_transaction(self):
        response = self.client.post(
            '/api/v1/subscriptions/checkout/',
            {
                'company_id': self.company.id,
                'plan_code': 'business',
                'provider': 'click',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['transaction']['provider'], 'click')
        self.assertEqual(response.data['transaction']['status'], 'pending')
        self.assertEqual(response.data['payment']['service_id'], '98765')
        self.assertFalse(
            CompanySubscription.objects.filter(company=self.company).exists()
        )

    @override_settings(CLICK_SERVICE_ID='98765', CLICK_SECRET_KEY='click-secret')
    def test_click_prepare_and_complete_activate_subscription_once(self):
        checkout = self.client.post(
            '/api/v1/subscriptions/checkout/',
            {
                'company_id': self.company.id,
                'plan_code': 'business',
                'provider': 'click',
            },
            format='json',
        )
        transaction_obj = PaymentTransaction.objects.get(
            merchant_trans_id=checkout.data['payment']['merchant_trans_id'],
        )
        amount = str(transaction_obj.amount)
        prepare_payload = self._click_payload(
            action='0',
            merchant_trans_id=transaction_obj.merchant_trans_id,
            amount=amount,
        )

        prepare = self.client.post(
            '/api/v1/payments/click/prepare/',
            prepare_payload,
            format='json',
        )

        self.assertEqual(prepare.status_code, status.HTTP_200_OK)
        self.assertEqual(prepare.data['error'], 0)
        self.assertEqual(prepare.data['merchant_prepare_id'], transaction_obj.id)

        complete_payload = self._click_payload(
            action='1',
            merchant_trans_id=transaction_obj.merchant_trans_id,
            amount=amount,
            merchant_prepare_id=transaction_obj.id,
        )
        complete = self.client.post(
            '/api/v1/payments/click/complete/',
            complete_payload,
            format='json',
        )
        duplicate = self.client.post(
            '/api/v1/payments/click/complete/',
            complete_payload,
            format='json',
        )

        self.assertEqual(complete.status_code, status.HTTP_200_OK)
        self.assertEqual(complete.data['error'], 0)
        self.assertEqual(duplicate.data, complete.data)
        transaction_obj.refresh_from_db()
        self.assertEqual(transaction_obj.status, PaymentTransaction.Status.SUCCEEDED)
        self.assertEqual(transaction_obj.subscription.status, 'active')
        self.assertEqual(transaction_obj.subscription.source, 'payment')
        self.assertEqual(transaction_obj.subscription.plan.code, 'business')
        self.assertEqual(
            WebhookEvent.objects.filter(
                provider='click',
                provider_event_id='123456789',
                action='1',
            ).count(),
            1,
        )

    @override_settings(CLICK_SERVICE_ID='98765', CLICK_SECRET_KEY='click-secret')
    def test_click_rejects_bad_signature_without_activation(self):
        checkout = self.client.post(
            '/api/v1/subscriptions/checkout/',
            {
                'company_id': self.company.id,
                'plan_code': 'business',
                'provider': 'click',
            },
            format='json',
        )
        transaction_obj = PaymentTransaction.objects.get(
            merchant_trans_id=checkout.data['payment']['merchant_trans_id'],
        )
        payload = self._click_payload(
            action='0',
            merchant_trans_id=transaction_obj.merchant_trans_id,
            amount=str(transaction_obj.amount),
        )
        payload['sign_string'] = 'bad-signature'

        response = self.client.post(
            '/api/v1/payments/click/prepare/',
            payload,
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['error'], -1)
        transaction_obj.refresh_from_db()
        self.assertEqual(transaction_obj.status, PaymentTransaction.Status.PENDING)
        self.assertFalse(
            CompanySubscription.objects.filter(company=self.company).exists()
        )

    @override_settings(
        CLICK_SERVICE_ID='98765',
        CLICK_SECRET_KEY='click-secret',
        CLICK_ALLOWED_IPS=['203.0.113.10'],
    )
    def test_click_webhook_rejects_unlisted_ip(self):
        response = self.client.post(
            '/api/v1/payments/click/prepare/',
            {},
            format='json',
            REMOTE_ADDR='198.51.100.20',
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['code'], 'click_ip_not_allowed')
        self.assertFalse(WebhookEvent.objects.exists())

    def test_canceled_subscription_cannot_be_extended(self):
        subscription = self.activate('business')
        cancel_subscription(subscription)

        with self.assertRaisesMessage(
            ValueError,
            'Canceled subscription cannot be extended.',
        ):
            extend_subscription(
                subscription,
                subscription.current_period_end + timedelta(days=30),
            )

    def _click_payload(
        self,
        *,
        action,
        merchant_trans_id,
        amount,
        merchant_prepare_id=None,
    ):
        payload = {
            'click_trans_id': '123456789',
            'service_id': '98765',
            'click_paydoc_id': '555111',
            'merchant_trans_id': merchant_trans_id,
            'amount': amount,
            'action': action,
            'error': '0',
            'error_note': 'Success',
            'sign_time': '2026-06-17 10:00:00',
        }
        parts = [
            payload['click_trans_id'],
            payload['service_id'],
            'click-secret',
            payload['merchant_trans_id'],
        ]
        if action == '1':
            payload['merchant_prepare_id'] = str(merchant_prepare_id)
            parts.append(payload['merchant_prepare_id'])
        parts.extend([
            payload['amount'],
            payload['action'],
            payload['sign_time'],
        ])
        payload['sign_string'] = hashlib.md5(
            ''.join(parts).encode('utf-8'),
        ).hexdigest()
        return payload


class EntitlementServiceTests(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            phone_number='+998901112211',
        )
        self.other_user = CustomUser.objects.create_user(
            phone_number='+998901112212',
        )
        self.company = CompanyProfile.objects.create(
            user=self.user,
            stir='309123458',
            company_name='Entitlement Test MChJ',
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

    def test_membership_resolver_denies_non_owner(self):
        with self.assertRaises(CompanyAccessDenied):
            resolve_company_membership(self.other_user, self.company)

    @patch('subscriptions.services.entitlements.resolve_company_membership')
    def test_role_policy_is_enforced(self, membership_mock):
        membership_mock.return_value = CompanyMembership(
            company=self.company,
            user=self.user,
            role=CompanyRole.ANALYST,
        )

        with self.assertRaises(CompanyRoleDenied):
            authorize_feature(
                self.user,
                self.company,
                Feature.TEAM_COLLABORATION,
            )


class UsageServiceTests(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            phone_number='+998901112221',
        )
        self.company = CompanyProfile.objects.create(
            user=self.user,
            company_name='Usage Test MChJ',
            company_type=CompanyProfile.CompanyType.MCHJ,
            industry='IT',
        )

    def test_free_limit_is_consumed_exactly_and_never_overruns(self):
        for expected in range(1, 5):
            record = consume_usage(
                self.company,
                UsageRecord.Metric.AI_ANALYSIS,
            )
            self.assertEqual(record.used, expected)

        with self.assertRaises(UsageLimitExceeded):
            consume_usage(
                self.company,
                UsageRecord.Metric.AI_ANALYSIS,
            )

        record = UsageRecord.objects.get(
            company=self.company,
            metric=UsageRecord.Metric.AI_ANALYSIS,
        )
        self.assertEqual(record.used, 4)
        self.assertEqual(record.limit_snapshot, 4)

    def test_database_rejects_two_active_subscriptions(self):
        now = timezone.now()
        free = SubscriptionPlan.objects.get(code='free')
        CompanySubscription.objects.create(
            company=self.company,
            plan=free,
            status=CompanySubscription.Status.ACTIVE,
            starts_at=now,
            current_period_start=now,
            current_period_end=now + timedelta(days=30),
        )

        with self.assertRaises(IntegrityError), transaction.atomic():
            CompanySubscription.objects.create(
                company=self.company,
                plan=free,
                status=CompanySubscription.Status.ACTIVE,
                starts_at=now,
                current_period_start=now,
                current_period_end=now + timedelta(days=30),
            )

    def test_database_rejects_incomplete_subscription_schedule(self):
        now = timezone.now()
        free = SubscriptionPlan.objects.get(code='free')

        with self.assertRaises(IntegrityError), transaction.atomic():
            CompanySubscription.objects.create(
                company=self.company,
                plan=free,
                status=CompanySubscription.Status.PAUSED,
                starts_at=now,
                current_period_start=now,
                current_period_end=now + timedelta(days=30),
                scheduled_plan=free,
                scheduled_change_at=None,
            )

    def test_database_rejects_negative_plan_price(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            SubscriptionPlan.objects.create(
                code='invalid-negative-price',
                name='Invalid price',
                price_uzs=-1,
            )

    def test_usage_limit_snapshot_is_stable_within_the_period(self):
        first = consume_usage(
            self.company,
            UsageRecord.Metric.AI_ANALYSIS,
        )
        free = SubscriptionPlan.objects.get(code='free')
        free.limits = {'ai_analysis_monthly': 1}
        free.save(update_fields=['limits', 'updated_at'])

        second = consume_usage(
            self.company,
            UsageRecord.Metric.AI_ANALYSIS,
        )

        self.assertEqual(first.limit_snapshot, 4)
        self.assertEqual(second.limit_snapshot, 4)
        self.assertEqual(second.used, 2)

    def test_usage_endpoint_returns_remaining_allowance(self):
        self.client.force_authenticate(self.user)
        consume_usage(self.company, UsageRecord.Metric.AI_ANALYSIS)

        response = self.client.get('/api/v1/subscriptions/usage/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['plan'], 'free')
        self.assertEqual(response.data['usage'][0]['used'], 1)
        self.assertEqual(response.data['usage'][0]['remaining'], 3)
