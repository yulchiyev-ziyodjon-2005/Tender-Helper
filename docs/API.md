# TenderHelper API - Current Implementation Snapshot

**Yangilangan:** 2026-06-14
**Base URL:** `http://localhost:8000/api/v1/`  
**Authentication:** Bearer JWT
**Scope:** faqat hozir kodda mavjud demo/MVP endpointlar

> Bu target API contract emas. Rejalashtirilgan plural endpointlar,
> Business funksiyalari va Superadmin API'lari `Plan.md` hamda
> `IMPLEMENTATION_PLAN.md`da yuritiladi. Implementatsiya qilingach ushbu
> snapshot OpenAPI schema asosida yangilanadi.

## Prefix Migration

Company API uchun `/companies/` canonical prefix qo'shilgan. Eski
`/company/` prefix compatibility alias sifatida ishlashda davom etadi.
Qolgan demo applar hozircha singular `/analysis/`, `/subscription/` va
`/team/` prefixlaridan foydalanadi.

Target v1 contract plural prefixlarga o'tadi: `/companies/`, `/analyses/`,
`/subscriptions/`, `/teams/`.

Migration compatibility va deprecation muddati implementation oldidan
OpenAPI/ADR bilan belgilanadi.

## Health

| Method | URL | Auth | Holat |
|---|---|---:|---|
| GET | `/api/health/` | Yo'q | Mavjud |

## Auth

| Method | URL | Auth | Holat |
|---|---|---:|---|
| POST | `/api/v1/auth/register/` | Yo'q | Mavjud |
| POST | `/api/v1/auth/login/` | Yo'q | Mavjud |
| POST | `/api/v1/auth/send-otp/` | Yo'q | Mavjud |
| POST | `/api/v1/auth/verify-otp/` | Yo'q | Mavjud |
| POST | `/api/v1/auth/google/` | Yo'q | Mavjud |
| GET | `/api/v1/auth/google/config/` | Yo'q | Mavjud |
| GET | `/api/v1/auth/google/start/` | Yo'q | Mavjud |
| GET | `/api/v1/auth/google/callback/` | Yo'q | Bir martalik exchange code bilan frontendga qaytaradi |
| POST | `/api/v1/auth/google/exchange/` | Yo'q | Bir martalik code'ni JWT payloadga almashtiradi |
| POST | `/api/v1/auth/refresh/` | Yo'q | Mavjud |
| GET/PATCH | `/api/v1/auth/me/` | Ha | Mavjud |

## Company

| Method | URL | Auth | Holat |
|---|---|---:|---|
| POST | `/api/v1/companies/onboarding/` | Ha | Manual profile create/update |
| GET/PATCH | `/api/v1/companies/profile/` | Ha | Profil va feature access |
| POST | `/api/v1/companies/registry/lookup/` | Ha | Persistent editable draft yaratadi |
| GET | `/api/v1/companies/registry/drafts/<uuid>/` | Ha | Ownership-scoped draft holati |
| POST | `/api/v1/companies/registry/drafts/<uuid>/confirm/` | Ha | Edited draftni atomik tasdiqlaydi |
| POST | `/api/v1/companies/onboarding/skip-stir/` | Ha | STIRsiz profil yaratadi/yangilaydi |
| POST | `/api/v1/companies/profile/registry-refresh/` | Ha | Cache bypass bilan yangi draft |

Registry lookup 5 soniya timeout, 1 retry va 24 soat cache contractiga ega.
Provider ishlamasa endpoint `201` bilan `failed` draft qaytaradi va
`manual_entry_allowed=true` bo'ladi. Provider raw payloadi API response'ga
chiqmaydi; u faqat confirm qilingandan keyin audit uchun profilda saqlanadi.

Default provider o'chirilgan:

```text
COMPANY_REGISTRY_PROVIDER=companies.services.registry.DisabledCompanyRegistryProvider
```

Configurable HTTP adapterni productionda yoqishdan oldin provider va huquqiy
foydalanish tasdiqlanishi shart. Contract `docs/adr/0010-stir-registry-provider.md`
da yozilgan.

## Tenders

| Method | URL | Auth | Holat |
|---|---|---:|---|
| GET | `/api/v1/tenders/` | Yo'q | Mavjud, search/filter/order |
| GET | `/api/v1/tenders/<uuid>/` | Yo'q | Mavjud |
| POST | `/api/v1/tenders/manual/` | Ha | Mavjud; yaratuvchi `created_by` orqali saqlanadi |

Tender qidiruvi DRF `SearchFilter` orqali `title`, `buyer_name` va
`lot_number` maydonlarida ishlaydi. PostgreSQL `ILIKE` va `pg_trgm` target
optimallashtirish bo'lib, SQLite demo muhitida mavjud emas.

## Analysis

| Method | URL | Auth | Holat |
|---|---|---:|---|
| POST | `/api/v1/analysis/start/` | Ha | Mavjud; company ownership tekshiriladi |
| GET | `/api/v1/analysis/history/` | Ha | Mavjud; faqat joriy user ma'lumotlari |
| GET | `/api/v1/analysis/<uuid>/status/` | Ha | Mavjud; ownership-scoped |
| GET | `/api/v1/analysis/<uuid>/result/` | Ha | Mavjud; ownership-scoped |
| POST | `/api/v1/analysis/<uuid>/calculate/` | Ha | Mavjud; ownership-scoped |

Demo analysis sinxron ishlaydi. Provider xatosida analysis `FAILED` holatiga
o'tadi; soxta muvaffaqiyat fallbacki olib tashlangan.

## Subscription

| Method | URL | Auth | Holat |
|---|---|---:|---|
| GET | `/api/v1/subscription/plans/` | Yo'q | Mavjud, hardcoded Free/Pro/Enterprise |
| GET | `/api/v1/subscription/status/` | Ha | Mavjud |
| POST | `/api/v1/subscription/checkout/` | Ha | Test-mode placeholder |

Business plan, usage accounting, CLICK lifecycle va Superadmin overrides
target scope bo'lib, hali implementatsiya qilinmagan.

## Empty Prefixes

Quyidagi prefixlar URL konfiguratsiyasida bor, lekin endpointlari yo'q:

- `/api/v1/team/`
- `/api/v1/competitors/`

`documents`, `payments` va `/api/v1/admin/*` target endpointlari hali URL
konfiguratsiyasiga qo'shilmagan.

## Error Contract

Amaldagi endpointlarda error format bir xil emas (`error` yoki DRF default).
Target format:

```json
{
  "code": "profile_required",
  "message": "Kompaniya profilini yarating",
  "details": {}
}
```

Unified exception handler target implementatsiyaning majburiy qismidir.
