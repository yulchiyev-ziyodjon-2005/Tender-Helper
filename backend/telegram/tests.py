from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone

from companies.models import CompanyProfile
from teams.models import CompanyMember
from users.models import CustomUser

from .models import (
    NotificationDelivery,
    NotificationPreference,
    TelegramIdentity,
)


class TelegramDataContractTests(TestCase):
    def setUp(self):
        self.owner = CustomUser.objects.create_user(
            email='telegram.owner@example.uz',
            password='OwnerPassword!23',
        )
        self.company = CompanyProfile.objects.create(
            user=self.owner,
            company_name='Telegram Company',
            industry='IT',
            stir='309654321',
            registry_status=CompanyProfile.RegistryStatus.VERIFIED,
            current_tariff='business',
        )
        self.member = CompanyMember.objects.get(
            company=self.company,
            user=self.owner,
        )

    def test_verified_numeric_telegram_id_is_globally_unique(self):
        TelegramIdentity.objects.create(
            member=self.member,
            telegram_user_id=123456789,
            username='current_name',
            status=TelegramIdentity.Status.VERIFIED,
            verified_at=timezone.now(),
        )
        second_user = CustomUser.objects.create_user(
            email='second.telegram@example.uz',
            password='MemberPassword!23',
        )
        second_member = CompanyMember.objects.create(
            company=self.company,
            user=second_user,
            role=CompanyMember.Role.VIEWER,
        )

        with self.assertRaises(IntegrityError), transaction.atomic():
            TelegramIdentity.objects.create(
                member=second_member,
                telegram_user_id=123456789,
                username='renamed_user',
                status=TelegramIdentity.Status.VERIFIED,
                verified_at=timezone.now(),
            )

    def test_security_notifications_cannot_be_disabled(self):
        preference = NotificationPreference(
            member=self.member,
            event_type=NotificationPreference.EventType.SECURITY,
            channel=NotificationPreference.Channel.TELEGRAM,
            enabled=False,
        )

        with self.assertRaises(ValidationError):
            preference.full_clean()

    def test_delivery_event_is_idempotent_per_member_and_channel(self):
        payload = {
            'member': self.member,
            'event_key': 'lot:42:deadline:24h',
            'event_type': NotificationPreference.EventType.DEADLINE,
            'channel': NotificationPreference.Channel.TELEGRAM,
        }
        NotificationDelivery.objects.create(**payload)

        with self.assertRaises(IntegrityError), transaction.atomic():
            NotificationDelivery.objects.create(**payload)

    def test_notification_threshold_cannot_exceed_one_hundred(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            NotificationPreference.objects.create(
                member=self.member,
                event_type=NotificationPreference.EventType.MATCHING_LOT,
                channel=NotificationPreference.Channel.TELEGRAM,
                threshold=101,
            )

    def test_pending_identity_can_be_relinked_without_username_identity(self):
        identity = TelegramIdentity.objects.create(
            member=self.member,
            telegram_user_id=987654321,
            username='old_username',
            status=TelegramIdentity.Status.AWAITING_RELINK,
            initialization_context={
                'source': 'settings',
                'expires_at': (
                    timezone.now() + timedelta(minutes=15)
                ).isoformat(),
            },
            relink_requested_at=timezone.now(),
        )

        self.assertEqual(identity.telegram_user_id, 987654321)
        self.assertEqual(identity.status, TelegramIdentity.Status.AWAITING_RELINK)
