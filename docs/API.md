# TenderHelper API - Current Implementation Snapshot

**Yangilangan:** 2026-06-18
**Base URL:** `http://localhost:8000/api/v1/`  
**Authentication:** Bearer JWT
**Scope:** hozir kodda mavjud backend endpointlar

## Prefix Migration

Company, subscription va team API uchun `/companies/`, `/subscriptions/`
hamda `/teams/` canonical prefixlari mavjud. Eski `/company/`,
`/subscription/` va `/team/` compatibility alias sifatida ishlaydi.

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
| GET | `/api/v1/auth/session/` | Ha | UI bootstrap: user, company, role, permission, entitlement, usage, navigation |
| POST | `/api/v1/auth/change-password/` | Ha | Force-change checkpoint, auth version rotate va yangi token |

`/auth/session/` frontend uchun canonical bootstrap endpoint hisoblanadi.
Response joriy user, active company, membership role/permissions,
subscription limits, usage remaining, feature entitlements, navigation itemlari
va action capabilitylarini bitta contractda qaytaradi. `company_id` query
parametri berilsa response shu kompaniyaga scoped bo'ladi; userga tegishli
bo'lmagan kompaniya `404 company_not_found` qaytaradi. Telegram menyusi hozir
`planned_later` sabab bilan disabled qaytadi, chunki Mini App alohida keyingi
scope.

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

Tender response `source`, `external_id`, legacy `platform_source` va
`lot_number`ni qaytaradi. Portal lotining canonical identity contracti
`(source, external_id)`; bir xil external ID boshqa portalda mavjud bo'lishi
mumkin. Manual lotlarda `source=manual`, `external_id=""` va generated
`lot_number` ishlatiladi.

Tender qidiruvi `title`, `buyer_name`, `lot_number`, `category` maydonlarida
case-insensitive ishlaydi. Search region/category, platform, narx, deadline va
ordering filtrlari bilan birga qo'llanadi. Whitespace query barcha active
lotlarni qaytaradi; 200 belgidan uzun query `400` bo'ladi.

Pagination default 20, `page_size` orqali maksimal 100. PostgreSQLda Django
`icontains` hosil qiladigan `UPPER(column) LIKE` expressionlari uchun
`pg_trgm` functional GIN indekslari mavjud. SQLite faqat local contract
fallback; 100 ming qator p95 gate PostgreSQL 16 CI jobida bajariladi.

## Analysis

| Method | URL | Auth | Holat |
|---|---|---:|---|
| POST | `/api/v1/analysis/start/` | Ha | `202`; ownership/quota tekshiradi va `AnalysisRun.id` qaytaradi |
| GET | `/api/v1/analysis/history/` | Ha | Mavjud; faqat joriy user ma'lumotlari |
| GET | `/api/v1/analysis/legal-sources/` | Ha | Legal RAG uchun official source policy |
| GET | `/api/v1/analysis/<uuid>/status/` | Ha | `AnalysisRun.id` bo'yicha progress, telemetry va finding snapshot |
| GET | `/api/v1/analysis/<uuid>/result/` | Ha | `AnalysisRun.id` yoki legacy analysis ID bo'yicha result |
| POST | `/api/v1/analysis/<uuid>/calculate/` | Ha | Mavjud; ownership-scoped |

Analysis HTTP threadda provider chaqirmaydi. Start endpoint `AnalysisRun`
yaratadi, Celery task esa Gemini provider chaqiruvi, citation-aware JSON
parsing, `AnalysisFinding` strukturalash va `ModelInvocation` telemetry yozuvini
bajaradi. Provider xatosida analysis `FAILED` holatiga o'tadi; soxta
muvaffaqiyat fallbacki yo'q. Analysis boshlanishidan oldin joriy billing period
uchun `ai_analysis` usage atomik oshiriladi. Free tarifda beshinchi request
`429 usage_limit_exceeded` qaytaradi.

Legal RAG source policy [`RAG_SOURCE_POLICY.md`](RAG_SOURCE_POLICY.md)da
saqlanadi. Binding huquqiy xulosalar primary manba sifatida Lex.uz citationini
talab qiladi; Gov.uz va davlat xaridlari portali official context/fact source
sifatida ishlatiladi. Technical standard source default holatda inactive va
manual-review talab qiladi.

## Subscription

