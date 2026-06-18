"""
TenderHelper AI — Django Settings
==================================
Professional configuration for MVP development.
Uses python-dotenv for environment variable management.
"""

import os
from pathlib import Path
from datetime import timedelta
from decimal import Decimal

import dj_database_url
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv


class CoreRuntimeConfigurationError(ImproperlyConfigured):
    """Raised when runtime settings would violate production safety guarantees."""


# ──────────────── Base Directory ────────────────
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env from project root (one level above backend/)
load_dotenv(BASE_DIR.parent / '.env')

APP_ENV = os.getenv('APP_ENV', 'local').strip().lower()
if APP_ENV not in {'local', 'test', 'staging', 'production'}:
    raise ImproperlyConfigured(
        'APP_ENV must be local, test, staging, or production.'
    )

# ──────────────── Security ────────────────
def env_bool(name, default=False):
    raw_default = 'True' if default else 'False'
    return os.getenv(name, raw_default).lower() in ('true', '1', 'yes')


def env_int(name, default):
    return int(os.getenv(name, str(default)))


def env_float(name, default):
    return float(os.getenv(name, str(default)))


def env_decimal(name, default):
    return Decimal(os.getenv(name, str(default)))


SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-dev-key-change-in-production')
DEBUG = env_bool('DEBUG', default=APP_ENV == 'local')
ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv(
        'ALLOWED_HOSTS',
        'tenderhelperai.com,api.tenderhelperai.com,127.0.0.1',
    ).split(',')
    if host.strip()
]
DEMO_MODE = env_bool('DEMO_MODE')

IS_DEPLOYED_ENV = APP_ENV in {'staging', 'production'}
if IS_DEPLOYED_ENV and DEBUG:
    raise ImproperlyConfigured(
        'DEBUG must be False in staging and production.'
    )
if IS_DEPLOYED_ENV and (
    len(SECRET_KEY) < 50 or SECRET_KEY.startswith('django-insecure-')
):
    raise ImproperlyConfigured(
        'Staging and production require a strong SECRET_KEY.'
    )

SECURE_SSL_REDIRECT = False if APP_ENV == 'test' else env_bool(
    'SECURE_SSL_REDIRECT',
    default=IS_DEPLOYED_ENV,
)
SESSION_COOKIE_SECURE = False if APP_ENV == 'test' else env_bool(
    'SESSION_COOKIE_SECURE',
    default=IS_DEPLOYED_ENV,
)
CSRF_COOKIE_SECURE = False if APP_ENV == 'test' else env_bool(
    'CSRF_COOKIE_SECURE',
    default=IS_DEPLOYED_ENV,
)
SECURE_HSTS_SECONDS = int(os.getenv(
    'SECURE_HSTS_SECONDS',
    '31536000' if APP_ENV == 'production' else '0',
))
SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool(
    'SECURE_HSTS_INCLUDE_SUBDOMAINS',
)
SECURE_HSTS_PRELOAD = env_bool('SECURE_HSTS_PRELOAD')
if env_bool('TRUST_X_FORWARDED_PROTO', default=IS_DEPLOYED_ENV):
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# ──────────────── Application Definition ────────────────
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',
]

LOCAL_APPS = [
    'users.apps.UsersConfig',
    'companies.apps.CompaniesConfig',
    'tenders.apps.TendersConfig',
    'analysis.apps.AnalysisConfig',
    'subscriptions.apps.SubscriptionsConfig',
    'documents.apps.DocumentsConfig',
    'teams.apps.TeamsConfig',
    'competitors.apps.CompetitorsConfig',
    'controlplane.apps.ControlPlaneConfig',
    'telegram.apps.TelegramConfig',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# ──────────────── Middleware ────────────────
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',          # CORS — must be high
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

if DEMO_MODE:
    MIDDLEWARE.insert(
        MIDDLEWARE.index('django.contrib.messages.middleware.MessageMiddleware'),
        'core.demo_middleware.DemoUserMiddleware',
    )

# ──────────────── URL Configuration ────────────────
ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# ──────────────── Database ────────────────
# DATABASE_URL is the single source of truth for deployed environments.
# When it is absent, use an isolated in-memory SQLite database only for
# local/test execution cycles. Staging and production refuse non-PostgreSQL.
DATABASE_URL = os.getenv('DATABASE_URL', '').strip()
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=int(os.getenv('DATABASE_CONN_MAX_AGE', '60')),
            conn_health_checks=True,
        ),
    }
