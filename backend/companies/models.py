"""
TenderHelper companies models.
"""

import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone


class CompanyProfile(models.Model):
    """Korxona raqamli dosyasi."""

    class CompanyType(models.TextChoices):
        YATT = 'yatt', 'YaTT'
        MCHJ = 'mchj', 'MChJ'
        AJ = 'aj', 'AJ'
        TT = 'tt', 'TT'

    class ExperienceLevel(models.TextChoices):
        BEGINNER = 'beginner', 'Yangi boshlovchi'
        INTERMEDIATE = 'intermediate', "O'rtacha"
        EXPERT = 'expert', 'Professional'

    class Tariff(models.TextChoices):
        FREE = 'free', 'Free'
        PRO = 'pro', 'Pro'
        BUSINESS = 'business', 'Business'
        ENTERPRISE = 'enterprise', 'Enterprise'

    class RegistrySource(models.TextChoices):
        MANUAL = 'manual', "Qo'lda kiritilgan"
        TAX = 'tax', 'Soliq reyestri'
        STATISTICS = 'statistics', 'Statistika reyestri'

    class RegistryStatus(models.TextChoices):
        NOT_CHECKED = 'not_checked', 'Tekshirilmagan'
        PENDING = 'pending', 'Tekshirilmoqda'
        VERIFIED = 'verified', 'Tasdiqlangan'
        NOT_FOUND = 'not_found', 'Topilmadi'
        FAILED = 'failed', 'Tekshiruv xatosi'
        MANUAL = 'manual', "Qo'lda kiritilgan"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='company_profiles',
    )
    stir = models.CharField(max_length=9, unique=True, null=True, blank=True)
    company_name = models.CharField(max_length=500)
    company_type = models.CharField(
        max_length=20,
        choices=CompanyType.choices,
        default=CompanyType.MCHJ,
    )
    industry = models.CharField(max_length=255)
    experience_level = models.CharField(
        max_length=20,
        choices=ExperienceLevel.choices,
        default=ExperienceLevel.BEGINNER,
    )
    registration_date = models.DateField(null=True, blank=True)
    ustav_fondi = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    has_vat = models.BooleanField(default=False)
    director_name = models.CharField(max_length=255, blank=True, default='')
    legal_address = models.TextField(blank=True, default='')
    stir_skipped = models.BooleanField(default=False)
    registry_source = models.CharField(
        max_length=20,
        choices=RegistrySource.choices,
        default=RegistrySource.MANUAL,
    )
    registry_status = models.CharField(
        max_length=20,
        choices=RegistryStatus.choices,
        default=RegistryStatus.NOT_CHECKED,
    )
    registry_fetched_at = models.DateTimeField(null=True, blank=True)
    current_tariff = models.CharField(
        max_length=20,
        choices=Tariff.choices,
        default=Tariff.FREE,
    )
    tariff_expires_at = models.DateTimeField(null=True, blank=True)
    onboarding_answers = models.JSONField(default=dict, blank=True)
    raw_tax_data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'company_profiles'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'current_tariff']),
            models.Index(fields=['industry']),
            models.Index(fields=['registry_status', 'registry_source']),
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(stir__isnull=True) | Q(stir_skipped=False),
                name='company_stir_not_skipped',
            ),
            models.CheckConstraint(
                condition=Q(stir__isnull=True) | Q(stir__regex=r'^[0-9]{9}$'),
                name='company_stir_format',
            ),
        ]

    def __str__(self):
        return self.company_name

    @property
    def has_stir_identity(self):
        return bool(self.stir) and not self.stir_skipped

    def clean(self):
        super().clean()
        if self.stir and self.stir_skipped:
            raise ValidationError({
                'stir_skipped': "STIR mavjud profilni STIRsiz deb belgilash mumkin emas.",
            })


class CompanyRegistryDraft(models.Model):
    """Registry lookup result that requires explicit user confirmation."""

    class Status(models.TextChoices):
        PENDING = 'pending', 'Kutilmoqda'
        READY = 'ready', 'Tasdiqlashga tayyor'
        CONFIRMED = 'confirmed', 'Tasdiqlangan'
        EXPIRED = 'expired', 'Muddati tugagan'
        FAILED = 'failed', 'Xatolik'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='company_registry_drafts',
    )
    profile = models.ForeignKey(
        CompanyProfile,
        on_delete=models.SET_NULL,
        related_name='registry_drafts',
        null=True,
        blank=True,
    )
    stir = models.CharField(max_length=9)
    normalized_data = models.JSONField(default=dict, blank=True)
    confirmed_data = models.JSONField(default=dict, blank=True)
    raw_payload = models.JSONField(default=dict, blank=True)
    provider = models.CharField(max_length=100)
    source = models.CharField(
        max_length=20,
        choices=CompanyProfile.RegistrySource.choices,
        default=CompanyProfile.RegistrySource.MANUAL,
    )
    lookup_metadata = models.JSONField(default=dict, blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    error_code = models.CharField(max_length=50, blank=True, default='')
    error_message = models.CharField(max_length=500, blank=True, default='')
    cache_hit = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    confirmed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'company_registry_drafts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['provider', 'stir']),
            models.Index(fields=['expires_at']),
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(stir__regex=r'^[0-9]{9}$'),
                name='registry_draft_stir_format',
            ),
        ]

    def __str__(self):
        return f'{self.provider}:{self.stir}:{self.status}'

    @property
    def is_expired(self):
        return self.status not in {
            self.Status.CONFIRMED,
            self.Status.EXPIRED,
        } and self.expires_at <= timezone.now()
