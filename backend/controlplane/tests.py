from datetime import timedelta

from django.core.exceptions import ValidationError
from django.test import override_settings
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from companies.models import CompanyProfile
from controlplane.constants import AdminCapability
from controlplane.models import (
    AdminActionRequest,
    AdminAuditEvent,
    AdminPrincipal,
    FeatureFlag,
)
from controlplane.services.mfa import AdminMFAProvider
from subscriptions.constants import Feature
from subscriptions.models import (
    CompanySubscription,
    PaymentTransaction,
    SubscriptionPlan,
    WebhookEvent,
)
from subscriptions.services.billing import activate_subscription
from subscriptions.tasks import apply_scheduled_subscription_changes_task
from users.models import CustomUser


class TestAdminMFAProvider(AdminMFAProvider):
    def verify(self, *, user, code):
        return code == '123456'


TEST_MFA_PROVIDER = 'controlplane.tests.TestAdminMFAProvider'


class ControlPlaneApiTests(APITestCase):
    def setUp(self):
        self.root = CustomUser.objects.create_superuser(
            phone_number='+998901115001',
            email='root@example.test',
            password='StrongAdminPass123!',
        )
        now = timezone.now()
        self.principal = AdminPrincipal.objects.create(
            user=self.root,
            capabilities=[AdminCapability.ROOT],
            is_active=True,
            mfa_verified_at=now,
            step_up_at=now,
            granted_by=self.root,
        )
        self.user = CustomUser.objects.create_user(
            phone_number='+998901115002',
            email='user@example.test',
            password='UserPass123!',
            full_name='Ordinary User',
        )
        self.company = CompanyProfile.objects.create(
            user=self.user,
            stir='309555002',
            company_name='Ordinary Company MChJ',
            company_type=CompanyProfile.CompanyType.MCHJ,
            industry='IT',
        )
        self.client.force_authenticate(self.root)

    def action_payload(self, *, action, key, version='0', **extra):
        return {
            'action': action,
            'reason': 'Support ticket TH-1001 approved action.',
            'idempotency_key': key,
            'expected_version': version,
            'confirmed': True,
            **extra,
        }

    def test_company_owner_and_unassigned_superuser_are_denied(self):
        self.client.force_authenticate(self.user)
        owner_response = self.client.get('/api/v1/admin/overview/')

        unassigned = CustomUser.objects.create_superuser(
            phone_number='+998901115003',
            email='unassigned@example.test',
            password='StrongAdminPass123!',
        )
        self.client.force_authenticate(unassigned)
        superuser_response = self.client.get('/api/v1/admin/overview/')

        self.assertEqual(owner_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            superuser_response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_capabilities_are_least_privilege_and_root_assignment_is_audited(self):
        staff = CustomUser.objects.create_user(
            phone_number='+998901115004',
            email='support@example.test',
            password='SupportPass123!',
            is_staff=True,
        )
        assignment = self.client.post(
            f'/api/v1/admin/principals/{staff.id}/',
            {
                'capabilities': [AdminCapability.SUPPORT],
                'is_active': True,
                'reason': 'Approved support operator access TH-1000.',
                'idempotency_key': 'principal-assign-001',
                'expected_version': 'none',
                'confirmed': True,
            },
            format='json',
        )
        self.assertEqual(assignment.status_code, status.HTTP_200_OK)
        principal = AdminPrincipal.objects.get(user=staff)
        principal.mfa_verified_at = timezone.now()
        principal.step_up_at = timezone.now()
        principal.save(update_fields=[
            'mfa_verified_at',
            'step_up_at',
            'updated_at',
        ])

        self.client.force_authenticate(staff)
        users_response = self.client.get('/api/v1/admin/users/')
        plans_response = self.client.get('/api/v1/admin/plans/')

        self.assertEqual(users_response.status_code, status.HTTP_200_OK)
        self.assertEqual(plans_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(
            AdminAuditEvent.objects.filter(
                action='admin_principal.assign',
                target_id=str(principal.id),
            ).exists()
        )

    def test_last_active_root_cannot_remove_its_root_capability(self):
        response = self.client.post(
            f'/api/v1/admin/principals/{self.root.id}/',
            {
                'capabilities': [AdminCapability.SUPPORT],
                'is_active': True,
                'reason': 'Attempted root role rotation TH-1000.',
                'idempotency_key': 'last-root-remove-001',
                'expected_version': str(self.principal.version),
                'confirmed': True,
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data['code'], 'last_admin_root')
        self.principal.refresh_from_db()
        self.assertIn(AdminCapability.ROOT, self.principal.capabilities)

    def test_mfa_and_step_up_freshness_are_enforced(self):
        self.principal.mfa_verified_at = timezone.now() - timedelta(days=1)
        self.principal.step_up_at = timezone.now() - timedelta(days=1)
        self.principal.save(update_fields=[
            'mfa_verified_at',
            'step_up_at',
            'updated_at',
        ])

        overview = self.client.get('/api/v1/admin/overview/')

        self.assertEqual(overview.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(overview.data['code'], 'admin_mfa_required')

    @override_settings(ADMIN_MFA_PROVIDER=TEST_MFA_PROVIDER)
    def test_step_up_requires_password_and_mfa_and_is_audited(self):
        self.principal.mfa_verified_at = None
        self.principal.step_up_at = None
        self.principal.save(update_fields=[
            'mfa_verified_at',
            'step_up_at',
            'updated_at',
        ])

        failed = self.client.post(
            '/api/v1/admin/auth/step-up/',
            {'password': 'wrong', 'mfa_code': '123456'},
            format='json',
        )
        successful = self.client.post(
            '/api/v1/admin/auth/step-up/',
            {
                'password': 'StrongAdminPass123!',
                'mfa_code': '123456',
            },
            format='json',
        )

        self.assertEqual(failed.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(successful.status_code, status.HTTP_200_OK)
        self.principal.refresh_from_db()
        self.assertIsNotNone(self.principal.mfa_verified_at)
        self.assertEqual(
            AdminAuditEvent.objects.filter(action='admin.step_up').count(),
            2,
        )

    def test_overview_uses_real_sources_and_marks_missing_domains(self):
        response = self.client.get('/api/v1/admin/overview/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data['growth']['total_users'], 2)
        self.assertEqual(
            response.data['revenue']['source_status'],
            'unavailable',
        )
        self.assertEqual(
            response.data['operations']['payments']['source_status'],
            'unavailable',
        )

    def test_payment_list_uses_payment_ledger(self):
        plan = SubscriptionPlan.objects.get(code='business')
        transaction = PaymentTransaction.objects.create(
            company=self.company,
            plan=plan,
            provider=PaymentTransaction.Provider.CLICK,
            status=PaymentTransaction.Status.PREPARED,
            merchant_trans_id='th-controlplane-payment',
            amount=plan.price_uzs,
            currency=plan.currency,
            billing_period=plan.billing_period,
        )
        WebhookEvent.objects.create(
            provider=PaymentTransaction.Provider.CLICK,
            event_type='prepare',
            provider_event_id='click-001',
            action='0',
            transaction=transaction,
            status=WebhookEvent.Status.PROCESSED,
            request_payload={'action': '0'},
            response_payload={'error': 0},
        )

        response = self.client.get('/api/v1/admin/payments/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['source_status'], 'available')
        self.assertEqual(
            response.data['transactions'][0]['merchant_trans_id'],
            'th-controlplane-payment',
        )
        self.assertEqual(response.data['webhooks'][0]['provider_event_id'], 'click-001')
        self.assertEqual(
            response.data['reconciliation']['automated_job'],
            'not_implemented',
        )

    def test_user_list_masks_pii_and_reveal_requires_reason_and_audit(self):
        listed = self.client.get(
            '/api/v1/admin/users/',
            {'search': 'Ordinary'},
        )
        revealed = self.client.post(
            f'/api/v1/admin/users/{self.user.id}/reveal/',
            {'reason': 'Support ticket TH-1002 identity verification.'},
            format='json',
        )

        self.assertEqual(listed.status_code, status.HTTP_200_OK)
        row = listed.data['results'][0]
        self.assertNotEqual(row['email'], self.user.email)
        self.assertTrue(row['phone_number'].endswith('5002'))
        self.assertEqual(revealed.status_code, status.HTTP_200_OK)
        self.assertEqual(revealed.data['email'], self.user.email)
        self.assertTrue(
            AdminAuditEvent.objects.filter(
                action='user.pii_reveal',
                target_id=str(self.user.id),
            ).exists()
        )

    def test_session_revoke_is_idempotent_and_invalidates_existing_jwt(self):
        refresh = RefreshToken.for_user(self.user)
        refresh['auth_version'] = self.user.auth_version
        target_client = APIClient()
        target_client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}',
        )
        self.assertEqual(
            target_client.get('/api/v1/auth/me/').status_code,
            status.HTTP_200_OK,
        )
        payload = self.action_payload(
            action='revoke',
            key='revoke-session-001',
        )

        first = self.client.post(
            f'/api/v1/admin/users/{self.user.id}/action/',
            payload,
            format='json',
        )
        replay = self.client.post(
            f'/api/v1/admin/users/{self.user.id}/action/',
            payload,
            format='json',
        )

        self.assertEqual(first.status_code, status.HTTP_200_OK)
        self.assertFalse(first.data['idempotent_replay'])
        self.assertTrue(replay.data['idempotent_replay'])
        self.user.refresh_from_db()
        self.assertEqual(self.user.auth_version, 1)
        self.assertEqual(
            target_client.get('/api/v1/auth/me/').status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
        self.assertEqual(
            AdminAuditEvent.objects.filter(action='user.revoke').count(),
            1,
        )

    def test_stale_user_action_is_rejected_and_failure_is_audited(self):
        payload = self.action_payload(
            action='block',
            key='stale-user-action-001',
            version='999',
        )
        response = self.client.post(
            f'/api/v1/admin/users/{self.user.id}/action/',
            payload,
            format='json',
        )
        replay = self.client.post(
            f'/api/v1/admin/users/{self.user.id}/action/',
            payload,
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data['code'], 'admin_version_conflict')
        self.assertEqual(replay.status_code, status.HTTP_409_CONFLICT)
        self.assertTrue(replay.data['idempotent_replay'])
        self.assertEqual(replay.data['notification']['status'], 'error')
        self.assertTrue(
            AdminAuditEvent.objects.filter(
                action='user.block',
                outcome=AdminAuditEvent.Outcome.FAILURE,
            ).exists()
        )
        self.assertTrue(
            AdminActionRequest.objects.filter(
                idempotency_key='stale-user-action-001',
                status=AdminActionRequest.Status.FAILED,
            ).exists()
        )

    def test_feature_kill_switch_is_versioned_audited_and_enforced(self):
        flag = FeatureFlag.objects.get(feature=Feature.COMPETITOR_INTELLIGENCE)
        payload = {
            'reason': 'Incident TH-1003 temporary feature shutdown.',
            'idempotency_key': 'feature-flag-001',
            'expected_version': str(flag.version),
            'is_enabled': False,
            'confirmed': True,
        }

        response = self.client.post(
            '/api/v1/admin/operations/features/competitor_intelligence/',
            payload,
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        flag.refresh_from_db()
        self.assertFalse(flag.is_enabled)
        self.assertEqual(flag.version, 2)

        now = timezone.now()
        activate_subscription(
            self.company,
            SubscriptionPlan.objects.get(code='business'),
            period_start=now,
            period_end=now + timedelta(days=30),
        )
        self.client.force_authenticate(self.user)
        gated = self.client.get('/api/v1/competitors/freshness/')
        self.assertEqual(
            gated.status_code,
            status.HTTP_503_SERVICE_UNAVAILABLE,
        )
        self.assertEqual(gated.data['code'], 'feature_temporarily_disabled')

    def test_subscription_activation_uses_billing_service_and_audit(self):
        response = self.client.post(
            f'/api/v1/admin/subscriptions/{self.company.id}/action/',
            self.action_payload(
                action='activate',
                key='subscription-activate-001',
                version='none',
                plan_code='business',
            ),
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        subscription = CompanySubscription.objects.get(company=self.company)
        self.assertEqual(subscription.plan.code, 'business')
        self.assertEqual(subscription.status, CompanySubscription.Status.ACTIVE)
        self.assertTrue(
            AdminAuditEvent.objects.filter(
                action='subscription.activate',
                target_id=str(subscription.id),
            ).exists()
        )

    def test_search_detail_entitlement_and_subscription_preview_are_read_only(self):
        now = timezone.now()
        current = activate_subscription(
            self.company,
            SubscriptionPlan.objects.get(code='business'),
            period_start=now,
            period_end=now + timedelta(days=30),
        )

        search = self.client.get('/api/v1/admin/search/', {'q': 'Ordinary'})
        user_detail = self.client.get(
            f'/api/v1/admin/users/{self.user.id}/',
        )
        company_detail = self.client.get(
            f'/api/v1/admin/companies/{self.company.id}/',
        )
        entitlements = self.client.get(
            f'/api/v1/admin/companies/{self.company.id}/entitlements/',
            {'plan': 'enterprise'},
        )
        preview = self.client.post(
            f'/api/v1/admin/subscriptions/{self.company.id}/preview/',
            {
                'action': 'downgrade',
                'plan_code': 'pro',
                'expected_version': current.updated_at.isoformat(),
            },
            format='json',
        )

        self.assertEqual(search.status_code, status.HTTP_200_OK)
        self.assertEqual(search.data['companies'][0]['id'], self.company.id)
        self.assertEqual(user_detail.status_code, status.HTTP_200_OK)
        self.assertEqual(company_detail.status_code, status.HTTP_200_OK)
        self.assertEqual(
            company_detail.data['subscription']['plan'],
            'business',
        )
        self.assertEqual(entitlements.data['plan'], 'enterprise')
        self.assertEqual(entitlements.data['source'], 'proposed')
        self.assertEqual(preview.status_code, status.HTTP_200_OK)
        self.assertEqual(preview.data['proposed']['scheduled_plan'], 'pro')
        current.refresh_from_db()
        self.assertIsNone(current.scheduled_plan_id)

        no_subscription_company = CompanyProfile.objects.create(
            user=self.user,
            company_name='Read Only Preview MChJ',
            company_type=CompanyProfile.CompanyType.MCHJ,
            industry='Services',
        )
        empty_detail = self.client.get(
            f'/api/v1/admin/companies/{no_subscription_company.id}/',
        )
        self.assertEqual(empty_detail.status_code, status.HTTP_200_OK)
        self.assertIsNone(empty_detail.data['subscription'])
        self.assertEqual(empty_detail.data['effective_plan'], 'free')
        self.assertFalse(
            CompanySubscription.objects.filter(
                company=no_subscription_company,
            ).exists()
        )

    def test_critical_write_requires_confirmation_and_fresh_step_up(self):
        payload = self.action_payload(
            action='block',
            key='block-confirmation-001',
        )
        payload['confirmed'] = False
        confirmation_response = self.client.post(
            f'/api/v1/admin/users/{self.user.id}/action/',
            payload,
            format='json',
        )
        self.assertEqual(
            confirmation_response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.principal.step_up_at = timezone.now() - timedelta(hours=1)
        self.principal.save(update_fields=['step_up_at', 'updated_at'])
        payload['confirmed'] = True
        payload['idempotency_key'] = 'block-step-up-001'
        step_up_response = self.client.post(
            f'/api/v1/admin/users/{self.user.id}/action/',
            payload,
            format='json',
        )
        self.assertEqual(step_up_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(step_up_response.data['code'], 'admin_step_up_required')

    def test_plan_preview_does_not_mutate_and_publish_is_audited(self):
        plan = SubscriptionPlan.objects.get(code='business')
        original_limits = dict(plan.limits)
        proposed_limits = {**original_limits, 'ai_analysis_monthly': 275}

        preview = self.client.post(
            '/api/v1/admin/plans/business/preview/',
            {'limits': proposed_limits},
            format='json',
        )

        self.assertEqual(preview.status_code, status.HTTP_200_OK)
        self.assertIn('limits', preview.data['changed_fields'])
        plan.refresh_from_db()
        self.assertEqual(plan.limits, original_limits)

        payload = {
            'limits': proposed_limits,
            'reason': 'Approved pricing review TH-1101 plan limit update.',
            'idempotency_key': 'plan-update-001',
            'expected_version': plan.updated_at.isoformat(),
            'confirmed': True,
        }
        published = self.client.post(
            '/api/v1/admin/plans/business/',
            payload,
            format='json',
        )
        replay = self.client.post(
            '/api/v1/admin/plans/business/',
            payload,
            format='json',
        )

        self.assertEqual(published.status_code, status.HTTP_200_OK)
        self.assertFalse(published.data['idempotent_replay'])
        self.assertTrue(replay.data['idempotent_replay'])
        plan.refresh_from_db()
        self.assertEqual(plan.limits, proposed_limits)
        self.assertEqual(
            AdminAuditEvent.objects.filter(action='plan.update').count(),
            1,
        )

    def test_scheduled_downgrade_is_applied_once(self):
        now = timezone.now()
        current = activate_subscription(
            self.company,
            SubscriptionPlan.objects.get(code='business'),
            period_start=now,
            period_end=now + timedelta(days=30),
        )
        response = self.client.post(
            f'/api/v1/admin/subscriptions/{self.company.id}/action/',
            self.action_payload(
                action='downgrade',
                key='subscription-downgrade-001',
                version=current.updated_at.isoformat(),
                plan_code='pro',
            ),
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['scheduled_plan'], 'pro')
        current.refresh_from_db()
        CompanySubscription.objects.filter(pk=current.pk).update(
            scheduled_change_at=timezone.now() - timedelta(seconds=1),
        )

        first = apply_scheduled_subscription_changes_task()
        second = apply_scheduled_subscription_changes_task()

        self.assertEqual(first, 1)
        self.assertEqual(second, 0)
        active = CompanySubscription.objects.get(
            company=self.company,
            status=CompanySubscription.Status.ACTIVE,
        )
        self.assertEqual(active.plan.code, 'pro')

    def test_elapsed_scheduled_expiry_is_cleared_without_activation(self):
        now = timezone.now()
        current = activate_subscription(
            self.company,
            SubscriptionPlan.objects.get(code='business'),
            period_start=now,
            period_end=now + timedelta(days=30),
        )
        response = self.client.post(
            f'/api/v1/admin/subscriptions/{self.company.id}/action/',
            self.action_payload(
                action='downgrade',
                key='subscription-expired-schedule-001',
                version=current.updated_at.isoformat(),
                plan_code='pro',
                effective_at=now + timedelta(days=30),
                period_end=now + timedelta(days=60),
            ),
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        CompanySubscription.objects.filter(pk=current.pk).update(
            scheduled_change_at=now - timedelta(days=2),
            scheduled_period_end=now - timedelta(days=1),
        )

        applied = apply_scheduled_subscription_changes_task()

        self.assertEqual(applied, 0)
        current.refresh_from_db()
        self.assertIsNone(current.scheduled_plan_id)
        self.assertEqual(
            current.metadata['scheduled_change_skipped']['reason'],
            'scheduled_period_end_elapsed',
        )
        self.assertFalse(
            CompanySubscription.objects.filter(
                company=self.company,
                plan__code='pro',
                status=CompanySubscription.Status.ACTIVE,
            ).exists()
        )

    def test_maintenance_banner_is_versioned_and_audited(self):
        operations = self.client.get('/api/v1/admin/operations/')
        version = operations.data['maintenance_banner']['version']
        response = self.client.post(
            '/api/v1/admin/operations/maintenance-banner/',
            {
                'enabled': True,
                'message': 'Planned database maintenance.',
                'severity': 'warning',
                'reason': 'Approved maintenance window TH-1102.',
                'idempotency_key': 'maintenance-banner-001',
                'expected_version': str(version),
                'confirmed': True,
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['value']['enabled'])
        self.assertTrue(
            AdminAuditEvent.objects.filter(
                action='system_setting.maintenance_banner.update',
            ).exists()
        )

    def test_user_and_audit_exports_are_step_up_protected_and_audited(self):
        user_export = self.client.post(
            f'/api/v1/admin/users/{self.user.id}/export/',
            {'reason': 'Approved data request TH-1103 export.'},
            format='json',
        )
        audit_export = self.client.post(
            '/api/v1/admin/audit/export/',
            {'reason': 'Quarterly compliance review TH-1104 export.'},
            format='json',
        )

        self.assertEqual(user_export.status_code, status.HTTP_200_OK)
        self.assertEqual(user_export['Content-Type'], 'text/csv')
        self.assertEqual(audit_export.status_code, status.HTTP_200_OK)
        self.assertTrue(
            AdminAuditEvent.objects.filter(action='user.pii_export').exists()
        )
        self.assertTrue(
            AdminAuditEvent.objects.filter(action='audit.export').exists()
        )


class AdminAuditImmutabilityTests(APITestCase):
    def setUp(self):
        self.actor = CustomUser.objects.create_superuser(
            phone_number='+998901115010',
            email='audit@example.test',
            password='StrongAdminPass123!',
        )
        self.event = AdminAuditEvent.objects.create(
            actor=self.actor,
            capability=AdminCapability.AUDIT,
            action='test.action',
            target_type='test',
            target_id='1',
            reason='Test append-only audit event.',
            outcome=AdminAuditEvent.Outcome.SUCCESS,
        )

    def test_audit_event_cannot_be_updated_or_deleted(self):
        self.event.reason = 'Changed'
        with self.assertRaises(ValidationError):
            self.event.save()
        with self.assertRaises(ValidationError):
            self.event.delete()
        with self.assertRaises(ValidationError):
            AdminAuditEvent.objects.filter(pk=self.event.pk).delete()
        with self.assertRaises(ValidationError):
            AdminAuditEvent.objects.filter(pk=self.event.pk).update(
                reason='Changed',
            )