else:
    if IS_DEPLOYED_ENV:
        raise ImproperlyConfigured(
            'Staging and production require a PostgreSQL DATABASE_URL.'
        )
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'file:tenderhelper_test?mode=memory&cache=shared',
            'OPTIONS': {
                'uri': True,
            },
            'TEST': {
                'NAME': 'file:tenderhelper_test?mode=memory&cache=shared',
            },
        },
    }

if (
    APP_ENV in {'staging', 'production'}
    and DATABASES['default']['ENGINE'] != 'django.db.backends.postgresql'
):
    raise ImproperlyConfigured(
        'Staging and production require a PostgreSQL DATABASE_URL.'
    )

# ──────────────── Custom User Model ────────────────
AUTH_USER_MODEL = 'users.CustomUser'

# ──────────────── Password Validation ────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ──────────────── Internationalization ────────────────
LANGUAGE_CODE = 'uz'
TIME_ZONE = 'Asia/Tashkent'
USE_I18N = True
USE_TZ = True

# ──────────────── Static & Media Files ────────────────
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ──────────────── Default Primary Key ────────────────
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ══════════════════════════════════════════════════════
#  THIRD-PARTY CONFIGURATIONS
# ══════════════════════════════════════════════════════

# ──────────────── Django REST Framework ────────────────
REST_FRAMEWORK = {
    # Authentication
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'users.authentication.VersionedJWTAuthentication',
    ],

    # Permissions — default: authenticated only
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],

    # Throttling (Rate Limiting)
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '15/minute',       # Anonim foydalanuvchilar
        'user': '60/minute',       # Autentifikatsiya qilingan
        'registry_lookup': '10/hour',
    },

    # Pagination
    'DEFAULT_PAGINATION_CLASS': 'core.pagination.StandardPageNumberPagination',
    'PAGE_SIZE': 20,

    # Filtering
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],

    # Date/Time format
    'DATETIME_FORMAT': '%Y-%m-%dT%H:%M:%S%z',
    'DATE_FORMAT': '%Y-%m-%d',

    # Exception handling
    'EXCEPTION_HANDLER': 'core.utils.exceptions.custom_exception_handler',
}

# ──────────────── JWT (SimpleJWT) ────────────────
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(
        minutes=int(os.getenv('JWT_ACCESS_TOKEN_LIFETIME_MINUTES', '60'))
    ),
    'REFRESH_TOKEN_LIFETIME': timedelta(
        days=int(os.getenv('JWT_REFRESH_TOKEN_LIFETIME_DAYS', '7'))
    ),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
}

# ──────────────── CORS (Cross-Origin) ────────────────
CORS_ALLOWED_ORIGINS = os.getenv(
    'CORS_ALLOWED_ORIGINS',
    'https://tenderhelperai.com,https://www.tenderhelperai.com',
)
CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in CORS_ALLOWED_ORIGINS.split(',')
    if origin.strip()
]

CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        'CSRF_TRUSTED_ORIGINS',
        'https://tenderhelperai.com,https://www.tenderhelperai.com,https://api.tenderhelperai.com',
    ).split(',')
    if origin.strip()
]

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

FRONTEND_BASE_URL = os.getenv(
    'FRONTEND_BASE_URL',
    'https://tenderhelperai.com',
).rstrip('/')

EMAIL_BACKEND = os.getenv(
    'EMAIL_BACKEND',
    'django.core.mail.backends.console.EmailBackend',
)
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'TenderHelper <no-reply@tenderhelperai.com>')
EMAIL_HOST = os.getenv('EMAIL_HOST', '')
EMAIL_PORT = env_int('EMAIL_PORT', 465)
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_SSL = env_bool('EMAIL_USE_SSL', default=True)
EMAIL_USE_TLS = env_bool('EMAIL_USE_TLS', default=False)
if EMAIL_USE_SSL and EMAIL_USE_TLS:
    raise ImproperlyConfigured(
        'EMAIL_USE_SSL and EMAIL_USE_TLS cannot both be enabled.',
    )

# ══════════════════════════════════════════════════════
#  TENDERHELPER CUSTOM SETTINGS
# ══════════════════════════════════════════════════════