| Method | URL | Auth | Holat |
|---|---|---:|---|
| GET | `/api/v1/subscriptions/plans/` | Ha | DB-backed Free/Pro/Business/Enterprise katalogi |
| GET | `/api/v1/subscriptions/current/` | Ha | Effective active subscription |
| GET | `/api/v1/subscriptions/status/` | Ha | Current contract + legacy tariff maydonlari |
| GET | `/api/v1/subscriptions/usage/` | Ha | Joriy period usage va remaining |
| GET | `/api/v1/subscriptions/entitlements/` | Ha | Barcha WP2 feature gate holatlari |
| POST | `/api/v1/subscriptions/features/<key>/check/` | Ha | Backend authoritative gate |
| POST | `/api/v1/subscriptions/checkout/` | Ha | CLICK sozlangan bo'lsa pending transaction yaratadi; aks holda `501` |

Eski `/api/v1/subscription/*` yo'llari compatibility aliasidir. Seed pricing:
Free `0`, Pro `350000`, Business `950000` UZS/oy. Annual UI contract Pro
`3360000`, Business `9120000` UZS. Checkout hech qachon payment tasdig'isiz
subscription aktivlashtirmaydi.

## Payments

| Method | URL | Auth | Holat |
|---|---|---:|---|
| POST | `/api/v1/payments/click/prepare/` | Yo'q | CLICK `Prepare`, signature, amount va idempotency tekshiradi |
| POST | `/api/v1/payments/click/complete/` | Yo'q | CLICK `Complete`; success bo'lsa subscription payment source bilan aktivlashadi |

CLICK callbacklari `CLICK_ALLOWED_IPS` berilgan production muhitida IP
whitelistdan o'tishi kerak. `click_trans_id + action` takroran kelsa
`WebhookEvent`dagi birinchi response replay qilinadi. Payme va Uzum
credentiallari hozir config placeholder; provider state machine hali
CLICK uchun implement qilingan.

Feature gate auth, company ownership, role, active subscription, feature va
STIR talabini tekshiradi. Enterprise seed konfiguratsiyasida Business
featurelarining barchasi mavjud. Free/Pro/Business/Enterprise analysis
limitlari mos ravishda 4/100/250/500.

## Documents

Document API faqat authenticated foydalanuvchi uchun. Generate, edit,
approve va export amallari backendda Business/Enterprise, STIR va company
membership gate'ini qayta tekshiradi.

| Method | URL | Holat |
|---|---|---|
| GET | `/api/v1/documents/` | Ownership-scoped, paginated list va filterlar |
| GET | `/api/v1/documents/templates/` | Active/published uz/ru template katalogi |
| POST | `/api/v1/documents/generate/` | Celery generation task, `202` |
| GET | `/api/v1/documents/<uuid>/` | Status polling, context va draft |
| PATCH | `/api/v1/documents/<uuid>/` | Canonical JSON autosave, `edit_version` |
| POST | `/api/v1/documents/<uuid>/approve/` | Explicit user approval |
| POST | `/api/v1/documents/<uuid>/archive/` | Delete o'rniga archive |
| GET | `/api/v1/documents/<uuid>/versions/` | Immutable revision history |
| POST | `/api/v1/documents/<uuid>/export/` | Approved revisiondan PDF/DOCX |
| GET | `/api/v1/documents/exports/<uuid>/` | Export status polling |
| GET | `/api/v1/documents/exports/<uuid>/download/` | Auth + short-lived signed token |

AI yoki export xatosi real `failed` statusda saqlanadi. Canonical JSONdan
sanitizatsiyalangan HTML va plain text serverda hosil qilinadi. Eski
`edit_version` bilan PATCH `409 edit_version_conflict` qaytaradi. Export
approvaldan oldin rad etiladi.

## Competitors

Competitor API faqat authenticated Business/Enterprise kompaniya owner,
manager yoki analyst rollari uchun ochiq. Har bir ranking/history request
`competitor_query` usage metrikasiga yoziladi; freshness request usage
sarflamaydi.

| Method | URL | Holat |
|---|---|---|
| GET | `/api/v1/competitors/top/?lot_id=<uuid>&period=365d` | Tanlangan lot kategoriyasidagi TOP ranking |
| GET | `/api/v1/competitors/top/?category=it&period=365d` | Category/period ranking |
| GET | `/api/v1/competitors/<stir>/history/` | STIR bo'yicha category snapshot tarixi |
| GET | `/api/v1/competitors/freshness/` | Calculated time, age va open quality issue soni |

