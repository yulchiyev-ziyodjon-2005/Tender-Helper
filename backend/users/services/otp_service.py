"""
TenderHelper — OTP Service
=============================
6 raqamli SMS kod generatsiyasi, saqlash va tekshirish.
MVP: console'ga chiqarish (real SMS keyinroq — Eskiz.uz).
"""

import logging
import secrets

from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

# ──────────── Konfiguratsiya ────────────
OTP_LENGTH = getattr(settings, 'OTP_LENGTH', 6)
OTP_EXPIRY_MINUTES = getattr(settings, 'OTP_EXPIRY_MINUTES', 3)
OTP_MAX_ATTEMPTS = 5  # Bitta raqamga maksimum urinishlar


def _cache_key(phone_number, suffix='otp'):
    """Cache kalitini generatsiya qilish."""
    cleaned = phone_number.replace('+', '').replace(' ', '')
    return f'tenderhelper:{suffix}:{cleaned}'


def generate_otp(phone_number):
    """
    Yangi OTP generatsiya qilib, cache'ga saqlash.

    Returns:
        str: 6 raqamli OTP kod
        yoki None agar rate limit bo'lsa
    """
    rate_key = _cache_key(phone_number, 'rate')
    otp_key = _cache_key(phone_number, 'otp')
    attempts_key = _cache_key(phone_number, 'attempts')

    # Rate limiting: 1 daqiqada 1 ta OTP
    if cache.get(rate_key):
        logger.warning(f"OTP rate limit: {phone_number}")
        return None

    # OTP generatsiya
    otp = ''.join(str(secrets.randbelow(10)) for _ in range(OTP_LENGTH))

    # Cache'ga saqlash (3 daqiqa amal muddati)
    expiry_seconds = OTP_EXPIRY_MINUTES * 60
    cache.set(otp_key, otp, timeout=expiry_seconds)

    # Rate limit: 60 soniya
    cache.set(rate_key, True, timeout=60)

    # Urinishlar hisoblagichini tozalash
    cache.set(attempts_key, 0, timeout=expiry_seconds)

    logger.info(f"OTP generated for {phone_number}")

    return otp


def verify_otp(phone_number, submitted_otp):
    """
    Kiritilgan OTP ni tekshirish.

    Returns:
        tuple: (is_valid: bool, error_message: str | None)
    """
    otp_key = _cache_key(phone_number, 'otp')
    attempts_key = _cache_key(phone_number, 'attempts')

    # Saqlangan OTP ni olish
    stored_otp = cache.get(otp_key)

    if stored_otp is None:
        return False, 'otp_expired'  # Muddati tugagan yoki yuborilmagan

    # Urinishlar hisobi
    attempts = cache.get(attempts_key, 0)
    if attempts >= OTP_MAX_ATTEMPTS:
        cache.delete(otp_key)
        cache.delete(attempts_key)
        return False, 'max_attempts'

    # Tekshirish
    if str(submitted_otp) == str(stored_otp):
        # Muvaffaqiyat — cache'dan tozalash
        cache.delete(otp_key)
        cache.delete(attempts_key)
        logger.info(f"OTP verified for {phone_number}")
        return True, None
    else:
        # Noto'g'ri — urinishni oshirish
        cache.set(attempts_key, attempts + 1, timeout=OTP_EXPIRY_MINUTES * 60)
        remaining = OTP_MAX_ATTEMPTS - attempts - 1
        logger.warning(f"Invalid OTP for {phone_number}. {remaining} attempts left.")
        return False, 'invalid_otp'


def send_otp_sms(phone_number, otp):
    """
    OTP ni SMS orqali yuborish.
    MVP: console'ga chiqarish.
    Production: Eskiz.uz API orqali.
    """
    provider = getattr(settings, 'SMS_PROVIDER', 'console')

    if provider == 'console':
        # ──── Development: console'ga chiqarish ────
        logger.info("OTP accepted by console provider for %s", phone_number)
        return True

    elif provider == 'eskiz':
        # ──── Production: Eskiz.uz API ────
        return _send_via_eskiz(phone_number, otp)

    else:
        logger.error(f"Unknown SMS provider: {provider}")
        return False


def _send_via_eskiz(phone_number, otp):
    """Eskiz.uz API orqali SMS yuborish."""
    import requests

    try:
        # Eskiz token olish
        auth_url = f"{settings.ESKIZ_API_URL}/auth/login"
        auth_response = requests.post(auth_url, data={
            'email': settings.ESKIZ_EMAIL,
            'password': settings.ESKIZ_PASSWORD,
        }, timeout=10)

        if auth_response.status_code != 200:
            logger.error(f"Eskiz auth failed: {auth_response.text}")
            return False

        token = auth_response.json().get('data', {}).get('token')

        # SMS yuborish
        sms_url = f"{settings.ESKIZ_API_URL}/message/sms/send"
        sms_response = requests.post(sms_url, data={
            'mobile_phone': phone_number.replace('+', ''),
            'message': f"TenderHelper tasdiqlash kodi: {otp}. {OTP_EXPIRY_MINUTES} daqiqa ichida kiriting.",
            'from': '4546',
        }, headers={
            'Authorization': f'Bearer {token}',
        }, timeout=10)

        if sms_response.status_code == 200:
            logger.info(f"Eskiz SMS sent to {phone_number}")
            return True
        else:
            logger.error(f"Eskiz SMS failed: {sms_response.text}")
            return False

    except requests.RequestException as e:
        logger.error(f"Eskiz request error: {e}")
        return False