# ──────────────── AI (Google Gemini) ────────────────
# Company registry
COMPANY_REGISTRY_PROVIDER = os.getenv(
    'COMPANY_REGISTRY_PROVIDER',
    'companies.services.registry.DisabledCompanyRegistryProvider',
)
COMPANY_REGISTRY_API_URL = os.getenv('COMPANY_REGISTRY_API_URL', '')
COMPANY_REGISTRY_API_TOKEN = os.getenv('COMPANY_REGISTRY_API_TOKEN', '')
COMPANY_REGISTRY_SOURCE = os.getenv('COMPANY_REGISTRY_SOURCE', 'tax')
COMPANY_REGISTRY_TIMEOUT_SECONDS = env_float('COMPANY_REGISTRY_TIMEOUT_SECONDS', 5)
COMPANY_REGISTRY_RETRY_COUNT = env_int('COMPANY_REGISTRY_RETRY_COUNT', 1)
COMPANY_REGISTRY_CACHE_SECONDS = env_int('COMPANY_REGISTRY_CACHE_SECONDS', 86400)
COMPANY_REGISTRY_DRAFT_TTL_SECONDS = env_int('COMPANY_REGISTRY_DRAFT_TTL_SECONDS', 1800)

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
GEMINI_MODEL_ANALYSIS = os.getenv(
    'GEMINI_MODEL_ANALYSIS',
    os.getenv('GEMINI_MODEL', 'gemini-2.5-flash'),
)
GEMINI_MODEL_EMBEDDING = os.getenv(
    'GEMINI_MODEL_EMBEDDING',
    'text-embedding-004',
)
# Compatibility alias for legacy code paths; new analysis code uses
# GEMINI_MODEL_ANALYSIS explicitly.
GEMINI_MODEL = GEMINI_MODEL_ANALYSIS
GEMINI_TIMEOUT = env_int('GEMINI_TIMEOUT', 30)
ANALYSIS_PROVIDER = os.getenv(
    'ANALYSIS_PROVIDER',
    'analysis.providers.gemini.GeminiAnalysisProvider',
)

# Document generation and export
DOCUMENT_GENERATION_PROVIDER = os.getenv(
    'DOCUMENT_GENERATION_PROVIDER',
    'documents.services.providers.GeminiDocumentGenerationProvider',
)
DOCUMENT_GENERATION_MODEL = os.getenv(
    'DOCUMENT_GENERATION_MODEL',
    GEMINI_MODEL,
)
DOCUMENT_GENERATION_TIMEOUT_SECONDS = env_int(
    'DOCUMENT_GENERATION_TIMEOUT_SECONDS',
    30,
)
DOCUMENT_EXPORT_URL_TTL_SECONDS = env_int('DOCUMENT_EXPORT_URL_TTL_SECONDS', 300)
DOCUMENT_PDF_FONT_PATH = os.getenv('DOCUMENT_PDF_FONT_PATH', '')

# Celery. Eager mode is for local development/tests only.
REDIS_URL = os.getenv('REDIS_URL', 'redis://redis:6379')
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', f'{REDIS_URL}/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', f'{REDIS_URL}/1')
CELERY_TASK_ALWAYS_EAGER = os.getenv(
    'CELERY_TASK_ALWAYS_EAGER',
    'False',
).lower() in ('true', '1', 'yes')
if IS_DEPLOYED_ENV and CELERY_TASK_ALWAYS_EAGER:
    raise CoreRuntimeConfigurationError(
        'CELERY_TASK_ALWAYS_EAGER cannot be enabled in staging or production.'
    )
CELERY_TASK_EAGER_PROPAGATES = False
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TIMEZONE = TIME_ZONE

COMPETITOR_MIN_SAMPLE_SIZE = env_int('COMPETITOR_MIN_SAMPLE_SIZE', 3)
COMPETITOR_FRESHNESS_SECONDS = env_int('COMPETITOR_FRESHNESS_SECONDS', 86400)
COMPETITOR_PERIOD_DAYS = tuple(sorted({
    int(value.strip())
    for value in os.getenv('COMPETITOR_PERIOD_DAYS', '30,90,365').split(',')
    if value.strip()
}))
if not COMPETITOR_PERIOD_DAYS or any(
    value <= 0 for value in COMPETITOR_PERIOD_DAYS
):
    raise ImproperlyConfigured(
        'COMPETITOR_PERIOD_DAYS must contain positive integers.'
    )
CELERY_BEAT_SCHEDULE = {
    'refresh-competitor-intelligence-daily': {
        'task': 'competitors.tasks.refresh_competitor_analytics_task',
        'schedule': 86400.0,
    },
    'apply-scheduled-subscription-changes': {
        'task': 'subscriptions.tasks.apply_scheduled_subscription_changes_task',
        'schedule': 60.0,
    },
    'reset-monthly-sms-counters': {
        'task': 'subscriptions.tasks.reset_monthly_sms_counters_task',
        'schedule': 86400.0,
    },
}

