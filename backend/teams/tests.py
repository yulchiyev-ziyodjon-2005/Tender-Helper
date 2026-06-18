from datetime import timedelta

from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from companies.models import CompanyProfile
from subscriptions.models import CompanySubscription, SubscriptionPlan
from users.models import CustomUser
from .models import CompanyMember, TeamPermission, TeamSession
from .signals import ensure_owner_membership


class TeamApiTests(APITestCase):
    def setUp(self):
        self.owner = CustomUser.objects.create_user(
            email='owner@example.uz',
            password='OwnerPassword!23',
            full_name='Company Owner',
        )
        self.company = CompanyProfile.objects.create(
            user=self.owner,
            company_name='Owner Company',
            industry='IT',
            stir='309123456',
            registry_status=CompanyProfile.RegistryStatus.VERIFIED,
            current_tariff='business',
        )
        now = timezone.now()
        CompanySubscription.objects.create(
            company=self.company,
            plan=SubscriptionPlan.objects.get(code='business'),
            status=CompanySubscription.Status.ACTIVE,
            source=CompanySubscription.Source.SYSTEM,
            starts_at=now,
            current_period_start=now,
            current_period_end=now + timedelta(days=30),
        )
        self.client.force_authenticate(self.owner)

    def test_owner_membership_is_created(self):
        membership = CompanyMember.objects.get(
            company=self.company,
            user=self.owner,
        )
        self.assertEqual(membership.role, CompanyMember.Role.OWNER)
        self.assertIn(TeamPermission.MANAGE_TEAM, membership.permissions)
        self.assertTrue(membership.can_search_lots)
        self.assertTrue(membership.can_run_ai_analysis)
        self.assertTrue(membership.can_generate_documents)
        self.assertTrue(membership.can_view_competitor_metrics)

    def test_fixture_load_does_not_generate_duplicate_owner_membership(self):
        CompanyMember.objects.filter(
            company=self.company,
            user=self.owner,
        ).delete()

        ensure_owner_membership(
            sender=CompanyProfile,
            instance=self.company,
            raw=True,
        )

        self.assertFalse(
            CompanyMember.objects.filter(
                company=self.company,
                user=self.owner,
            ).exists(),
        )

    def test_analyst_role_projects_visual_permission_matrix(self):
        analyst = CustomUser.objects.create_user(
            email='analyst@example.uz',
            password='AnalystPassword!23',
        )
        membership = CompanyMember.objects.create(
            company=self.company,
            user=analyst,
            role=CompanyMember.Role.ANALYST,
        )

        self.assertTrue(membership.can_search_lots)
        self.assertTrue(membership.can_run_ai_analysis)
        self.assertTrue(membership.can_generate_documents)
        self.assertTrue(membership.can_view_competitor_metrics)
        self.assertNotIn(TeamPermission.MANAGE_TEAM, membership.permissions)

    def test_explicit_permissions_are_projected_to_visual_flags(self):
        viewer = CustomUser.objects.create_user(
            email='metrics.viewer@example.uz',
            password='ViewerPassword!23',
        )
        membership = CompanyMember.objects.create(
            company=self.company,
            user=viewer,
            role=CompanyMember.Role.VIEWER,
            permissions=[
                TeamPermission.VIEW_LOTS,
                TeamPermission.VIEW_COMPETITORS,
            ],
        )

        self.assertTrue(membership.can_search_lots)
        self.assertFalse(membership.can_run_ai_analysis)
        self.assertFalse(membership.can_generate_documents)
        self.assertTrue(membership.can_view_competitor_metrics)

    def test_owner_can_invite_member_with_explicit_permissions(self):
        response = self.client.post('/api/v1/team/members/', {
            'company_id': str(self.company.id),
            'full_name': 'Team Manager',
            'email': 'manager@example.uz',
            'temporary_password': 'Temporary!Pass23',
            'force_password_change': True,
            'role': 'manager',
            'permissions': [
                TeamPermission.VIEW_LOTS,
                TeamPermission.RUN_AI_ANALYSIS,
            ],
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['temporary_password'], 'Temporary!Pass23')
        member = CompanyMember.objects.get(user__email='manager@example.uz')
        self.assertEqual(
            member.permissions,
            [TeamPermission.VIEW_LOTS, TeamPermission.RUN_AI_ANALYSIS],
        )
        self.assertTrue(member.force_password_change)

    def test_viewer_cannot_manage_team(self):
        viewer = CustomUser.objects.create_user(
            email='viewer@example.uz',
            password='ViewerPassword!23',
        )
        CompanyMember.objects.create(
            company=self.company,
            user=viewer,
            role=CompanyMember.Role.VIEWER,
            permissions=[TeamPermission.VIEW_LOTS],
        )
        self.client.force_authenticate(viewer)
        response = self.client.get('/api/v1/team/members/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_revoke_terminates_membership_and_all_sessions(self):
        employee = CustomUser.objects.create_user(
            email='employee@example.uz',
            password='EmployeePassword!23',
        )
        member = CompanyMember.objects.create(
            company=self.company,
            user=employee,
            role=CompanyMember.Role.MANAGER,
            permissions=[TeamPermission.VIEW_LOTS],
        )
        TeamSession.objects.create(
            user=employee,
            token_jti='employee-access-jti',
            device='Windows',
            browser='Chrome',
            ip_address='127.0.0.1',
        )

        response = self.client.post(
            f'/api/v1/team/members/{member.id}/revoke-sessions/',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        member.refresh_from_db()
        employee.refresh_from_db()
        self.assertFalse(member.is_active)
        self.assertEqual(employee.auth_version, 1)
        self.assertIsNotNone(employee.team_sessions.get().revoked_at)

    def test_free_plan_cannot_use_team_management(self):
        self.company.subscriptions.update(status=CompanySubscription.Status.EXPIRED)
        self.company.current_tariff = 'free'
        self.company.save(update_fields=['current_tariff'])
        response = self.client.get('/api/v1/team/members/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_temporary_password_requires_change_before_workspace_access(self):
        invite = self.client.post('/api/v1/teams/members/', {
            'company_id': str(self.company.id),
            'full_name': 'Secure Employee',
            'email': 'secure.employee@example.uz',
            'temporary_password': 'Temporary!Pass23',
            'force_password_change': True,
            'role': 'viewer',
            'permissions': [TeamPermission.VIEW_LOTS],
        }, format='json')
        self.assertEqual(invite.status_code, status.HTTP_201_CREATED)

        self.client.force_authenticate(user=None)
        login = self.client.post('/api/v1/auth/login/', {
            'email': 'secure.employee@example.uz',
            'password': 'Temporary!Pass23',
        }, format='json')
        self.assertEqual(login.status_code, status.HTTP_200_OK)
        self.assertTrue(login.data['force_password_change'])

        access = login.data['tokens']['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')
        workspace = self.client.get('/api/v1/teams/workspace/')
        self.assertEqual(workspace.status_code, status.HTTP_401_UNAUTHORIZED)

        changed = self.client.post('/api/v1/auth/change-password/', {
            'current_password': 'Temporary!Pass23',
            'new_password': 'Permanent!Password24',
        }, format='json')
        self.assertEqual(changed.status_code, status.HTTP_200_OK)
        self.assertFalse(changed.data['force_password_change'])

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {changed.data['tokens']['access']}",
        )
        workspace = self.client.get('/api/v1/teams/workspace/')
        self.assertEqual(workspace.status_code, status.HTTP_200_OK)
