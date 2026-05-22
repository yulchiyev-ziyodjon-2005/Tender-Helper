"""
TenderHelper — Users Serializers
===================================
Auth va profil uchun serializerlar.
"""

from rest_framework import serializers
from .models import CustomUser


class SendOTPSerializer(serializers.Serializer):
    """Telefon raqamini qabul qilish — OTP yuborish uchun."""
    phone_number = serializers.CharField(
        max_length=15,
        help_text="O'zbekiston formati: +998XXXXXXXXX"
    )

    def validate_phone_number(self, value):
        """Telefon raqami validatsiyasi."""
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
        fields = ['full_name', 'email']

    def validate_email(self, value):
        user = self.context.get('request').user
        if CustomUser.objects.filter(email=value).exclude(id=user.id).exists():
            raise serializers.ValidationError("Bu email allaqachon ishlatilgan")
        return value