Configured periodlar default `30d`, `90d`, `365d`; custom
`period_start/period_end` ham qo'llanadi. Har bir result `source_count`,
`source_lot_ids` va `calculated_at` qaytaradi. Minimal sample default `3`;
thresholdga yetmagan scope `200` va `status=insufficient_data` qaytaradi.

Faqat completed tenderning verified awardlari agregatsiyaga kiradi. Invalid
start price, missing winning bid, unsupported currency yoki `0..100`dan
tashqari discount analyticsdan chiqarilib, data-quality issue sifatida
saqlanadi. Public manual competitor CRUD mavjud emas. Daily Celery refresh
category snapshotlari va active lot comparison snapshotlarini qayta hisoblaydi.
Qarorlar `docs/adr/0012-competitor-analytics-aggregation.md`da yozilgan.

## Teams

Team API authenticated, company-scoped va Business + STIR bilan gated.
`manage_team` member write actionlari uchun majburiy.

| Method | URL | Vazifa |
|---|---|---|
| GET | `/api/v1/teams/workspace/` | Joriy member, permissions, sidebar va team snapshot |
| GET | `/api/v1/teams/members/` | Company memberlari va session metadata |
| POST | `/api/v1/teams/members/` | Member invite, role, permissions va bir martalik temporary password |
| PATCH | `/api/v1/teams/members/<uuid>/` | Role, explicit permissions va active holatini yangilash |
| POST | `/api/v1/teams/members/<uuid>/revoke-sessions/` | Sessionlarni revoke, membershipni deactivate va auth version rotate |

Rollar: `owner`, `admin`, `manager`, `viewer`. Explicit permission keys:
`view_lots`, `export_lot_data`, `run_ai_analysis`, `use_analysis_quotas`,
`generate_ai_contracts`, `edit_inline_workspace`, `export_pdf_docx`,
`access_competitor_metrics`, `manage_team`.

Invited user birinchi loginidan keyin `/auth/change-password/`dan boshqa
private API'ga kira olmaydi. Temporary password response'da faqat yaratilgan
paytda bir marta ko'rsatiladi.

## Telegram/TMA Target API

Quyidagi endpointlar **rejalashtirilgan, hozir implementatsiya qilinmagan**:

| Method | URL | Vazifa |
|---|---|---|
| POST | `/api/v1/telegram/tma/auth/` | Telegram `initData` verification |
| POST | `/api/v1/telegram/link/challenges/` | Expiring link/re-link challenge |
| POST | `/api/v1/telegram/link/confirm/` | Numeric Telegram ID bilan confirm |
| PATCH/DELETE | `/api/v1/teams/members/<uuid>/telegram/` | Admin relink yoki unlink |
| GET/PATCH | `/api/v1/telegram/notifications/` | Permission-aware preferences |
| POST | `/api/v1/telegram/sessions/revoke/` | TMA sessions revoke |

Contract: [`TELEGRAM_TMA_PLAN.md`](TELEGRAM_TMA_PLAN.md).

## Superadmin Control Plane

Admin API faqat `is_staff`, aktiv `AdminPrincipal`, kerakli capability va
yangi MFA sessiyasi mavjud bo'lganda ochiladi. `is_superuser`ning o'zi yetarli
emas. Kritik write endpointlar fresh step-up, `reason`, `expected_version`,
`idempotency_key` va `confirmed=true` talab qiladi.

