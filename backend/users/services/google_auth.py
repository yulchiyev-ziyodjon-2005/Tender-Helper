"""
TenderHelper — Google OAuth Service
======================================
Google ID Token'ni tekshirish va foydalanuvchini
avtomatik ro'yxatdan o'tkazish.
"""

import logging

from django.conf import settings
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

logger = logging.getLogger(__name__)


def verify_google_token(token):
    """
    Google ID Token'ni tekshirish.

    Args:
        token: Frontend'dan kelgan Google ID token

    Returns:
        dict: Foydalanuvchi ma'lumotlari {'email', 'name', 'picture'}
        yoki None agar token noto'g'ri bo'lsa
    """
    if not settings.GOOGLE_CLIENT_ID:
        logger.error("Google OAuth client ID is not configured")
        return None

    try:
        id_info = id_token.verify_oauth2_token(
            token,
            google_requests.Request(),
            settings.GOOGLE_CLIENT_ID,
        )

        # Token issuer tekshiruvi
        if id_info['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            logger.warning("Google token: invalid issuer")
            return None

        # Email tasdiqlanganligini tekshirish
        if not id_info.get('email_verified', False):
            logger.warning("Google token: email not verified")
            return None

        user_info = {
            'email': id_info['email'],
            'name': id_info.get('name', ''),
            'first_name': id_info.get('given_name', ''),
            'last_name': id_info.get('family_name', ''),
            'picture': id_info.get('picture', ''),
            'google_id': id_info['sub'],
        }

        logger.info(f"Google token verified for {user_info['email']}")
        return user_info

    except ValueError as e:
        logger.warning(f"Google token verification failed: {e}")
        return None
    except Exception as e:
        logger.error(f"Google OAuth error: {e}")
        return None
