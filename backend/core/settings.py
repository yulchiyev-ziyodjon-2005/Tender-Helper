"""
TenderHelper AI — Django Settings
==================================
Professional configuration for MVP development.
Uses python-dotenv for environment variable management.
"""

import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv

# ──────────────── Base Directory ────────────────
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env from project root (one level above backend/)
load_dotenv(BASE_DIR.parent / '.env')

# ──────────────── Security ────────────────
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-dev-key-change-in-production')
DEBUG = os.getenv('DEBUG', 'True').lower() in ('true', '1', 'yes')
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1,testserver').split(',')
DEMO_MODE = os.getenv('DEMO_MODE', 'False').lower() in ('true', '1', 'yes')

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
    'teams.apps.TeamsConfig',
    'competitors.apps.CompetitorsConfig',
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
# MVP: SQLite (default). Production: PostgreSQL.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Production PostgreSQL (uncomment and set DATABASE_URL in .env):
# import dj_database_url
# DATABASES = {
#     'default': dj_database_url.config(default=os.getenv('DATABASE_URL'))
# }

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
        'rest_framework_simplejwt.authentication.JWTAuthentication',
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
    },

    # Pagination
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
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
    'EXCEPTION_HANDLER': 'rest_framework.views.exception_handler',
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
    'http://localhost:5173,http://127.0.0.1:5173'
).split(',')

CORS_ALLOW_CREDENTIALS = True

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

FRONTEND_BASE_URL = os.getenv('FRONTEND_BASE_URL', 'http://localhost:5173').rstrip('/')

# ══════════════════════════════════════════════════════
#  TENDERHELPER CUSTOM SETTINGS
# ══════════════════════════════════════════════════════

# ──────────────── AI (Google Gemini) ────────────────
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
GEMINI_MODEL = 'gemini-2.0-flash'
GEMINI_TIMEOUT = 30  # seconds

# ──────────────── SMS OTP ────────────────
SMS_PROVIDER = os.getenv('SMS_PROVIDER', 'console')  # 'console' | 'eskiz'
OTP_LENGTH = 6
OTP_EXPIRY_MINUTES = 3

# Eskiz.uz
ESKIZ_API_URL = os.getenv('ESKIZ_API_URL', 'https://notify.eskiz.uz/api')
ESKIZ_EMAIL = os.getenv('ESKIZ_EMAIL', '')
ESKIZ_PASSWORD = os.getenv('ESKIZ_PASSWORD', '')

# ──────────────── Google OAuth ────────────────
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', '')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET', '')

# ──────────────── Payment Providers ────────────────
PAYME_MERCHANT_ID = os.getenv('PAYME_MERCHANT_ID', '')
PAYME_SECRET_KEY = os.getenv('PAYME_SECRET_KEY', '')

CLICK_MERCHANT_ID = os.getenv('CLICK_MERCHANT_ID', '')
CLICK_SERVICE_ID = os.getenv('CLICK_SERVICE_ID', '')
CLICK_SECRET_KEY = os.getenv('CLICK_SECRET_KEY', '')

UZUM_MERCHANT_ID = os.getenv('UZUM_MERCHANT_ID', '')
UZUM_SECRET_KEY = os.getenv('UZUM_SECRET_KEY', '')

# ──────────────── Subscription Limits ────────────────
SUBSCRIPTION_LIMITS = {
    'free': {
        'analysis_per_month': 4,
        'search_per_minute': 15,
    },
    'pro': {
        'analysis_per_month': None,  # Cheksiz
        'search_per_minute': 60,
    },
    'enterprise': {
        'analysis_per_month': None,  # Cheksiz
        'search_per_minute': 100,
    },
}

# ──────────────── Scraping ────────────────
TENDER_PORTALS = {
    'xarid_uzex': 'https://xarid.uzex.uz',
    'dxarid_uzex': 'https://dxarid.uzex.uz',
    'exarid_uzex': 'https://exarid.uzex.uz',
    'e_auksion': 'https://e-auksion.uz',
}
SCRAPE_INTERVAL_MINUTES = 30

# ──────────────── Financial Constants (O'zbekiston) ────────────────
VAT_RATE = 0.12          # 12% QQS (Qo'shilgan Qiymat Solig'i)
OPERATOR_FEE_RATE = 0.0015  # 0.15% UzEx operatorlik komissiya
ZAKALAT_RATE = 0.03      # 3% zakalat (kafolat puli)
