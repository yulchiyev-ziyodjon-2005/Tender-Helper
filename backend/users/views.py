"""
TenderHelper — Users Views
==============================
Auth API: OTP yuborish/tasdiqlash, Google OAuth, profil.
"""

import logging
import secrets
from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core import signing
from django.core.cache import cache
from django.core.mail import send_mail
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.shortcuts import redirect
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from companies.serializers import CompanyProfileSerializer
from .models import CustomUser
from .serializers import (
    EmailLoginSerializer,
    EmailRegisterSerializer,
    ChangePasswordSerializer,
    ForgotPasswordSerializer,
    GoogleAuthSerializer,
    ResetPasswordSerializer,
    SendOTPSerializer,
    UserProfileSerializer,
    UserUpdateSerializer,
    VerifyOTPSerializer,
)
from .services.otp_service import generate_otp, verify_otp, send_otp_sms
from .services.google_auth import verify_google_token
from .services.google_oauth import (
    build_google_authorization_url,
    exchange_code_for_user_info,
    is_google_oauth_configured,
)
from .services.session_capabilities import build_session_capabilities

logger = logging.getLogger(__name__)
GOOGLE_EXCHANGE_TTL_SECONDS = 120


def _get_tokens_for_user(user):
    """JWT token juftligini generatsiya qilish."""
    refresh = RefreshToken.for_user(user)
    refresh['auth_version'] = user.auth_version
    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    }


def _get_primary_company(user):
    from subscriptions.services.membership import accessible_companies

    return accessible_companies(user).order_by('-created_at').first()


def _auth_payload(user, is_new_user):
    company = _get_primary_company(user)
    force_password_change = user.company_memberships.filter(
        is_active=True,
        force_password_change=True,
    ).exists()
    return {
        'tokens': _get_tokens_for_user(user),
        'user': UserProfileSerializer(user).data,
        'company': CompanyProfileSerializer(company).data if company else None,
        'is_new_user': is_new_user,
        'force_password_change': force_password_change,
    }


def _frontend_redirect(path, params=None):
    url = f"{settings.FRONTEND_BASE_URL}{path}"
    if params:
        url = f"{url}?{urlencode(params)}"
    return redirect(url)


def _get_google_redirect_uri(request):
    return request.build_absolute_uri('/api/v1/auth/google/callback/')


