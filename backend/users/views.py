"""
TenderHelper — Users Views
==============================
Auth API: OTP yuborish/tasdiqlash, Google OAuth, profil.
"""

import logging

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import CustomUser
from .serializers import (
    SendOTPSerializer,
    VerifyOTPSerializer,
    GoogleAuthSerializer,
    UserProfileSerializer,
    UserUpdateSerializer,
)
from .services.otp_service import generate_otp, verify_otp, send_otp_sms
from .services.google_auth import verify_google_token

logger = logging.getLogger(__name__)


def _get_tokens_for_user(user):
    """JWT token juftligini generatsiya qilish."""
    refresh = RefreshToken.for_user(user)
    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    }


# ══════════════════════════════════════════════════
#  OTP Authentication
# ══════════════════════════════════════════════════

@api_view(['POST'])
@permission_classes([AllowAny])
def send_otp_view(request):
    """
    POST /api/v1/auth/send-otp/
    Telefon raqamiga OTP yuborish.
    """
    serializer = SendOTPSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    phone_number = serializer.validated_data['phone_number']

    # OTP generatsiya
    otp = generate_otp(phone_number)
    if otp is None:
        return Response(
            {'error': 'rate_limit', 'message': 'Iltimos, 1 daqiqa kuting va qayta urinib ko\'ring'},
            status=status.HTTP_429_TOO_MANY_REQUESTS,
        )

    # SMS yuborish
    sent = send_otp_sms(phone_number, otp)
    if not sent:
        return Response(
            {'error': 'sms_failed', 'message': 'SMS yuborishda xatolik yuz berdi'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return Response({
        'message': 'OTP muvaffaqiyatli yuborildi',
        'phone_number': phone_number,
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp_view(request):
    """
    POST /api/v1/auth/verify-otp/
    OTP tasdiqlash → JWT token qaytarish.
    Agar foydalanuvchi yo'q bo'lsa, avtomatik ro'yxatdan o'tkazish.
    """
    serializer = VerifyOTPSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    phone_number = serializer.validated_data['phone_number']
    otp_code = serializer.validated_data['otp']

    # OTP tekshirish
    is_valid, error = verify_otp(phone_number, otp_code)

    if not is_valid:
        error_messages = {
            'otp_expired': 'Kod muddati tugagan. Yangi kod so\'rang',
            'invalid_otp': 'Noto\'g\'ri kod. Qayta kiriting',
            'max_attempts': 'Urinishlar soni tugadi. Yangi kod so\'rang',
        }
        return Response(
            {'error': error, 'message': error_messages.get(error, 'Xatolik')},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Foydalanuvchini topish yoki yaratish
    user, created = CustomUser.objects.get_or_create(
        phone_number=phone_number,
        defaults={
            'auth_provider': 'phone',
            'is_active': True,
        }
    )

    if created:
        logger.info(f"New user registered via OTP: {phone_number}")

    # JWT token qaytarish
    tokens = _get_tokens_for_user(user)
    profile = UserProfileSerializer(user).data

    return Response({
        'tokens': tokens,
        'user': profile,
        'is_new_user': created,  # Frontend — onboarding ko'rsatish uchun
    }, status=status.HTTP_200_OK)


# ══════════════════════════════════════════════════
#  Google OAuth
# ══════════════════════════════════════════════════

@api_view(['POST'])
@permission_classes([AllowAny])
def google_auth_view(request):
    """
    POST /api/v1/auth/google/
    Google ID Token → tasdiqlash → JWT token.
    """
    serializer = GoogleAuthSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    token = serializer.validated_data['token']

    # Google token tekshirish
    google_user = verify_google_token(token)
    if google_user is None:
        return Response(
            {'error': 'invalid_token', 'message': 'Google token noto\'g\'ri yoki muddati tugagan'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Foydalanuvchini topish yoki yaratish
    user, created = CustomUser.objects.get_or_create(
        email=google_user['email'],
        defaults={
            'full_name': google_user.get('name', ''),
            'auth_provider': 'google',
            'is_active': True,
        }
    )

    # Mavjud foydalanuvchi uchun — ismni yangilash (agar bo'sh bo'lsa)
    if not created and not user.full_name and google_user.get('name'):
        user.full_name = google_user['name']
        user.save(update_fields=['full_name'])

    if created:
        logger.info(f"New user registered via Google: {google_user['email']}")

    # JWT token
    tokens = _get_tokens_for_user(user)
    profile = UserProfileSerializer(user).data

    return Response({
        'tokens': tokens,
        'user': profile,
        'is_new_user': created,
    }, status=status.HTTP_200_OK)


# ══════════════════════════════════════════════════
#  User Profile
# ══════════════════════════════════════════════════

@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def user_profile_view(request):
    """
    GET  /api/v1/auth/me/ — Joriy foydalanuvchi profilini olish.
    PATCH /api/v1/auth/me/ — Profilni yangilash.
    """
    user = request.user

    if request.method == 'GET':
        serializer = UserProfileSerializer(user)
        return Response(serializer.data)

    elif request.method == 'PATCH':
        serializer = UserUpdateSerializer(
            user,
            data=request.data,
            partial=True,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            UserProfileSerializer(user).data,
            status=status.HTTP_200_OK,
        )
