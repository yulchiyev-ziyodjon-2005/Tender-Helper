from rest_framework import serializers

from .models import CompanyProfile


class CompanyProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyProfile
        fields = [
            'id',
            'stir',
            'company_name',
            'company_type',
            'industry',
            'experience_level',
            'registration_date',
            'ustav_fondi',
            'has_vat',
            'current_tariff',
            'tariff_expires_at',
            'onboarding_answers',
            'raw_tax_data',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'current_tariff',
            'tariff_expires_at',
            'raw_tax_data',
            'created_at',
            'updated_at',
        ]

    def validate_stir(self, value):
        if value in ('', None):
            return None
        if not value.isdigit() or len(value) != 9:
            raise serializers.ValidationError("STIR 9 ta raqamdan iborat bo'lishi kerak")
        return value


class OnboardingSerializer(CompanyProfileSerializer):
    class Meta(CompanyProfileSerializer.Meta):
        read_only_fields = ['id', 'current_tariff', 'tariff_expires_at', 'raw_tax_data']