def _get_or_create_google_user(google_user):
    user, created = CustomUser.objects.get_or_create(
        email=google_user['email'],
        defaults={
            'full_name': google_user.get('name', ''),
            'auth_provider': 'google',
            'is_active': True,
        }
    )

    update_fields = []
    if not user.full_name and google_user.get('name'):
        user.full_name = google_user['name']
        update_fields.append('full_name')
    if user.auth_provider != 'google':
        user.auth_provider = 'google'
        update_fields.append('auth_provider')
    if update_fields:
        user.save(update_fields=update_fields)

    return user, created


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

    # Foydalanuvchini topish yoki yaratish (yoki ulash)
    user_req = getattr(request, 'user', None)
    
    if user_req and user_req.is_authenticated:
        if CustomUser.objects.filter(phone_number=phone_number).exclude(id=user_req.id).exists():
            return Response(
                {'error': 'phone_used', 'message': 'Bu raqam allaqachon boshqa profilga ulangan'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = user_req
        user.phone_number = phone_number
        user.save(update_fields=['phone_number'])
        created = False
        logger.info(f"User {user.email} linked phone: {phone_number}")
    else:
        user, created = CustomUser.objects.get_or_create(
            phone_number=phone_number,
            defaults={
                'auth_provider': 'phone',
                'is_active': True,
            }
        )

    if created:
        logger.info(f"New user registered via OTP: {phone_number}")

    return Response(_auth_payload(user, created), status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_registration_phone_view(request):
    """Verify an OTP without creating a user and return a registration proof."""
    serializer = VerifyOTPSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    phone_number = serializer.validated_data['phone_number']
    otp_code = serializer.validated_data['otp']

    is_valid, error = verify_otp(phone_number, otp_code)
    if not is_valid:
        error_messages = {
            'otp_expired': "Kod muddati tugagan. Yangi kod so'rang",
            'invalid_otp': "Noto'g'ri kod. Qayta kiriting",
            'max_attempts': "Urinishlar soni tugadi. Yangi kod so'rang",
        }
        return Response(
            {'error': error, 'message': error_messages.get(error, 'Xatolik')},
            status=status.HTTP_400_BAD_REQUEST,
        )

    verification_token = signing.dumps(
        {'phone_number': phone_number, 'purpose': 'register'},
        salt='registration-phone-verification',
        compress=True,
    )
    return Response({
        'phone_number': phone_number,
        'verification_token': verification_token,
        'expires_in': 10 * 60,
    })


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

    user, created = _get_or_create_google_user(google_user)

    # Mavjud foydalanuvchi uchun — ismni yangilash (agar bo'sh bo'lsa)
    if not user.is_active:
        return Response(
            {'error': 'inactive_user', 'message': 'Foydalanuvchi bloklangan'},
            status=status.HTTP_403_FORBIDDEN,
        )

    if created:
        logger.info(f"New user registered via Google: {google_user['email']}")

    return Response(_auth_payload(user, created), status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def google_oauth_config_view(request):
    """
    GET /api/v1/auth/google/config/
    Frontend Google login holatini tekshirishi uchun.
    """
    enabled = is_google_oauth_configured()
    return Response({
        'enabled': enabled,
        'start_url': '/api/v1/auth/google/start/',
        'message': '' if enabled else 'Google OAuth sozlanmoqda',
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def google_oauth_start_view(request):
    """
    GET /api/v1/auth/google/start/
    An'anaviy Google OAuth account chooser sahifasiga redirect qiladi.
    """
    if not is_google_oauth_configured():
        return _frontend_redirect('/login', {
            'google_error': "Google OAuth sozlanmagan. GOOGLE_CLIENT_ID va GOOGLE_CLIENT_SECRET ni kiriting.",
        })

    next_path = request.query_params.get('next') or '/dashboard'
    state = signing.dumps({'next': next_path}, salt='google-oauth-state')
    auth_url = build_google_authorization_url(_get_google_redirect_uri(request), state)
    return redirect(auth_url)


@api_view(['GET'])
@permission_classes([AllowAny])
def google_oauth_callback_view(request):
    """
    GET /api/v1/auth/google/callback/
    Google authorization code'ni token/id_token'ga almashtirib JWT qaytaradi.
    """
    error = request.query_params.get('error')
    if error:
        return _frontend_redirect('/login', {'google_error': error})

    code = request.query_params.get('code')
    state = request.query_params.get('state')
    if not code or not state:
        return _frontend_redirect('/login', {'google_error': 'Google callback noto\'liq qaytdi'})

    try:
        state_data = signing.loads(state, salt='google-oauth-state', max_age=600)
    except signing.BadSignature:
        return _frontend_redirect('/login', {'google_error': 'Google sessiya muddati tugagan'})

    try:
        google_user = exchange_code_for_user_info(code, _get_google_redirect_uri(request))
    except Exception as exc:
        logger.exception('Google OAuth callback failed: %s', exc)
        return _frontend_redirect('/login', {'google_error': 'Google orqali kirishda xatolik yuz berdi'})

    if google_user is None:
        return _frontend_redirect('/login', {'google_error': 'Google token noto\'g\'ri yoki email tasdiqlanmagan'})

    user, created = _get_or_create_google_user(google_user)
    if not user.is_active:
        return _frontend_redirect('/login', {'google_error': 'Foydalanuvchi bloklangan'})

    if created:
        logger.info(f"New user registered via Google OAuth redirect: {google_user['email']}")

    next_path = state_data.get('next') or '/dashboard'
    if created:
        next_path = '/onboarding'

    exchange_code = secrets.token_urlsafe(32)
    cache.set(
        f'tenderhelper:google-exchange:{exchange_code}',
        {
            'user_id': str(user.id),
            'is_new_user': created,
            'next': next_path,
        },
        timeout=GOOGLE_EXCHANGE_TTL_SECONDS,
    )

    return _frontend_redirect('/auth/google/callback', {
        'code': exchange_code,
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def google_oauth_exchange_view(request):
    code = request.data.get('code')
    if not isinstance(code, str) or not code:
        return Response(
            {'error': 'invalid_code', 'message': 'Google exchange kodi kiritilmagan'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    cache_key = f'tenderhelper:google-exchange:{code}'
    exchange = cache.get(cache_key)
    cache.delete(cache_key)
    if exchange is None:
        return Response(
            {'error': 'invalid_code', 'message': 'Google exchange kodi yaroqsiz yoki muddati tugagan'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = CustomUser.objects.filter(id=exchange['user_id'], is_active=True).first()
    if user is None:
        return Response(
            {'error': 'inactive_user', 'message': 'Foydalanuvchi topilmadi yoki bloklangan'},
            status=status.HTTP_403_FORBIDDEN,
        )

    payload = _auth_payload(user, exchange['is_new_user'])
    payload['next'] = exchange['next']
    return Response(payload, status=status.HTTP_200_OK)


# ══════════════════════════════════════════════════
#  Email Authentication
# ══════════════════════════════════════════════════

@api_view(['POST'])
@permission_classes([AllowAny])
def email_register_view(request):
    """
    POST /api/v1/auth/register/
    Email orqali ro'yxatdan o'tish.
    """
    serializer = EmailRegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    
    logger.info(f"New user registered via Email: {user.email}")
    
    return Response(_auth_payload(user, True), status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([AllowAny])
def email_login_view(request):
    """
    POST /api/v1/auth/login/
    Email va parol orqali kirish.
    """
    serializer = EmailLoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    email = serializer.validated_data['email'].lower()
    password = serializer.validated_data['password']
    
    # Authenticate (uses phone or email depending on backend, but we need email auth)
    # By default, Django's authenticate uses the USERNAME_FIELD. 
    # Let's handle it manually if custom auth backend is not fully setup for email.
    try:
        user = CustomUser.objects.get(email__iexact=email)
        if not user.check_password(password):
            return Response({'error': 'invalid_credentials', 'message': 'Email yoki parol noto\'g\'ri'}, status=status.HTTP_400_BAD_REQUEST)
    except CustomUser.DoesNotExist:
        return Response({'error': 'invalid_credentials', 'message': 'Email yoki parol noto\'g\'ri'}, status=status.HTTP_400_BAD_REQUEST)

    if not user.is_active:
        return Response({'error': 'inactive_user', 'message': 'Foydalanuvchi bloklangan'}, status=status.HTTP_403_FORBIDDEN)
        
    return Response(_auth_payload(user, False), status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password_view(request):
    serializer = ForgotPasswordSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.validated_data['email'].lower()
    user = CustomUser.objects.filter(email__iexact=email, is_active=True).first()

    if user and user.has_usable_password():
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        reset_url = f'{settings.FRONTEND_BASE_URL}/reset-password?uid={uid}&token={token}'
        send_mail(
            subject='TenderHelper parolini tiklash',
            message=(
                "Parolingizni yangilash uchun quyidagi havolani oching:\n\n"
                f"{reset_url}\n\n"
                "Agar bu so'rovni siz yubormagan bo'lsangiz, xabarni e'tiborsiz qoldiring."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

    return Response({
        'message': "Agar email ro'yxatdan o'tgan bo'lsa, tiklash havolasi yuborildi.",
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password_view(request):
    serializer = ResetPasswordSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    try:
        user_id = force_str(urlsafe_base64_decode(serializer.validated_data['uid']))
        user = CustomUser.objects.get(pk=user_id, is_active=True)
    except (ValueError, TypeError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user is None or not default_token_generator.check_token(
        user,
        serializer.validated_data['token'],
    ):
        return Response(
            {'error': 'invalid_token', 'message': "Tiklash havolasi yaroqsiz yoki muddati tugagan."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user.set_password(serializer.validated_data['new_password'])
    user.auth_version += 1
    user.save(update_fields=['password', 'auth_version', 'updated_at'])
    return Response({'message': 'Parol muvaffaqiyatli yangilandi.'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password_view(request):
    serializer = ChangePasswordSerializer(
        data=request.data,
        context={'request': request},
    )
    serializer.is_valid(raise_exception=True)
    user = request.user
    user.set_password(serializer.validated_data['new_password'])
    user.auth_version += 1
    user.save(update_fields=['password', 'auth_version', 'updated_at'])
    user.company_memberships.filter(
        is_active=True,
        force_password_change=True,
    ).update(force_password_change=False)
    return Response(_auth_payload(user, False))


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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def session_capabilities_view(request):
    """
    GET /api/v1/auth/session/ - UI bootstrap uchun role, permission,
    entitlement, usage va navigation holatini qaytaradi.
    """
    payload = build_session_capabilities(
        request.user,
        company_id=request.query_params.get('company_id'),
    )
    if payload is None:
        return Response(
            {
                'code': 'company_not_found',
                'message': 'Kompaniya topilmadi yoki sizga tegishli emas.',
                'details': {},
            },
            status=status.HTTP_404_NOT_FOUND,
        )
    return Response(payload)
