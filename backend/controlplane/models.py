import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from controlplane.constants import AdminCapability
from subscriptions.constants import Feature


class AppendOnlyAuditQuerySet(models.QuerySet):
    def update(self, **kwargs):
        raise ValidationError('Admin audit events cannot be updated.')

    def delete(self):
        raise ValidationError('Admin audit events cannot be deleted.')


class AdminPrincipal(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='admin_principal',
    )
    capabilities = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    mfa_verified_at = models.DateTimeField(null=True, blank=True)
    step_up_at = models.DateTimeField(null=True, blank=True)
    version = models.PositiveIntegerField(default=1)
    granted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='granted_admin_principals',
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'admin_principals'

    def __str__(self):
        return f'{self.user} / {", ".join(self.capabilities)}'

    def clean(self):
        super().clean()
        if not self.user.is_staff:
            raise ValidationError({'user': 'Admin principal must be staff.'})
        if (
            not isinstance(self.capabilities, list)
            or any(not isinstance(item, str) for item in self.capabilities)
        ):
            raise ValidationError({
                'capabilities': 'Capabilities must be a list of strings.',
            })
        unknown = set(self.capabilities) - set(AdminCapability.ALL)
        if unknown:
            raise ValidationError({
                'capabilities': (
                    'Unknown capabilities: ' + ', '.join(sorted(unknown))
                ),
            })
        if len(self.capabilities) != len(set(self.capabilities)):
            raise ValidationError({
                'capabilities': 'Capabilities must be unique.',
            })

    def save(self, *args, **kwargs):
        self.capabilities = sorted(set(self.capabilities))
        self.full_clean()
        return super().save(*args, **kwargs)

    def has_capability(self, capability):
        return (
            AdminCapability.ROOT in self.capabilities
            or capability in self.capabilities
        )


class AdminActionRequest(models.Model):
    class Status(models.TextChoices):
        PROCESSING = 'processing', 'Processing'
        SUCCEEDED = 'succeeded', 'Succeeded'
        FAILED = 'failed', 'Failed'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='admin_action_requests',
    )
    idempotency_key = models.CharField(max_length=100)
    action = models.CharField(max_length=100)
    request_hash = models.CharField(max_length=64)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PROCESSING,
    )
    response_data = models.JSONField(default=dict, blank=True)
    response_status = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'admin_action_requests'
        constraints = [
            models.UniqueConstraint(
                fields=['actor', 'idempotency_key'],
                name='unique_admin_idempotency_key',
            ),
        ]
        indexes = [
            models.Index(fields=['actor', '-created_at']),
            models.Index(fields=['action', 'status']),
        ]


class AdminAuditEvent(models.Model):
    class Outcome(models.TextChoices):
        SUCCESS = 'success', 'Success'
        FAILURE = 'failure', 'Failure'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='admin_audit_events',
    )
    capability = models.CharField(max_length=50)
    action = models.CharField(max_length=100)
    target_type = models.CharField(max_length=100)
    target_id = models.CharField(max_length=255, blank=True, default='')
    reason = models.TextField()
    before = models.JSONField(default=dict, blank=True)
    after = models.JSONField(default=dict, blank=True)
    outcome = models.CharField(max_length=20, choices=Outcome.choices)
    request_id = models.CharField(max_length=100, blank=True, default='')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    objects = AppendOnlyAuditQuerySet.as_manager()

    class Meta:
        db_table = 'admin_audit_events'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['actor', '-created_at']),
            models.Index(fields=['action', '-created_at']),
            models.Index(fields=['target_type', 'target_id']),
        ]

    def save(self, *args, **kwargs):
        if self.pk and type(self).objects.filter(pk=self.pk).exists():
            raise ValidationError('Admin audit events are append-only.')
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError('Admin audit events cannot be deleted.')


class FeatureFlag(models.Model):
    feature = models.CharField(
        max_length=50,
        choices=tuple((item, item) for item in Feature.ALL),
        unique=True,
    )
    is_enabled = models.BooleanField(default=True)
    reason = models.TextField(blank=True, default='')
    version = models.PositiveIntegerField(default=1)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='updated_feature_flags',
        null=True,
        blank=True,
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'admin_feature_flags'


class SystemSetting(models.Model):
    MAINTENANCE_BANNER = 'maintenance_banner'
    KEY_CHOICES = ((MAINTENANCE_BANNER, 'Maintenance banner'),)

    key = models.CharField(max_length=100, choices=KEY_CHOICES, unique=True)
    value = models.JSONField(default=dict, blank=True)
    version = models.PositiveIntegerField(default=1)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='updated_system_settings',
        null=True,
        blank=True,
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'admin_system_settings'


class InvariantDiagnosticCounter(models.Model):
    """Current control-plane invariant and health counter snapshot."""

    class SourceStatus(models.TextChoices):
        HEALTHY = 'healthy', 'Healthy'
        DEGRADED = 'degraded', 'Degraded'
        UNAVAILABLE = 'unavailable', 'Unavailable'
        STALE = 'stale', 'Stale'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    key = models.CharField(max_length=150, unique=True)
    value = models.BigIntegerField(default=0)
    source_status = models.CharField(
        max_length=20,
        choices=SourceStatus.choices,
        default=SourceStatus.HEALTHY,
    )
    dimensions = models.JSONField(default=dict, blank=True)
    diagnostic_message = models.TextField(blank=True, default='')
    observed_at = models.DateTimeField()
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'admin_invariant_counters'
        indexes = [
            models.Index(fields=['source_status', '-observed_at']),
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(value__gte=0),
                name='admin_invariant_counter_non_negative',
            ),
        ]
