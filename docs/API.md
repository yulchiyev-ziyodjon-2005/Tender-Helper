# TenderHelper AI — API Documentation

**Base URL:** `http://localhost:8000/api/v1/`  
**Authentication:** Bearer JWT Token

---

## Health Check

| Method | URL | Auth | Description |
|--------|-----|------|-------------|
| GET | `/api/health/` | ❌ | API sog'liq tekshiruvi |

**Response:**
```json
{
    "status": "ok",
    "service": "TenderHelper AI",
    "version": "1.0.0-mvp"
}
```

---

## Auth Endpoints

| Method | URL | Auth | Description |
|--------|-----|------|-------------|
| POST | `/api/v1/auth/send-otp/` | ❌ | OTP yuborish |
| POST | `/api/v1/auth/verify-otp/` | ❌ | OTP tasdiqlash → JWT |
| POST | `/api/v1/auth/google/` | ❌ | Google OAuth → JWT |
| POST | `/api/v1/auth/refresh/` | ❌ | JWT refresh |
| GET | `/api/v1/auth/me/` | ✅ | Joriy foydalanuvchi |

## Company Endpoints

| Method | URL | Auth | Description |
|--------|-----|------|-------------|
| POST | `/api/v1/company/onboarding/` | ✅ | Onboarding |
| GET | `/api/v1/company/profile/` | ✅ | Profil olish |
| PATCH | `/api/v1/company/profile/` | ✅ | Profil yangilash |

## Tender Endpoints

| Method | URL | Auth | Description |
|--------|-----|------|-------------|
| GET | `/api/v1/tenders/` | ✅ | Lotlar ro'yxati + qidiruv |
| GET | `/api/v1/tenders/<uuid>/` | ✅ | Lot tafsiloti |
| POST | `/api/v1/tenders/manual/` | ✅ | Qo'lda tender kiritish |

## Analysis Endpoints

| Method | URL | Auth | Description |
|--------|-----|------|-------------|
| POST | `/api/v1/analysis/start/` | ✅ | AI tahlil boshlash |
| GET | `/api/v1/analysis/<uuid>/status/` | ✅ | Tahlil holati |
| GET | `/api/v1/analysis/<uuid>/result/` | ✅ | Tahlil natijasi |
| GET | `/api/v1/analysis/history/` | ✅ | Tahlillar tarixi |
| POST | `/api/v1/analysis/<uuid>/calculate/` | ✅ | Kalkulyator |

## Subscription Endpoints

| Method | URL | Auth | Description |
|--------|-----|------|-------------|
| GET | `/api/v1/subscription/plans/` | ❌ | Tarif rejalari |
| GET | `/api/v1/subscription/status/` | ✅ | Obuna holati |
| POST | `/api/v1/subscription/checkout/` | ✅ | To'lov boshlash |
