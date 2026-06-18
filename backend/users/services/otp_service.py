import logging
import secrets

from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

OTP_LENGTH = getattr(settings, 'OTP_LENGTH', 6)
OTP_EXPIRY_MINUTES = getattr(settings, 'OTP_EXPIRY_MINUTES', 3)
OTP_MAX_ATTEMPTS = 5
ESKIZ_TOKEN_CACHE_KEY = 'tenderhelper:sms:eskiz:token'
ESKIZ_TOKEN_TIMEOUT_SECONDS = 60 * 55


def _cache_key(phone_number, suffix='otp'):
    cleaned = phone_number.replace('+', '').replace(' ', '')
    return f'tenderhelper:{suffix}:{cleaned}'


def generate_otp(phone_number):
    rate_key = _cache_key(phone_number, 'rate')
    otp_key = _cache_key(phone_number, 'otp')
    attempts_key = _cache_key(phone_number, 'attempts')

    if cache.get(rate_key):
        logger.warning("OTP rate limit: %s", phone_number)
        return None

    otp = ''.join(str(secrets.randbelow(10)) for _ in range(OTP_LENGTH))
    expiry_seconds = OTP_EXPIRY_MINUTES * 60
    cache.set(otp_key, otp, timeout=expiry_seconds)
    cache.set(rate_key, True, timeout=60)
    cache.set(attempts_key, 0, timeout=expiry_seconds)
    logger.info("OTP generated for %s", phone_number)
    return otp


def verify_otp(phone_number, submitted_otp):
    otp_key = _cache_key(phone_number, 'otp')
    attempts_key = _cache_key(phone_number, 'attempts')
    stored_otp = cache.get(otp_key)

    if stored_otp is None:
        return False, 'otp_expired'

    attempts = cache.get(attempts_key, 0)
    if attempts >= OTP_MAX_ATTEMPTS:
        cache.delete(otp_key)
        cache.delete(attempts_key)
        return False, 'max_attempts'

    if str(submitted_otp) == str(stored_otp):
        cache.delete(otp_key)
        cache.delete(attempts_key)
        logger.info("OTP verified for %s", phone_number)
        return True, None

    cache.set(attempts_key, attempts + 1, timeout=OTP_EXPIRY_MINUTES * 60)
    remaining = OTP_MAX_ATTEMPTS - attempts - 1
    logger.warning("Invalid OTP for %s. %s attempts left.", phone_number, remaining)
    return False, 'invalid_otp'


def send_otp_sms(phone_number, otp):
    message = (
        f"TenderHelper tasdiqlash kodi: {otp}. "
        f"{OTP_EXPIRY_MINUTES} daqiqa ichida kiriting."
    )
    success, _provider_message_id = send_sms_message(phone_number, message)
    return success


def send_sms_message(phone_number, message, *, sender=None):
    """Send a plain SMS and return (success, provider_message_id)."""
    provider = getattr(settings, 'SMS_PROVIDER', 'console')

    if provider == 'console':
        logger.info("Development SMS for %s: %s", phone_number, message)
        return True, ''

    if provider == 'eskiz':
        return _send_via_eskiz(phone_number, message, sender=sender)

    logger.error("Unknown SMS provider: %s", provider)
    return False, ''


def _send_via_eskiz(phone_number, message, *, sender=None):
    import requests

    if not _eskiz_is_configured():
        logger.error("Eskiz SMS provider is not configured.")
        return False, ''

    try:
        token = _get_eskiz_token(requests)
        if not token:
            return False, ''

        sms_response = requests.post(
            f"{settings.ESKIZ_API_URL}/message/sms/send",
            data={
                'mobile_phone': phone_number.replace('+', ''),
                'message': message,
                'from': sender or getattr(settings, 'ESKIZ_SMS_FROM', 'TenderHelper'),
            },
            headers={
                'Authorization': f'Bearer {token}',
            },
            timeout=10,
        )

        if sms_response.status_code != 200:
            logger.error("Eskiz SMS failed with status %s", sms_response.status_code)
            return False, ''

        payload = sms_response.json()
        provider_message_id = str(
            payload.get('id')
            or payload.get('message_id')
            or payload.get('data', {}).get('id')
            or '',
        )
        logger.info("Eskiz SMS sent to %s", phone_number)
        return True, provider_message_id
    except requests.RequestException as exc:
        logger.error("Eskiz request error: %s", exc)
        return False, ''


def _eskiz_is_configured():
    required = (
        settings.ESKIZ_API_URL,
        settings.ESKIZ_EMAIL,
        settings.ESKIZ_SECRET_KEY,
    )
    return all(value and not str(value).startswith('<') for value in required)


def _get_eskiz_token(requests_module):
    token = cache.get(ESKIZ_TOKEN_CACHE_KEY)
    if token:
        return token

    auth_response = requests_module.post(
        f"{settings.ESKIZ_API_URL}/auth/login",
        data={
            'email': settings.ESKIZ_EMAIL,
            'password': settings.ESKIZ_SECRET_KEY,
        },
        timeout=10,
    )
    if auth_response.status_code != 200:
        logger.error("Eskiz auth failed with status %s", auth_response.status_code)
        return ''

    token = auth_response.json().get('data', {}).get('token')
    if not token:
        logger.error("Eskiz auth response did not include a token.")
        return ''

    cache.set(
        ESKIZ_TOKEN_CACHE_KEY,
        token,
        timeout=getattr(
            settings,
            'ESKIZ_TOKEN_CACHE_SECONDS',
            ESKIZ_TOKEN_TIMEOUT_SECONDS,
        ),
    )
    return token
