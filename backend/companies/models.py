"""
TenderHelper companies models.
"""

import uuid

from django.conf import settings
from django.db import models


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
        ENTERPRISE = 'enterprise', 'Enterprise'

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
        ]

    def __str__(self):
        return self.company_name