# Privileged control-plane authentication
ADMIN_MFA_PROVIDER = os.getenv(
    'ADMIN_MFA_PROVIDER',
    'controlplane.services.mfa.DisabledAdminMFAProvider',
)
ADMIN_MFA_SESSION_SECONDS = env_int('ADMIN_MFA_SESSION_SECONDS', 43200)
ADMIN_STEP_UP_SECONDS = env_int('ADMIN_STEP_UP_SECONDS', 600)

# ──────────────── SMS OTP ────────────────
SMS_PROVIDER = os.getenv('SMS_PROVIDER', 'eskiz')  # 'console' | 'eskiz'
OTP_LENGTH = env_int('OTP_LENGTH', 6)
OTP_EXPIRY_MINUTES = env_int('OTP_EXPIRY_MINUTES', 3)

# Eskiz.uz
ESKIZ_API_URL = os.getenv('ESKIZ_API_URL', 'https://notify.eskiz.uz/api')
ESKIZ_EMAIL = os.getenv('ESKIZ_EMAIL', '')
ESKIZ_SECRET_KEY = os.getenv(
    'ESKIZ_SECRET_KEY',
    os.getenv('ESKIZ_PASSWORD', ''),
)
ESKIZ_SMS_FROM = os.getenv('ESKIZ_SMS_FROM', 'TenderHelper')
# Temporary compatibility alias for deployments using the old variable name.
ESKIZ_PASSWORD = ESKIZ_SECRET_KEY

# ──────────────── Google OAuth ────────────────
GOOGLE_OAUTH_CLIENT_ID = os.getenv(
    'GOOGLE_OAUTH_CLIENT_ID',
    os.getenv('GOOGLE_CLIENT_ID', ''),
)
GOOGLE_OAUTH_CLIENT_SECRET = os.getenv(
    'GOOGLE_OAUTH_CLIENT_SECRET',
    os.getenv('GOOGLE_CLIENT_SECRET', ''),
)
# Internal compatibility aliases; new deployments should use GOOGLE_OAUTH_*.
GOOGLE_CLIENT_ID = GOOGLE_OAUTH_CLIENT_ID
GOOGLE_CLIENT_SECRET = GOOGLE_OAUTH_CLIENT_SECRET

# ──────────────── Payment Providers ────────────────
PAYME_MERCHANT_ID = os.getenv('PAYME_MERCHANT_ID', '')
PAYME_SECRET_KEY = os.getenv('PAYME_SECRET_KEY', '')

CLICK_MERCHANT_ID = os.getenv('CLICK_MERCHANT_ID', '')
CLICK_SERVICE_ID = os.getenv('CLICK_SERVICE_ID', '')
CLICK_SECRET_KEY = os.getenv('CLICK_SECRET_KEY', '')
CLICK_ALLOWED_IPS = [
    ip.strip()
    for ip in os.getenv('CLICK_ALLOWED_IPS', '').split(',')
    if ip.strip()
]

UZUM_MERCHANT_ID = os.getenv('UZUM_MERCHANT_ID', '')
UZUM_SECRET_KEY = os.getenv('UZUM_SECRET_KEY', '')

# ──────────────── Subscription Limits ────────────────
# ──────────────── Scraping ────────────────
TENDER_PORTALS = {
    'xarid_uzex': os.getenv('TENDER_PORTAL_XARID_UZEX_URL', 'https://xarid.uzex.uz'),
    'dxarid_uzex': os.getenv('TENDER_PORTAL_DXARID_UZEX_URL', 'https://dxarid.uzex.uz'),
    'exarid_uzex': os.getenv('TENDER_PORTAL_EXARID_UZEX_URL', 'https://exarid.uzex.uz'),
    'e_auksion': os.getenv('TENDER_PORTAL_E_AUKSION_URL', 'https://e-auksion.uz'),
}
SCRAPE_INTERVAL_MINUTES = env_int('SCRAPE_INTERVAL_MINUTES', 30)
SCRAPER_TIMEOUT_SECONDS = env_float('SCRAPER_TIMEOUT_SECONDS', 15)
SCRAPER_RETRY_COUNT = env_int('SCRAPER_RETRY_COUNT', 3)
SCRAPER_RETRY_BASE_SECONDS = env_float('SCRAPER_RETRY_BASE_SECONDS', 0.5)

# ──────────────── Financial Constants (O'zbekiston) ────────────────
VAT_RATE = env_decimal('VAT_RATE', '0.12')          # 12% QQS
OPERATOR_FEE_RATE = env_decimal('OPERATOR_FEE_RATE', '0.0015')
ZAKALAT_RATE = env_decimal('ZAKALAT_RATE', '0.03')
