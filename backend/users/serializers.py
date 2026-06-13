"""
TenderHelper — Users Serializers
===================================
Auth va profil uchun serializerlar.
"""

from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework import serializers

from companies.models import CompanyProfile
from .models import CustomUser


class SendOTPSerializer(serializers.Serializer):
    """Telefon raqamini qabul qilish — OTP yuborish uchun."""
    phone_number = serializers.CharField(
        max_length=15,
        help_text="O'zbekiston formati: +998XXXXXXXXX"
    )

    def validate_phone_number(self, value):
        cleaned = value.replace('+', '').replace(' ', '').replace('-', '')
        if not cleaned.startswith('998') or len(cleaned) != 12:
            raise serializers.ValidationError(
                "Noto'g'ri telefon raqami. Format: +998XXXXXXXXX"
            )
        return f'+{cleaned}'


class VerifyOTPSerializer(serializers.Serializer):
    """OTP kodni tekshirish."""
    phone_number = serializers.CharField(max_length=15)
    otp = serializers.CharField(max_length=6, min_length=6)

    def validate_phone_number(self, value):
        cleaned = value.replace('+', '').replace(' ', '').replace('-', '')
        if not cleaned.startswith('998') or len(cleaned) != 12:
            raise serializers.ValidationError(
                "Noto'g'ri telefon raqami. Format: +998XXXXXXXXX"
            )
        return f'+{cleaned}'

    def validate_otp(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("OTP faqat raqamlardan iborat bo'lishi kerak")
        return value


class GoogleAuthSerializer(serializers.Serializer):
    """Google ID Token qabul qilish."""
    token = serializers.CharField(
        help_text="Google OAuth2 ID Token"
    )


class EmailRegisterSerializer(serializers.ModelSerializer):
    """Account va kompaniya profilini birga ro'yxatdan o'tkazish."""
    password = serializers.CharField(write_only=True, min_length=8)
    phone_number = serializers.CharField(required=False, allow_blank=True, max_length=15)
    company_name = serializers.CharField(write_only=True, max_length=500)
    company_type = serializers.ChoiceField(
        write_only=True,
        choices=CompanyProfile.CompanyType.choices,
        default=CompanyProfile.CompanyType.MCHJ,
    )
    industry = serializers.CharField(write_only=True, max_length=255)
    experience_level = serializers.ChoiceField(
        write_only=True,
        choices=CompanyProfile.ExperienceLevel.choices,
        default=CompanyProfile.ExperienceLevel.BEGINNER,
    )
    stir = serializers.CharField(write_only=True, required=False, allow_blank=True, max_length=9)
    has_vat = serializers.BooleanField(write_only=True, required=False, default=False)
    business_type = serializers.ChoiceField(
        write_only=True,
        required=False,
        choices=[
            ('supplier', 'Yetkazib beruvchi'),
            ('customer', 'Xaridor'),
            ('both', 'Ikkalasi ham'),
        ],
        default='supplier',
    )
    tender_keywords = serializers.CharField(write_only=True, required=False, allow_blank=True)
    target_regions = serializers.ListField(
        write_only=True,
        required=False,
        child=serializers.CharField(max_length=100),
        default=list,
    )
    annual_tender_volume = serializers.ChoiceField(
        write_only=True,
        required=False,
        choices=[
            ('first_time', 'Tenderlarda yangi'),
            ('1_5', 'Yiliga 1-5 ta'),
            ('6_20', 'Yiliga 6-20 ta'),
            ('20_plus', 'Yiliga 20+ ta'),
        ],
        default='first_time',
    )

    class Meta:
        model = CustomUser
        fields = [
            'email',
            'password',
            'full_name',
            'phone_number',
            'company_name',
            'company_type',
            'industry',
            'experience_level',
            'stir',
            'has_vat',
            'business_type',
            'tender_keywords',
            'target_regions',
            'annual_tender_volume',
        ]
        extra_kwargs = {
            'email': {'required': True, 'allow_blank': False},
            'full_name': {'required': True, 'allow_blank': False}
        }

    def validate_email(self, value):
        value = CustomUser.objects.normalize_email(value).lower()
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Bu email allaqachon ro'yxatdan o'tgan")
        return value

    def validate_password(self, value):
        validate_password(value)
        return value

    def validate_phone_number(self, value):
        if not value:
            return None
        cleaned = value.replace('+', '').replace(' ', '').replace('-', '')
        if not cleaned.startswith('998') or len(cleaned) != 12:
            raise serializers.ValidationError("Telefon raqami formati: +998XXXXXXXXX")
        phone_number = f'+{cleaned}'
        if CustomUser.objects.filter(phone_number=phone_number).exists():
            raise serializers.ValidationError("Bu telefon raqami allaqachon ishlatilgan")
        return phone_number

    def validate_stir(self, value):
        if value in ('', None):
            return None
        if not value.isdigit() or len(value) != 9:
            raise serializers.ValidationError("STIR 9 ta raqamdan iborat bo'lishi kerak")
        if CompanyProfile.objects.filter(stir=value).exists():
            raise serializers.ValidationError("Bu STIR bo'yicha kompaniya profili mavjud")
        return value

    @transaction.atomic
    def create(self, validated_data):
        company_data = {
            'company_name': validated_data.pop('company_name'),
            'company_type': validated_data.pop('company_type'),
            'industry': validated_data.pop('industry'),
            'experience_level': validated_data.pop('experience_level'),
            'stir': validated_data.pop('stir', None),
            'has_vat': validated_data.pop('has_vat', False),
        }
        onboarding_answers = {
            'business_type': validated_data.pop('business_type', 'supplier'),
            'tender_keywords': validated_data.pop('tender_keywords', ''),
            'target_regions': validated_data.pop('target_regions', []),
            'annual_tender_volume': validated_data.pop('annual_tender_volume', 'first_time'),
        }
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            full_name=validated_data['full_name'],
            phone_number=validated_data.get('phone_number'),
            auth_provider='email'
        )
        CompanyProfile.objects.create(
            user=user,
            onboarding_answers=onboarding_answers,
            **company_data,
        )
        return user


class EmailLoginSerializer(serializers.Serializer):
    """Email va parol orqali kirish."""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class UserProfileSerializer(serializers.ModelSerializer):
    """Foydalanuvchi profili — o'qish uchun."""
    display_name = serializers.ReadOnlyField()

    class Meta:
        model = CustomUser
        fields = [
            'id',
            'phone_number',
            'email',
            'full_name',
            'display_name',
            'role',
            'auth_provider',
            'date_joined',
            'updated_at',
        ]
        read_only_fields = [
            'id', 'date_joined', 'updated_at',
            'role', 'auth_provider',
        ]


class UserUpdateSerializer(serializers.ModelSerializer):
    """Foydalanuvchi profilini yangilash."""

    class Meta:
        model = CustomUser
        fields = ['full_name', 'email', 'phone_number']

    def validate_email(self, value):
        user = self.context.get('request').user
        if CustomUser.objects.filter(email=value).exclude(id=user.id).exists():
            raise serializers.ValidationError("Bu email allaqachon ishlatilgan")
        return value