| Method | URL | Capability | Vazifa |
|---|---|---|---|
| POST | `/api/v1/admin/auth/step-up/` | Assigned admin | Password + MFA re-auth |
| GET | `/api/v1/admin/overview/` | `admin_overview` | Range/freshness/source status bilan KPI |
| GET | `/api/v1/admin/search/` | `admin_support` | User/company global search |
| GET | `/api/v1/admin/users/` | `admin_support` | Maskalangan user list |
| GET | `/api/v1/admin/users/<uuid>/` | `admin_support` | Auth, company va support timeline |
| POST | `/api/v1/admin/users/<uuid>/action/` | `admin_support` + step-up | Block/unblock/session revoke |
| POST | `/api/v1/admin/users/<uuid>/reveal/` | `admin_support` + step-up | Reason bilan PII reveal |
| POST | `/api/v1/admin/users/<uuid>/export/` | `admin_support` + step-up | Auditlangan CSV PII export |
| GET | `/api/v1/admin/companies/` | `admin_support` | Company, owner, usage va agregatlar |
| GET | `/api/v1/admin/companies/<uuid>/` | `admin_support` | Timeline/history/detail |
| GET | `/api/v1/admin/companies/<uuid>/entitlements/` | `admin_billing` | Effective yoki proposed plan preview |
| GET | `/api/v1/admin/plans/` | `admin_billing` | Plan config va subscriber count |
| POST | `/api/v1/admin/plans/<code>/preview/` | `admin_billing` | Mutatsiyasiz impact preview |
| POST | `/api/v1/admin/plans/<code>/` | `admin_billing` + step-up | Versioned plan publish |
| GET | `/api/v1/admin/subscriptions/` | `admin_billing` | Paginated/filterable lifecycle list |
| POST | `/api/v1/admin/subscriptions/<company>/preview/` | `admin_billing` | Action confirmation summary |
| POST | `/api/v1/admin/subscriptions/<company>/action/` | `admin_billing` + step-up | Activate/upgrade/downgrade/pause/cancel/extend |
| GET | `/api/v1/admin/payments/` | `admin_billing` | Provider yo'qligi sabab `unavailable` |
| GET | `/api/v1/admin/operations/` | `admin_operations` | Feature/template/AI source status |
| POST | `/api/v1/admin/operations/features/<key>/` | `admin_operations` + step-up | Feature kill switch |
| POST | `/api/v1/admin/operations/templates/<uuid>/` | `admin_content` + step-up | Publish/unpublish |
| POST | `/api/v1/admin/operations/maintenance-banner/` | `admin_root` + step-up | Versioned banner setting |
| GET | `/api/v1/admin/audit/` | `admin_audit` | Filterable append-only audit |
| POST | `/api/v1/admin/audit/export/` | `admin_audit` + step-up | Auditlangan CSV export |
| POST | `/api/v1/admin/principals/<user>/` | `admin_root` + step-up | Capability assignment |

Scheduled downgrade joriy billing period oxiriga yoziladi va Celery beat task
uni row lock bilan bir marta qo'llaydi. Payment, scraping, queue va to'liq AI
cost/provider domainlari mavjud bo'lmagani uchun overview/operations ularni
soxta raqam bilan emas, `source_status=unavailable` bilan qaytaradi.

Arxitektura qarori
`docs/adr/0013-superadmin-control-plane.md`da hujjatlashtirilgan.

## Error Contract

DRF exception handler yagona typed envelope qaytaradi. Ba'zi legacy viewlar
hali bevosita `Response({"error": ...})` qaytaradi; ularni keyingi API
cleanup bosqichida shu contractga o'tkazish kerak. Canonical xato formati:

```json
{
  "error_code": "feature_not_available",
  "code": "feature_not_available",
  "message": "Bu funksiya Business tarifida mavjud",
  "details": {
    "feature": "document_generation",
    "requires_stir": true,
    "required_plan": "business"
  }
}
```

Custom exception handler `core.utils.exceptions.custom_exception_handler`
orqali ulangan va DRF exceptionlari uchun ishlaydi.

## Frontend Contract Smoke

Frontend canonical endpoint source-of-truth:

```text
frontend/src/api/endpoints.js
```

Real backendga qarshi smoke:

```powershell
cd frontend
$env:API_CONTRACT_ORIGIN='http://127.0.0.1:8000'

# Staging/VPS uchun:
$env:API_CONTRACT_API_BASE_URL='https://api.tenderhelperai.com/api/v1'

npm run contract:api
```

Credential berilmasa smoke public endpointlar va auth guard xato envelope'ini
tekshiradi. `API_CONTRACT_EMAIL` va `API_CONTRACT_PASSWORD` berilsa login,
session, company profile, entitlements, team workspace va admin overview
contractlari ham tekshiriladi. Yangi frontend yuzasi yangi endpoint ishlatsa,
`endpoints.js` va `scripts/api-contract-smoke.mjs` birga yangilanishi shart.
`VITE_API_BASE_URL` contract smoke target sifatida ishlatilmaydi; u faqat
frontend build uchun qoladi.
