import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q


class TelegramIdentity(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        VERIFIED = 'verified', 'Verified'
        AWAITING_RELINK = (
            'awaiting_new_session_verification',
            'Awaiting new session verification',
        )
        REVOKED = 'revoked', 'Revoked'
        FAILED = 'failed', 'Failed'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    member = models.OneToOneField(
        'teams.CompanyMember',
        on_delete=models.CASCADE,
        related_name='telegram_identity',
    )
    telegram_user_id = models.BigIntegerField(null=True, blank=True)
    chat_id = models.BigIntegerField(null=True, blank=True)
    username = models.CharField(max_length=64, blank=True, default='')
    username_synced_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=50,
        choices=Status.choices,
        default=Status.PENDING,
    )
    initialization_context = models.JSONField(default=dict, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    relink_requested_at = models.DateTimeField(null=True, blank=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
    revoked_reason = models.CharField(max_length=255, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'telegram_identities'
        indexes = [
            models.Index(fields=['member', 'status']),
            models.Index(fields=['username']),
            models.Index(fields=['chat_id']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['telegram_user_id'],
                condition=Q(
                    telegram_user_id__isnull=False,
                    status='verified',
                ),
                name='unique_verified_telegram_user_id',
            ),
        ]


class TelegramLinkChallenge(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    member = models.ForeignKey(
        'teams.CompanyMember',
        on_delete=models.CASCADE,
        related_name='telegram_link_challenges',
    )
    token_hash = models.CharField(max_length=128, unique=True)
    expires_at = models.DateTimeField()
    attempts = models.PositiveSmallIntegerField(default=0)
    consumed_at = models.DateTimeField(null=True, blank=True)
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='telegram_link_challenges_requested',
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'telegram_link_challenges'
        indexes = [
            models.Index(fields=['member', 'expires_at', 'consumed_at']),
        ]


class TelegramMiniAppSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    identity = models.ForeignKey(
        TelegramIdentity,
        on_delete=models.CASCADE,
        related_name='mini_app_sessions',
    )
    init_data_hash = models.CharField(max_length=128, unique=True)
    auth_date = models.DateTimeField()
    last_active_at = models.DateTimeField(auto_now=True)
    device = models.CharField(max_length=255, blank=True, default='')
    user_agent = models.TextField(blank=True, default='')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    expires_at = models.DateTimeField()
    revoked_at = models.DateTimeField(null=True, blank=True)
    revoked_reason = models.CharField(max_length=255, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'telegram_mini_app_sessions'
        indexes = [
            models.Index(fields=['identity', 'revoked_at', 'last_active_at']),
            models.Index(fields=['expires_at']),
        ]


class NotificationPreference(models.Model):
    class Channel(models.TextChoices):
        TELEGRAM = 'telegram', 'Telegram'
        EMAIL = 'email', 'Email'
        PUSH = 'push', 'Push'

    class EventType(models.TextChoices):
        MATCHING_LOT = 'matching_lot', 'Matching lot'
        DEADLINE = 'deadline_reminder', 'Deadline reminder'
        ANALYSIS = 'analysis_status', 'Analysis status'
        DOCUMENT = 'document_status', 'Document status'
        SECURITY = 'security', 'Security'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    member = models.ForeignKey(
        'teams.CompanyMember',
        on_delete=models.CASCADE,
        related_name='notification_preferences',
    )
    event_type = models.CharField(max_length=40, choices=EventType.choices)
    channel = models.CharField(max_length=20, choices=Channel.choices)
    enabled = models.BooleanField(default=True)
    threshold = models.PositiveSmallIntegerField(null=True, blank=True)
    quiet_hours = models.JSONField(default=dict, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'notification_preferences'
        constraints = [
            models.UniqueConstraint(
                fields=['member', 'event_type', 'channel'],
                name='unique_member_event_channel_preference',
            ),
            models.CheckConstraint(
                condition=Q(threshold__isnull=True) | Q(threshold__lte=100),
                name='notification_threshold_lte_100',
            ),
        ]

    def clean(self):
        super().clean()
        if self.event_type == self.EventType.SECURITY and not self.enabled:
            raise ValidationError({
                'enabled': 'Security notifications cannot be disabled.',
            })


class NotificationDelivery(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        SENT = 'sent', 'Sent'
        FAILED = 'failed', 'Failed'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    member = models.ForeignKey(
        'teams.CompanyMember',
        on_delete=models.CASCADE,
        related_name='notification_deliveries',
    )
    event_key = models.CharField(max_length=255)
    event_type = models.CharField(
        max_length=40,
        choices=NotificationPreference.EventType.choices,
    )
    channel = models.CharField(
        max_length=20,
        choices=NotificationPreference.Channel.choices,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    attempts = models.PositiveSmallIntegerField(default=0)
    provider_message_id = models.CharField(max_length=255, blank=True, default='')
    error_message = models.CharField(max_length=500, blank=True, default='')
    payload_metadata = models.JSONField(default=dict, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'notification_deliveries'
        indexes = [
            models.Index(fields=['status', 'created_at']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['event_key', 'member', 'channel'],
                name='unique_notification_delivery',
            ),
        ]
