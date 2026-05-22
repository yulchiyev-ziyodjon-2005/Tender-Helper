"""
Traditional Google OAuth 2.0 authorization-code flow helpers.
"""

import logging
from urllib.parse import urlencode

import requests
from django.conf import settings
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

logger = logging.getLogger(__name__)

GOOGLE_AUTH_URL = 'https://accounts.google.com/o/oauth2/v2/auth'
GOOGLE_TOKEN_URL = 'https://oauth2.googleapis.com/token'
GOOGLE_SCOPES = 'openid email profile'


def _is_placeholder(value):
    return not value or value.startswith('your-')


def is_google_oauth_configured():
    return (
        not _is_placeholder(settings.GOOGLE_CLIENT_ID)
        and not _is_placeholder(settings.GOOGLE_CLIENT_SECRET)
    )


def build_google_authorization_url(redirect_uri, state):
    params = {
        'client_id': settings.GOOGLE_CLIENT_ID,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': GOOGLE_SCOPES,
        'state': state,
        'access_type': 'offline',
        'prompt': 'select_account',
        'include_granted_scopes': 'true',
    }
    return f'{GOOGLE_AUTH_URL}?{urlencode(params)}'


def exchange_code_for_user_info(code, redirect_uri):
    token_response = requests.post(
        GOOGLE_TOKEN_URL,
        data={
            'code': code,
            'client_id': settings.GOOGLE_CLIENT_ID,
            'client_secret': settings.GOOGLE_CLIENT_SECRET,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code',
        },
        timeout=15,
    )
    token_response.raise_for_status()
    token_data = token_response.json()
    id_token_value = token_data.get('id_token')

    if not id_token_value:
        logger.warning('Google OAuth token response did not include id_token')
        return None

    id_info = id_token.verify_oauth2_token(
        id_token_value,
        google_requests.Request(),
        settings.GOOGLE_CLIENT_ID,
    )

    if id_info['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
        logger.warning('Google OAuth callback: invalid issuer')
        return None

    if not id_info.get('email_verified', False):
        logger.warning('Google OAuth callback: email not verified')
        return None

    return {
        'email': id_info['email'],
        'name': id_info.get('name', ''),
        'first_name': id_info.get('given_name', ''),
        'last_name': id_info.get('family_name', ''),
        'picture': id_info.get('picture', ''),
        'google_id': id_info['sub'],
    }
