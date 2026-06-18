import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q


class TeamPermission:
    VIEW_LOTS = 'view_lots'
    EXPORT_LOTS = 'export_lot_data'
    RUN_AI_ANALYSIS = 'run_ai_analysis'
    USE_ANALYSIS_QUOTAS = 'use_analysis_quotas'
    GENERATE_DOCUMENTS = 'generate_ai_contracts'
    EDIT_DOCUMENTS = 'edit_inline_workspace'
    EXPORT_DOCUMENTS = 'export_pdf_docx'
    VIEW_COMPETITORS = 'access_competitor_metrics'
    MANAGE_TEAM = 'manage_team'

    ALL = (
        VIEW_LOTS,
        EXPORT_LOTS,
        RUN_AI_ANALYSIS,
        USE_ANALYSIS_QUOTAS,
        GENERATE_DOCUMENTS,
        EDIT_DOCUMENTS,
        EXPORT_DOCUMENTS,
        VIEW_COMPETITORS,
        MANAGE_TEAM,
    )


ROLE_DEFAULT_PERMISSIONS = {
    'owner': list(TeamPermission.ALL),
    'admin': list(TeamPermission.ALL),
    'manager': [
        TeamPermission.VIEW_LOTS,
        TeamPermission.EXPORT_LOTS,
        TeamPermission.RUN_AI_ANALYSIS,
        TeamPermission.USE_ANALYSIS_QUOTAS,
        TeamPermission.GENERATE_DOCUMENTS,
        TeamPermission.EDIT_DOCUMENTS,
        TeamPermission.EXPORT_DOCUMENTS,
        TeamPermission.VIEW_COMPETITORS,
    ],
    'analyst': [
        TeamPermission.VIEW_LOTS,
        TeamPermission.RUN_AI_ANALYSIS,
        TeamPermission.USE_ANALYSIS_QUOTAS,
        TeamPermission.GENERATE_DOCUMENTS,
        TeamPermission.EDIT_DOCUMENTS,
        TeamPermission.EXPORT_DOCUMENTS,
        TeamPermission.VIEW_COMPETITORS,
    ],
    'viewer': [
        TeamPermission.VIEW_LOTS,
        TeamPermission.VIEW_COMPETITORS,
    ],
}


class CompanyMember(models.Model):
    """WP2 company-scoped role and explicit permission assignment."""

    class Role(models.TextChoices):
        OWNER = 'owner', 'Owner'
        ADMIN = 'admin', 'Admin'
        MANAGER = 'manager', 'Manager'
        ANALYST = 'analyst', 'Analyst'
        VIEWER = 'viewer', 'Viewer'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(
        'companies.CompanyProfile',
        on_delete=models.CASCADE,
        related_name='memberships',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='company_memberships',
    )
    role = models.CharField(max_length=20, choices=Role.choices)
    permissions = models.JSONField(default=list, blank=True)
    can_search_lots = models.BooleanField(default=False)
    can_run_ai_analysis = models.BooleanField(default=False)
    can_generate_documents = models.BooleanField(default=False)
    can_view_competitor_metrics = models.BooleanField(default=False)
    force_password_change = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='team_invitations_sent',
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'company_members'
        ordering = ['role', 'user__full_name']
        constraints = [
            models.UniqueConstraint(
                fields=['company', 'user'],
                name='unique_company_member',
            ),
        ]
        indexes = [
            models.Index(fields=['company', 'is_active', 'role']),
            models.Index(fields=['user', 'is_active']),
        ]

    def clean(self):
        super().clean()
        if not isinstance(self.permissions, list):
            raise ValidationError({'permissions': 'Permissions must be a list.'})
        unknown = set(self.permissions) - set(TeamPermission.ALL)
        if unknown:
            raise ValidationError({
                'permissions': f'Unknown permissions: {", ".join(sorted(unknown))}',
            })
        if len(self.permissions) != len(set(self.permissions)):
            raise ValidationError({'permissions': 'Permissions must be unique.'})
        if self.role == self.Role.OWNER and self.company.user_id != self.user_id:
            raise ValidationError({'role': 'Owner role is reserved for company owner.'})

    def save(self, *args, **kwargs):
        if not self.permissions:
            self.permissions = list(ROLE_DEFAULT_PERMISSIONS[self.role])
        permission_set = set(self.permissions)
        self.can_search_lots = TeamPermission.VIEW_LOTS in permission_set
        self.can_run_ai_analysis = TeamPermission.RUN_AI_ANALYSIS in permission_set
        self.can_generate_documents = TeamPermission.GENERATE_DOCUMENTS in permission_set
        self.can_view_competitor_metrics = TeamPermission.VIEW_COMPETITORS in permission_set
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.company_id}:{self.user_id}:{self.role}'


class TeamSession(models.Model):
    """Security metadata observed for an authenticated employee session."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='team_sessions',
    )
    token_jti = models.CharField(max_length=255, unique=True)
    audience = models.CharField(max_length=50, default='web')
    auth_version = models.PositiveIntegerField(default=0)
    device = models.CharField(max_length=255, blank=True, default='')
    browser = models.CharField(max_length=255, blank=True, default='')
    user_agent = models.TextField(blank=True, default='')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    mfa_verified_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    last_active_at = models.DateTimeField(auto_now=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
    revoked_reason = models.CharField(max_length=255, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'team_sessions'
        ordering = ['-last_active_at']
        indexes = [
            models.Index(fields=['user', 'revoked_at', 'last_active_at']),
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(token_jti__gt=''),
                name='team_session_jti_not_empty',
            ),
        ]

    def __str__(self):
        return f'{self.user_id}:{self.token_jti}'
