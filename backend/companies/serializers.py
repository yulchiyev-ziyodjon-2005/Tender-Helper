from dataclasses import asdict

from rest_framework import serializers

from .features import get_company_feature_access
from .models import CompanyProfile, CompanyRegistryDraft


class CompanyProfileSerializer(serializers.ModelSerializer):
    feature_access = serializers.SerializerMethodField()

    class Meta:
        model = CompanyProfile
        fields = [
            'id',
            'stir',
            'stir_skipped',
            'company_name',
            'company_type',
            'industry',
            'experience_level',
            'registration_date',
            'ustav_fondi',
            'has_vat',
            'director_name',
            'legal_address',
            'registry_source',
            'registry_status',
            'registry_fetched_at',
            'current_tariff',
            'tariff_expires_at',
            'onboarding_answers',
            'feature_access',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'current_tariff',
            'tariff_expires_at',
            'stir_skipped',
            'registry_source',
            'registry_status',
            'registry_fetched_at',
            'feature_access',
            'created_at',
            'updated_at',
        ]

    def validate_stir(self, value):
        if value in ('', None):
            return None
        if not value.isdigit() or len(value) != 9:
            raise serializers.ValidationError("STIR 9 ta raqamdan iborat bo'lishi kerak")
        return value

    def validate(self, attrs):
        stir = attrs.get('stir', getattr(self.instance, 'stir', None))
        stir_skipped = attrs.get(
            'stir_skipped',
            getattr(self.instance, 'stir_skipped', False),
        )
        if stir and stir_skipped:
            raise serializers.ValidationError({
                'stir': "STIR mavjud profil STIRsiz deb belgilanishi mumkin emas.",
            })
        return attrs

    def create(self, validated_data):
        self._set_manual_registry_state(validated_data, instance=None)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        self._set_manual_registry_state(validated_data, instance=instance)
        return super().update(instance, validated_data)

    def get_feature_access(self, obj):
        return asdict(get_company_feature_access(obj))

    @staticmethod
    def _set_manual_registry_state(validated_data, instance):
        if 'stir' not in validated_data:
            return
        stir = validated_data['stir']
        is_same_verified_stir = bool(
            instance
            and stir
            and stir == instance.stir
            and instance.registry_status == CompanyProfile.RegistryStatus.VERIFIED
        )
        validated_data['stir_skipped'] = False
        if is_same_verified_stir:
            return
        validated_data['registry_source'] = CompanyProfile.RegistrySource.MANUAL
        validated_data['registry_status'] = (
            CompanyProfile.RegistryStatus.MANUAL
            if stir
            else CompanyProfile.RegistryStatus.NOT_CHECKED
        )
        validated_data['registry_fetched_at'] = None
        validated_data['raw_tax_data'] = {}


class OnboardingSerializer(CompanyProfileSerializer):
    class Meta(CompanyProfileSerializer.Meta):
        read_only_fields = CompanyProfileSerializer.Meta.read_only_fields


class RegistryLookupSerializer(serializers.Serializer):
    stir = serializers.CharField(max_length=9, min_length=9)

    def validate_stir(self, value):
        value = value.strip()
        if len(value) != 9 or not value.isdigit():
            raise serializers.ValidationError(
                "STIR 9 ta raqamdan iborat bo'lishi kerak"
            )
        return value


class RegistryDraftSerializer(serializers.ModelSerializer):
    profile_id = serializers.UUIDField(read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    manual_entry_allowed = serializers.SerializerMethodField()

    class Meta:
        model = CompanyRegistryDraft
        fields = [
            'id',
            'profile_id',
            'stir',
            'normalized_data',
            'confirmed_data',
            'provider',
            'source',
            'status',
            'error_code',
            'error_message',
            'cache_hit',
            'lookup_metadata',
            'is_expired',
            'manual_entry_allowed',
            'expires_at',
            'confirmed_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields

    def get_manual_entry_allowed(self, obj):
        return obj.status in {
            CompanyRegistryDraft.Status.FAILED,
            CompanyRegistryDraft.Status.EXPIRED,
        }


class RegistryConfirmSerializer(serializers.Serializer):
    company_name = serializers.CharField(max_length=500)
    company_type = serializers.ChoiceField(choices=CompanyProfile.CompanyType.choices)
    industry = serializers.CharField(max_length=255)
    experience_level = serializers.ChoiceField(
        choices=CompanyProfile.ExperienceLevel.choices,
        default=CompanyProfile.ExperienceLevel.BEGINNER,
    )
    director_name = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
        default='',
    )
    legal_address = serializers.CharField(
        required=False,
        allow_blank=True,
        default='',
    )
    registration_date = serializers.DateField(required=False, allow_null=True)
    has_vat = serializers.BooleanField(required=False, default=False)


class SkipStirSerializer(serializers.Serializer):
    company_name = serializers.CharField(max_length=500, required=False)
    company_type = serializers.ChoiceField(
        choices=CompanyProfile.CompanyType.choices,
        required=False,
        default=CompanyProfile.CompanyType.MCHJ,
    )
    industry = serializers.CharField(max_length=255, required=False)
    experience_level = serializers.ChoiceField(
        choices=CompanyProfile.ExperienceLevel.choices,
        required=False,
        default=CompanyProfile.ExperienceLevel.BEGINNER,
    )
    director_name = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
        default='',
    )
    legal_address = serializers.CharField(
        required=False,
        allow_blank=True,
        default='',
    )
    registration_date = serializers.DateField(required=False, allow_null=True)
    has_vat = serializers.BooleanField(required=False, default=False)
    onboarding_answers = serializers.JSONField(required=False, default=dict)

    def validate(self, attrs):
        profile = self.context.get('profile')
        if profile is None:
            missing = [
                field
                for field in ('company_name', 'industry')
                if not attrs.get(field)
            ]
            if missing:
                raise serializers.ValidationError({
                    field: 'This field is required when creating a profile.'
                    for field in missing
                })
        return attrs
