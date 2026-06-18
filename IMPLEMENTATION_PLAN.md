# TenderHelper - Canonical Implementation Plan

**Versiya:** 1.3
**Yangilangan:** 2026-06-18
**Status:** Implementation active. WP0-WP7 backend foundation, production
landing/auth/STIR onboarding, Business Team Hub va Superadmin preview
implementatsiya qilingan. Telegram/TMA uchun backend data-contract modellari
mavjud; bot runtime, linking endpointlari va Mini App auth oqimi Phase D
scope'ida qoladi.
**Strategik manba:** `Plan.md` v4.3

---

## 1. Hujjat Maqsadi

Ushbu hujjat `Plan.md`dagi strategik talablarni bajariladigan work
package'larga ajratadi. U kod emas va implementatsiyani boshlashga ruxsat
bermaydi. Kodlash faqat quyidagi shartlardan keyin boshlanadi:

1. `Plan.md` va ushbu hujjat tasdiqlangan.
2. Ochiq savollar bo'yicha qarorlar ADR yoki decision logda yozilgan.
3. Tegishli bosqichning acceptance criteria va dependency'lari tayyor.
4. Foydalanuvchi implementatsiyani boshlashni alohida tasdiqlagan.

Ustuvorlik:

1. Xavfsizlik va mavjud kritik xatolar.
2. STIR onboarding va feature gating.
3. AI Document Generator va Inline Editor.
4. Competitor Intelligence.
5. Superadmin Console va operatsion boshqaruv.
6. PostgreSQL/Celery/RAG va qolgan platforma imkoniyatlari.

---

## 2. Scope va Chegaralar

### Ushbu reja ichida

- canonical architecture va domain boundaries;
- database model spetsifikatsiyasi;
- API contract rejalari;
- service va async task chegaralari;
- permission va feature gating;
- migration strategiyasi;
- test va quality gate;
- 4 haftalik kritik delivery rejasi;
- keyingi platforma bosqichlari.

### Joriy bosqich chegarasi

- landing, auth, onboarding, team va Superadmin frontend yuzalari mavjud;
- document inline editorning to'liq production UX'i keyingi bosqichda;
- tasdiqlanmagan registry/payment providerga real ulanish qilinmaydi;
- work package'lar dependency tartibida backend va frontend bo'yicha bajariladi;
- provider credentiallari tasdiqsiz kodga kiritilmaydi;
- Telegram data-contract modellari mavjud; bot runtime, linking endpointlari
  va Mini App auth/UI hali implementatsiya qilinmagan.

---

## 3. Arxitektura Qarorlari

| ID | Qaror | Holat |
|---|---|---|
| D-01 | `Plan.md` strategik, `IMPLEMENTATION_PLAN.md` bajarilish hujjati | Qabul qilingan |
| D-02 | STIR optional, lekin rasmiy hujjat funksiyalari uchun majburiy | Qabul qilingan |
| D-03 | Registry javobi editable draft, avtomatik yakuniy profil emas | Qabul qilingan |
| D-04 | Document Generator Business/Enterprise + STIR bilan gated | Qabul qilingan |
| D-05 | Generated document avval draft, foydalanuvchi tasdig'isiz final emas | Qabul qilingan |
| D-06 | Competitor analytics faqat ochiq yakunlangan tenderlardan | Qabul qilingan |
| D-07 | Lot qidiruvi `ILIKE` + `pg_trgm`, RAG qidiruvi alohida | Qabul qilingan |
| D-08 | Backend feature gate yakuniy authority hisoblanadi | Qabul qilingan |
| D-09 | Document lifecycle alohida `documents` Django app'ida bo'ladi | Qabul qilingan |
| D-10 | Editor JSON'i canonical, sanitized HTML va plain text projection | Qabul qilingan |
| D-11 | Pro va Business alohida tarif; Enterprise Business'ni meros oladi | Qabul qilingan |
| D-12 | Competitor baseline Business beta sifatida MVP tarkibiga kiradi | Qabul qilingan |
| D-13 | Superadmin tarif emas, platforma capability roli | Qabul qilingan |
| D-14 | Superadmin mavjud domain servislarini boshqaradi; parallel backend yaratmaydi | Qabul qilingan |
| D-15 | Real-time dashboard MVP'da polling/cache, event alertlar alohida | Qabul qilingan |
| D-16 | Kritik admin action step-up auth va immutable audit talab qiladi | Qabul qilingan |
| D-17 | Target API resource prefixlari plural; singular demo prefixlar vaqtincha compatibility alias | Qabul qilingan |
| D-18 | Browser access tokeni default `sessionStorage`, faqat explicit Remember me bilan `localStorage`; refresh cookie keyingi security phase | Qabul qilingan interim |
| D-19 | Telegram username identity authority emas; verifikatsiyadan keyin immutable Telegram numeric user ID canonical bo'ladi | Phase D qarori |
| D-20 | TMA `initData` faqat serverda HMAC, `auth_date` freshness va replay tekshiruvidan keyin qabul qilinadi | Phase D qarori |

Quyidagilar ADR talab qiladi:

- registry provider va huquqiy foydalanish;
- browser token storage;
- document editor HTML storage/sanitization;
- document export engine;
- competitor source va data-quality siyosati;
- calculator formulasi;
- CLICK integratsiyasi.

### API prefix migratsiyasi

Amaldagi demo URL'lar `/company/`, `/analysis/`, `/subscription/` va
`/team/` singular prefixlardan foydalanadi. Target contract
`/companies/`, `/analyses/`, `/subscriptions/` va `/teams/` bo'ladi.

Migratsiya qoidasi:

1. Plural endpointlar canonical OpenAPI contract sifatida qo'shiladi.
2. Singular endpointlar vaqtincha compatibility alias bo'lib qoladi.
3. Alias response header yoki documentation orqali deprecated belgilanadi.
4. Frontend plural contractga o'tgach, kuzatuv davridan keyin alias olib
   tashlanadi.

---

## 4. Domain va App Chegaralari

| Domain | Django app | Mas'uliyat |
|---|---|---|
| Identity | `users` | Login, OTP, OAuth, user session |
| Company | `companies` | Company profile, STIR, registry lookup, members |
| Tender | `tenders` | Lotlar, qidiruv, source, hujjat metadata |
| Analysis | `analysis` | AI tahlil, citation, calculator |
| Documents | Alohida `documents` app | Template, generation, editor, version, export |
| Competitors | `competitors` | Completed results va analytics |
| Subscription | `subscriptions` | Tarif, usage, feature gate, payment |
| Team | `teams` | Company membership, roles, explicit permissions va session lifecycle |
| Telegram | rejalashtirilgan `telegram` app | Bot identity link, TMA auth/session va notification preferences |
| Admin control plane | Mavjud applar ustidagi admin API/UI | User, billing, operations, audit orchestration |

### Documents app qarori

`TenderDocumentTemplate` va `GeneratedDocument`ni `analysis` app ichiga
joylashtirish texnik jihatdan mumkin, lekin uzoq muddatli ownership uchun
alohida `documents` app tanlanadi:

- AI generation faqat hujjat lifecycle'ning bir qismi;
- editor, versions, approval va export analysis'dan mustaqil;
- permission va audit chegarasi aniq bo'ladi;
- keyinchalik non-AI template-based generation qo'shilishi mumkin.

Qarorning model, version va editor format tafsilotlari ADR-011 da
hujjatlanadi; app chegarasi qayta ochilmaydi.

---

## 5. Work Package 0 - Xavfsizlik Stabilizatsiyasi

**Maqsad:** yangi funksiyalarni xavfli mavjud poydevor ustiga qurmaslik.

**Status:** 2026-06-14 kuni implementatsiya va quality gate yakunlandi.

### Vazifalar

- Analysis endpointlarini `IsAuthenticated` qilish.
- Company ownership tekshiruvini tiklash.
- Demo company bypassni faqat `DEMO_MODE=True`ga bog'lash.
- AI xatosidagi soxta `COMPLETED`/92% fallbackni olib tashlash.
- Model nomlarini environment settings orqali boshqarish.
- `print()` debuglarni structured loggingga o'tkazish.
- OTP uchun cryptographic secure generator ishlatish va kodni loglamaslik.
- OAuth tokenini URL query'dan chiqarish.
- Frontend private route guardlarini yoqish.
- Manual tender yaratishni authenticated qilish va ownership belgilash.
- `AllowAny` audit testini CI'ga qo'shish.
- Mavjud analysis testidagi fake-success expectationni provider failure
  contractiga almashtirish.
- Company ownership va tender identity migration ADRlarini tayyorlash.

### Acceptance criteria

- Token yo'q analysis request `401`.
- Boshqa company obyektiga request `404` yoki `403`.
- Provider xatosida analysis `FAILED`.
- Productionda demo user/company avtomatik yaratilmaydi.
- URL va loglarda access/refresh token yo'q.
- CI kutilmagan `AllowAny`ni bloklaydi.

### Dependency

Yo'q. Barcha boshqa work package'lardan oldin tugashi kerak.

---

## 6. Work Package 1 - STIR Onboarding

**Status:** 2026-06-15 holatiga backend model/provider/cache/retry, editable
draft, confirm, skip, refresh va feature gate yakunlangan. Frontend signup,
STIR lookup, registry draft confirmation va skip/gated UX bilan ulangan.

### 6.1. User journey

1. Account yaratiladi.
2. Foydalanuvchi STIR kiritadi yoki `STIRsiz davom etish`ni tanlaydi.
3. STIR kiritilsa registry lookup bajariladi.
4. Normalizatsiya qilingan rekvizitlar editable draftda ko'rsatiladi.
5. Foydalanuvchi qiymatlarni tahrirlaydi va tasdiqlaydi.
6. Tasdiqlangan profil saqlanadi.
7. STIRsiz profilga feature gate holati ko'rsatiladi.

### 6.2. Registry service

Tavsiya etilgan interfeys:

```text
CompanyRegistryProvider.lookup(stir) -> RegistryCompanyDraft
```

Provider service quyidagilar uchun javobgar:

- STIR validatsiyasi;
- tashqi API authentication;
- timeout va retry;
- provider payload normalization;
- cache;
- audit metadata;
- xatoni domain errorga aylantirish.

View yoki serializer tashqi API'ga bevosita murojaat qilmaydi.

### 6.3. CompanyProfile kengaytmasi

Rejalashtirilgan maydonlar:

| Maydon | Tur | Izoh |
|---|---|---|
| `director_name` | CharField(255) | Rahbar F.I.Sh. |
| `legal_address` | TextField | Yuridik manzil |
| `stir_skipped` | BooleanField | Skip tanlangan |
| `registry_source` | CharField choices | manual/tax/statistics |
| `registry_status` | CharField choices | not_checked/pending/verified/not_found/failed/manual |
| `registry_fetched_at` | DateTime nullable | Oxirgi lookup |
| `raw_tax_data` | JSONField | Asl provider payload |

`stir` optional qoladi. `stir` va `stir_skipped=True` bir vaqtda saqlanmasligi
service/serializer validation orqali taqiqlanadi.

### 6.4. Draft strategiyasi

Registry lookup natijasi darhol `CompanyProfile`ga yozilmaydi.

Variantlar:

1. Signed short-lived draft payload.
2. Alohida `CompanyRegistryDraft` modeli.

Tavsiya: audit va retry uchun alohida draft modeli:

| Maydon | Izoh |
|---|---|
| `user` | Draft egasi |
| `stir` | Lookup STIR |
| `normalized_data` | UI uchun draft |
| `raw_payload` | Provider javobi |
| `provider` | Manba |
| `status` | pending/ready/confirmed/expired/failed |
| `expires_at` | Draft amal muddati |
| `confirmed_at` | Tasdiq vaqti |

### 6.5. API contract

| Method | Endpoint | Natija |
|---|---|---|
| POST | `/api/v1/companies/registry/lookup/` | Draft yaratadi |
| GET | `/api/v1/companies/registry/drafts/<id>/` | Draft holati |
| POST | `/api/v1/companies/registry/drafts/<id>/confirm/` | Edited draftni profilga yozadi |
| POST | `/api/v1/companies/onboarding/skip-stir/` | STIR skip holati |
| POST | `/api/v1/companies/profile/registry-refresh/` | Keyingi refresh |

### 6.6. Feature matrix

| Funksiya | STIR yo'q | STIR bor |
|---|---:|---:|
| Tender qidiruvi | Ha | Ha |
| AI tender tahlili | Ha | Ha |
| Calculator | Ha | Ha |
| Watchlist/notification | Ha | Ha |
| Rasmiy document generation | Yo'q | Tarifga qarab |
| Rasmiy paket export | Yo'q | Tarifga qarab |
| Verified company badge | Yo'q | Registry statusga qarab |
| STIR-based competitor match | Yo'q | Ha |

### 6.7. Testlar

- valid/invalid STIR;
- provider success/not-found/timeout;
- cache hit;
- draft edit va confirm;
- boshqa user draftiga access;
- skip flow;
- STIR qo'shganda gate ochilishi;
- registry unavailable bo'lsa manual onboarding.

### Acceptance criteria

- Provider ishlamasa onboarding davom etadi.
- Provider qiymatlari user tasdig'isiz profilga yozilmaydi.
- STIR skip qilgan user tizimga kira oladi.
- Backend gated funksiyani STIRsiz user uchun rad etadi.

---

## 7. Work Package 2 - Subscription va Feature Gating

**Backend status:** 2026-06-14 kuni DB-backed plan catalogi, subscription
lifecycle, membership boundary, role/STIR/feature gate, atomik usage
hisobi, canonical API, legacy alias va analysis quota integratsiyasi
yakunlandi. Payment provider va frontend bu work package tarkibida
aktivlashtirilmadi.

### Tariflar

| Tarif | Asosiy imkoniyat |
|---|---|
| Free | Qidiruv, 4 analysis, calculator |
| Pro | Kengaytirilgan analysis va notification |
| Business | Document Generator, editor, competitor intelligence, team |
| Enterprise | Business + yuqori limit, audit, priority |

### Feature keys

- `document_generation`
- `document_export`
- `competitor_intelligence`
- `team_collaboration`
- `advanced_audit`

### Gate tekshiruvlari

Gate service quyidagilarni tekshiradi:

1. Authenticated user.
2. Company membership.
3. Role.
4. Active subscription.
5. Feature availability.
6. Usage/fair-use limit.
7. STIR requirement.

Frontend gate faqat UX uchun; backend har requestda qayta tekshiradi.

### Error contract

```json
{
  "code": "feature_not_available",
  "message": "Bu funksiya Business tarifida mavjud",
  "details": {
    "feature": "document_generation",
    "requires_stir": true,
    "required_plan": "business"
  }
}
```

### Acceptance criteria

- URL'ni bevosita chaqirish gate'ni chetlab o'tmaydi.
- Expired subscription funksiyani yopadi.
- Enterprise Business funksiyalarini meros oladi.
- Usage atomik hisoblanadi.

---

## 8. Work Package 3 - AI Document Generator

**Backend status:** 2026-06-14 kuni standalone `documents` app, immutable
template versionlari, uz/ru seed template katalogi, allowlist context,
provider gateway, Celery task boundary, typed canonical output, ownership va
Business/STIR gate, generation status polling hamda revision API yakunlandi.
Frontendda feature surface mavjud; yakuniy rich-text inline editor va
production object storage keyingi bosqichda.

### 8.1. Model spetsifikatsiyasi

#### TenderDocumentTemplate

| Maydon | Tur | Talab |
|---|---|---|
| `id` | UUID PK | |
| `code` | SlugField(100) | Logical template ID |
| `name` | CharField(255) | |
| `document_type` | choices | application/guarantee/commercial/compliance/other |
| `language` | choices | uz/ru, keyin boshqa tillar |
| `version` | PositiveInteger | Immutable version |
| `prompt_template` | TextField | Internal prompt |
| `content_schema` | JSONField | Typed output schema |
| `required_company_fields` | JSONField list | STIR, director, address va boshqalar |
| `is_active` | Boolean | |
| `created_by` | User nullable | Admin author |
| timestamps | DateTime | |

Constraint:

- unique `(code, language, version)`.

Indekslar:

- `(document_type, language, is_active)`;
- `(code, is_active)`.

#### GeneratedDocument

| Maydon | Tur | Talab |
|---|---|---|
| `id` | UUID PK | |
| `company` | FK CompanyProfile | Ownership |
| `tender_lot` | FK TenderLot | Context |
| `template` | FK PROTECT | Used version |
| `analysis` | FK nullable SET_NULL | Optional source analysis |
| `created_by` | FK User PROTECT | |
| `title` | CharField(500) | |
| `document_type` | choices | Snapshot |
| `language` | choices | |
| `status` | choices | generating/draft/approved/exported/failed/archived |
| `content_json` | JSONField | Canonical rich-text document |
| `content_html` | TextField | Sanitized render/export projection |
| `content_text` | TextField | Search/export fallback |
| `context_snapshot` | JSONField | Company/tender facts at generation time |
| `generation_metadata` | JSONField | Model, prompt version, tokens |
| `template_version` | PositiveInteger | Snapshot |
| `edit_version` | PositiveInteger | Optimistic locking |
| `error_message` | TextField | |
| lifecycle timestamps | DateTime | |

Indekslar:

- `(company, status, -updated_at)`;
- `(tender_lot, document_type)`;
- `(created_by, -created_at)`.

### 8.2. Context builder

Allowlist context:

- company name;
- STIR;
- director name;
- legal address;
- legal form;
- tender lot number/title/buyer/deadline;
- verified analysis findings selected for the document.

`raw_tax_data` to'liq promptga yuborilmaydi.

### 8.3. Generation service

```text
authorize
-> validate template required fields
-> build context snapshot
-> create GENERATING row
-> enqueue task
-> provider structured generation
-> validate schema
-> sanitize HTML
-> save DRAFT or FAILED
```

### 8.4. API contract

| Method | Endpoint | Izoh |
|---|---|---|
| GET | `/api/v1/documents/templates/` | Available templates |
| POST | `/api/v1/documents/generate/` | Async generation |
| GET | `/api/v1/documents/<id>/` | Draft/result |
| PATCH | `/api/v1/documents/<id>/` | Inline edit, edit_version required |
| POST | `/api/v1/documents/<id>/approve/` | User approval |
| POST | `/api/v1/documents/<id>/export/` | PDF/DOCX |
| GET | `/api/v1/documents/<id>/versions/` | Revision history |

### Acceptance criteria

- Business + STIR bo'lmagan request rad etiladi.
- Template required field yo'q bo'lsa aniq validation error.
- AI xatosi `FAILED`, fake draft yo'q.
- HTML xavfli tag/attribute'lardan tozalanadi.
- Bir vaqtning o'zida eski `edit_version` bilan save `409 Conflict`.
- Foydalanuvchi tasdig'isiz export final deb belgilanmaydi.

---

## 9. Work Package 4 - Inline Editor va Export

**Backend status:** 2026-06-14 kuni canonical JSON adapteri, server-side HTML
sanitizatsiya, plain-text projection, autosave PATCH contracti, optimistic
locking, revision history, explicit approval, PDF/DOCX export, storage
metadata, checksum, signed download va append-only document audit yakunlandi.
Rich Text Editor UI va E2E frontend bosqichida bajariladi.

### Editor

Tanlov mezonlari:

- React 19 compatibility;
- extensible schema;
- paste sanitization;
- table va list;
- accessible keyboard navigation;
- HTML yoki JSON document format;
- bundle size.

Nomzodlar implementatsiyadan oldin spike bilan baholanadi: TipTap, Lexical.

### Storage

- Canonical content editor-neutral JSON schema'da saqlanadi.
- Sanitized HTML render/export projection sifatida serverda hosil qilinadi.
- Plain text derived field qidiruv va fallback uchun saqlanadi.
- Editor tanlovi canonical schema'ni buzmasligi kerak; adapter qatlamidan
  foydalaniladi.
- Autosave 2-5 soniya debounce.
- Optimistic locking `edit_version`.
- Muhim save'lar revision history yaratadi.

### Export

- DOCX va PDF backendda yaratiladi.
- Export original template/version va context snapshotga bog'lanadi.
- File object storagega yoziladi.
- Signed URL qisqa muddatli.

### Acceptance criteria

- Refreshdan keyin draft yo'qolmaydi.
- Ikki tab conflict silent overwrite qilmaydi.
- Export editor preview bilan semantik mos.
- XSS payload saqlanmaydi yoki render qilinmaydi.

---

## 10. Work Package 5 - Competitor Intelligence

**Backend status:** 2026-06-14 kuni normalized participant/bid/award source
modellari, deterministic va idempotent aggregation, data-quality lifecycle,
Business/Enterprise API gate, usage accounting, freshness endpointi, Celery
refresh taski va regression testlari yakunlandi. Portal source adapterlari
alohida ingestion bosqichida ulanadi.

### 10.1. Data pipeline

```text
completed tender source
-> participants and bids
-> winner normalization
-> company identity resolution
-> data-quality validation
-> aggregate
-> CompetitorAnalytics snapshot
```

### 10.2. Source model ehtiyoji

Analyticsdan oldin yakunlangan natijalarni normal saqlash zarur:

- `TenderParticipant`
- `TenderBid`
- `TenderAward`

Faqat agregat model yaratish source traceability'ni yo'qotadi. Shu sabab
`CompetitorAnalytics` source result modellaridan qayta hisoblanadigan snapshot
bo'ladi.

### 10.3. CompetitorAnalytics spetsifikatsiyasi

| Maydon | Tur | Talab |
|---|---|---|
| `id` | UUID PK | |
| `scope_type` | lot/category | |
| `tender_lot` | FK nullable | Lot scope |
| `category` | CharField(255) | Category scope |
| `competitor_name` | CharField(500) | Normalized |
| `competitor_stir` | CharField(9) optional | Identity |
| `period_start/end` | DateField | |
| `rank` | PositiveInteger | |
| `total_participations` | PositiveInteger | |
| `total_wins` | PositiveInteger | wins <= participations |
| `win_rate` | Decimal(5,2) | 0..100 |
| `average_bid_amount` | Decimal(18,2) | |
| `average_discount_percentage` | Decimal(5,2) | 0..100 |
| `source_count` | PositiveInteger | Sample size |
| `raw_metrics` | JSONField | Extra metrics |
| `calculated_at` | DateTime | Freshness |

Indekslar:

- `(scope_type, tender_lot, rank)`;
- `(scope_type, category, rank)`;
- `(competitor_stir, -calculated_at)`;
- `(-calculated_at)`.

Unique:

- lot scope: `(tender_lot, competitor identity, period)`;
- category scope: `(category, competitor identity, period)`.

### 10.4. Formula

```text
discount_percent =
    ((start_price - winning_bid) / start_price) * 100

win_rate =
    (total_wins / total_participations) * 100
```

Invalid cases:

- `start_price <= 0`;
- winning bid yo'q;
- discount < 0 yoki > 100;
- wins > participations.

Bunday row analyticsga kirmaydi va data-quality logga yoziladi.

### 10.5. API

| Method | Endpoint | Izoh |
|---|---|---|
| GET | `/api/v1/competitors/top/?lot_id=` | Similar lot/category |
| GET | `/api/v1/competitors/top/?category=&period=` | Category ranking |
| GET | `/api/v1/competitors/<stir>/history/` | Competitor trend |
| GET | `/api/v1/competitors/freshness/` | Data status |

### Acceptance criteria

- Business/Enterprise gate.
- Statistikada sample size va calculated time ko'rinadi.
- Yetarli data yo'q bo'lsa `insufficient_data`.
- Ranking deterministic.
- Aggregation qayta ishlatilganda duplicate snapshot yaratmaydi.
- Har bir metric source resultlarga trace qilinadi.

---

## 11. Work Package 6 - PostgreSQL va LIKE Qidiruv

**Backend status:** 2026-06-14 kuni `DATABASE_URL`/`APP_ENV` contracti,
PostgreSQL 16 CI service, `pg_trgm` va Django `icontains` SQLiga mos
functional GIN migration, category qidiruvi, 20/100 pagination, N+1siz list,
benchmark seeder va `EXPLAIN ANALYZE` p95 gate implement qilindi. Mahalliy
muhitda PostgreSQL mavjud emas; production p95 natijasi PostgreSQL CI jobida
tekshiriladi. Source-aware `(source, external_id)` tender identity, portal
source katalogi, mavjud lotlar backfilli va asosiy domain integrity
constraintlari ham qo'shildi. Frontend debounce backend scope'idan keyinga
qoldirilgan.

### Vazifalar

- PostgreSQL 16.
- `pg_trgm` extension.
- `title`, `buyer_name`, `lot_number` uchun GIN trigram indeks.
- `category` indeksini dataset bilan benchmark.
- Django `SearchFilter` yoki explicit `Q(...__icontains)` contract.
- 300-500 ms debounce.
- pagination va ordering.
- `EXPLAIN ANALYZE` benchmark.

### Acceptance criteria

- 100 ming lotda p95 <= 300 ms.
- Search va filter birga ishlaydi.
- Raw SQL concatenation yo'q.
- Semantic RAG lot qidiruvini almashtirmaydi.

---

## 12. Work Package 7 - Superadmin Console

**Backend status (2026-06-14):** capability/MFA/step-up foundation, immutable
audit, idempotent write contract, user/company support API, plan and
subscription controls, scheduled downgrade, feature flags, maintenance
banner, template publish control, PII/audit export and source-aware overview
implemented. Payment, scraper, queue and complete AI cost/provider operations
remain explicitly `unavailable` until their authoritative domain adapters
exist. Frontend `/superadmin/` operational preview mavjud va 401/403 holatida
fail-closed ishlaydi.

### 12.1. Chegara

Superadmin uchun Business billing logikasi qayta yozilmaydi. Panel mavjud
subscription, payment, usage, feature gate, AI invocation, scraping va user
servislariga privileged orchestration qatlamini beradi. Django admin ichki
CRUD/support vositasi bo'lib qolishi mumkin, lekin mahsulot darajasidagi
operatsion dashboard alohida `/superadmin/` interfeysiga ega bo'ladi.

### 12.2. Capability matrix

| Capability | Read | Write |
|---|---|---|
| `admin_overview` | KPI, usage, health | Yo'q |
| `admin_support` | user/company timeline | block/unblock, session revoke |
| `admin_billing` | plan, subscription, payment | lifecycle override, refund review |
| `admin_operations` | AI/scraper/queue status | retry, pause source, kill switch |
| `admin_content` | template/version | publish/unpublish |
| `admin_audit` | privileged action history | Yo'q |
| `admin_root` | Barchasi | capability assignment va system settings |

`admin_root` ham auditni o'chira olmaydi. Least privilege default hisoblanadi.

### 12.3. Dashboard metric contract

| Guruh | Metrikalar | Freshness |
|---|---|---|
| Growth | total/new/active users, companies, STIR completion | 5 daqiqa |
| Subscription | active/trial/expired/cancelled, plan distribution | 5 daqiqa |
| Revenue | MRR, paid amount, failed payment, refund, churn | 5 daqiqa, reconciled |
| Business usage | generation, editor/export, competitor, team adoption | 5 daqiqa |
| AI | requests, tokens, cost, latency, failures by provider/model | 60 soniya |
| Operations | API health, queue depth, scrape freshness/errors | 30-60 soniya |

Har bir card `updated_at`, interval, timezone va source statusni ko'rsatadi.
Range: today, 7d, 30d, 90d va custom. Metric formulalari alohida dictionary
bilan versiyalanadi.

### 12.4. Boshqaruv oqimlari

#### User va company

- global search: email, telefon, ism, company, STIR;
- profile, membership, auth/session, onboarding va usage timeline;
- block/unblock va active session revoke;
- PII default maskalangan; reveal/export reason bilan auditlanadi;
- impersonation MVP scope'iga kirmaydi.

#### Tarif va subscription

- plan feature, limit, price va visibility ko'rinishi;
- company entitlement preview;
- activate/upgrade/downgrade/pause/cancel/extend;
- manual override uchun reason, effective date va optional expiry;
- scheduled downgrade billing period oxirida;
- Business imkoniyatlari alohida feature keylar orqali boshqariladi;
- subscription va payment holati bir-biridan mustaqil, lekin reconciliation
  bilan tekshiriladi.

#### Payment

- transaction va webhook timeline;
- failed/replayed webhook diagnostikasi;
- reconciliation mismatch queue;
- refund faqat provider oqimi orqali, double confirmation bilan;
- completed transaction amount/status qo'lda overwrite qilinmaydi.

#### Operations

- AI provider/model cost, latency va failure;
- scraping source/run/error/freshness;
- Celery queue va failed task retry;
- feature kill switch va maintenance banner;
- document template publish/unpublish.

### 12.5. Admin action contract

Kritik action requestida:

- capability permission;
- MFA va yaqinda bajarilgan step-up authentication;
- target va expected current version;
- majburiy `reason`;
- idempotency key;
- confirmation summary;
- append-only audit event;
- success/failure notification.

Bulk action avval dry-run/preview qaytaradi. Destructive delete o'rniga
deactivate/archive ishlatiladi.

### 12.6. API va route contract

| Guruh | Vazifa |
|---|---|
| `/api/v1/admin/overview/` | KPI, usage, revenue, health |
| `/api/v1/admin/users/` | search, detail, status, sessions |
| `/api/v1/admin/companies/` | detail, members, STIR, usage, entitlement |
| `/api/v1/admin/plans/` | plan/feature/limit configuration |
| `/api/v1/admin/subscriptions/` | lifecycle va override |
| `/api/v1/admin/payments/` | transaction, webhook, reconciliation |
| `/api/v1/admin/operations/` | AI, scraping, queue, feature flags |
| `/api/v1/admin/audit/` | immutable action history va export |

### 12.7. Acceptance criteria

- oddiy staff yoki company owner superadmin route/API'ga kira olmaydi;
- har bir write action capability va auditga ega;
- critical action step-up bo'lmasa rad etiladi;
- subscription override mavjud entitlement service orqali bajariladi;
- payment history qo'lda buzilmaydi;
- dashboard fake real-time ko'rsatmaydi va freshnessni ko'rsatadi;
- PII reveal/export va bulk action auditlanadi;
- audit event UI yoki API orqali o'chirilmaydi.

---

## 13. 4 Haftalik Kritik Delivery Rejasi

Bu execution rejasi faqat hujjatlar tasdiqlanib, foydalanuvchi kodlashni
alohida boshlatgandan va WP0 tugagandan keyin boshlanadi. PostgreSQL/Celery
yoki completed tender ingestion'ga bog'liq deliverable tegishli foundation
dependency'siz production-ready deb hisoblanmaydi.

### Hafta 1 - STIR Onboarding va Gate

Deliverables:

- registry ADR va provider contract;
- company/draft schema;
- lookup/confirm/skip API contract;
- feature matrix;
- backend va frontend UX acceptance criteria;
- test matrix.

Exit:

- barcha ochiq savollar yopilgan;
- provider sandbox yoki mock contract mavjud;
- model va API schema review qilingan.

### Hafta 2 - Document Generator Backend

Deliverables:

- documents app ADR;
- template/generated document schema;
- generation state machine;
- context allowlist;
- endpoint contract;
- async task va failure contract;
- permission matrix.

Exit:

- model/index review;
- OpenAPI draft;
- security review;
- test cases tasdiqlangan.

### Hafta 3 - Editor va Export

Deliverables:

- editor spike qarori;
- content storage ADR;
- sanitization policy;
- autosave/conflict contract;
- revision va approval lifecycle;
- PDF/DOCX export contract.

Exit:

- XSS threat model;
- editor UX prototype;
- export acceptance fixtures.

### Hafta 4 - Competitor Intelligence

Deliverables:

- completed tender source schema;
- identity resolution qoidalari;
- analytics model/index;
- formula va data-quality qoidalari;
- dashboard API contract;
- freshness va insufficient-data UX.

Exit:

- sample datasetda expected ranking fixture;
- legal/source review;
- aggregation test specification.

---

## 14. Dependency va Critical Path

```text
Plan approval
-> external/legal decisions
-> WP0 security stabilization
-> PostgreSQL + Redis/Celery foundation
-> STIR onboarding + subscription gate
-> document generator
-> editor/export

Portal legal approval
-> completed tender ingestion
-> participant/bid/award source models
-> competitor aggregation
-> Business dashboard

Identity/MFA foundation
-> admin capability matrix
-> immutable audit
-> superadmin read-only dashboard
-> controlled write operations
```

Parallel bajarilishi mumkin:

- STIR provider contract va editor spike;
- tariff/feature matrix va document template legal review;
- LIKE benchmark dataset tayyorlash va competitor formula fixture'lari.

Bloklovchi dependency'lar:

| Deliverable | Bloklovchi shart |
|---|---|
| Real STIR lookup | Ruxsatli provider, credential va API contract |
| Production document generation | Tasdiqlangan template va legal disclaimer |
| Async generation/export | Redis/Celery va object storage |
| Fast production LIKE search | PostgreSQL + `pg_trgm` |
| Competitor dashboard | Ruxsatli completed-results source va source models |
| Paid feature gate | Subscription lifecycle va usage accounting |
| Superadmin write controls | MFA/step-up, capability permission va audit storage |

---

## 15. Keyingi Platforma Bosqichlari

### Phase A - Foundation

- PostgreSQL, Redis, Celery, Docker.
- Environment-specific settings.
- Logging, Sentry, backup.
- OpenAPI va CI.

### Phase B - Tender ingestion

- Birinchi real portal adapter.
- ScrapeRun va error monitoring.
- PDF/DOCX parsing.
- Completed results ingestion.

### Phase C - RAG

- pgvector.
- chunk/embedding pipeline.
- citations.
- eval dataset.
- provider fallback.

### Phase D - Telegram

**Holat:** backend data-contract modellari, migratsiya va invariant testlari
mavjud; bot runtime, linking endpointlari, HMAC `initData` verification va
Mini App UI hali rejalashtirilgan Phase D scope'ida.

- `aiogram` asosidagi bot va webhook/polling environment contracti;
- bir martalik, muddati cheklangan account-link challenge;
- `TelegramIdentity`: company member, immutable Telegram numeric user ID,
  oxirgi ma'lum username, verification va relink statusi;
- `TelegramLinkChallenge`: hash qilingan token, expiry, attempt count va
  consumed timestamp;
- `TelegramMiniAppSession`: init-data fingerprint, auth time, last active,
  device metadata va revoke holati;
- `NotificationPreference` va `NotificationDelivery` orqali role/permission
  bilan cheklangan match, deadline, analysis va system xabarlari;
- TMA `initData` payloadini serverda bot token asosidagi HMAC bilan tekshirish;
- `auth_date` freshness, replay resistance, rate limit va audit;
- username o'zgarganda admin `Update/Re-link Telegram` oqimi va
  `awaiting_new_session_verification` statusi;
- username yoki hash mismatch holatida avtomatik account takeover yo'q:
  corporate password va zarur bo'lsa step-up orqali qayta bog'lash;
- web va Mini App sessiyalarini bitta revoke action bilan bekor qilish;
- Mini App dashboard faqat member explicit permissionlari bo'yicha
  ruxsat etilgan bo'limlarni render qiladi;
- landing page'da Telegram Mini App ekotizimi alohida feature sifatida
  ko'rsatiladi, lekin mavjud bo'lmagan capability “live” deb da'vo qilinmaydi.

Target API contract:

| Method | Endpoint | Vazifa |
|---|---|---|
| POST | `/api/v1/telegram/tma/auth/` | `initData`ni tekshirib TMA session yaratish |
| POST | `/api/v1/telegram/link/challenges/` | Link/re-link challenge yaratish |
| POST | `/api/v1/telegram/link/confirm/` | Bot yoki TMA orqali challenge tasdiqlash |
| PATCH | `/api/v1/teams/members/<uuid>/telegram/` | Admin relink jarayonini boshlashi |
| DELETE | `/api/v1/teams/members/<uuid>/telegram/` | Identityni ajratish va sessionlarni revoke qilish |
| GET/PATCH | `/api/v1/telegram/notifications/` | Ruxsat doirasidagi notification sozlamalari |
| POST | `/api/v1/telegram/sessions/revoke/` | Joriy yoki barcha TMA sessionlarini bekor qilish |

Acceptance criteria:

- forged, expired yoki replay qilingan `initData` rad etiladi;
- faqat username mosligi account link uchun yetarli emas;
- permission olib tashlanganda TMA menyusi va backend endpoint darhol yopiladi;
- member revoke web va TMA token/sessionlarini birga bekor qiladi;
- bot token frontend bundle, URL yoki logga chiqmaydi;
- barcha link/re-link/revoke actionlari auditlanadi;
- notification delivery idempotent va retry-safe.

### Phase E - Billing

- subscription/usage;
- CLICK prepare/complete;
- idempotency;
- reconciliation.

### Phase E.1 - Superadmin

- read-only overview va metric dictionary;
- user/company support console;
- plan, entitlement va subscription controls;
- payment/reconciliation operations;
- AI/scraping/queue control;
- immutable audit va privileged alerts.

### Phase F - Advanced Enterprise

- team tasks;
- competitor trend/export;
- audit;
- higher limits.

---

## 16. Migration Strategiyasi

Har bir schema change:

1. Additive migration.
2. Backfill command/task.
3. Application dual-read yoki compatibility.
4. Constraint/index qo'shish.
5. Eski fieldni keyingi release'da olib tashlash.

Katta indekslar productionda imkon qadar concurrent yaratiladi.
Migration oldidan:

- backup;
- row count;
- estimated lock time;
- rollback;
- staging rehearsal.

---

## 17. Security Threat Checklist

### STIR

- enumeration/rate abuse;
- provider credential leakage;
- forged registry response;
- user edit va registry value aralashishi;
- PII logga chiqishi.

### Documents

- prompt injection;
- XSS;
- unauthorized company document access;
- stale edit overwrite;
- malicious export content;
- raw provider payloadning LLMga yuborilishi.

### Competitors

- noto'g'ri company identity merge;
- statistikadan g'alaba kafolati sifatida foydalanish;
- insufficient sample;
- noqonuniy yoki ToSga zid scraping;
- stale analytics.

### Superadmin

- privilege escalation va stolen admin session;
- PII overexposure yoki bulk export;
- subscription/payment fraud;
- audit tampering;
- dangerous bulk action;
- fake/stale real-time metric;
- feature kill switch misuse.

Har bir threat uchun mitigation va test case implementation issue'da bo'ladi.

---

## 18. Testing Strategiyasi

### Unit

- registry normalization;
- feature gate;
- document state transition;
- formula va aggregation;
- sanitization;
- identity resolution.
- admin capability va metric calculation.

### Integration

- registry provider;
- Celery generation;
- object storage/export;
- subscription + gate;
- completed tender ingestion.
- subscription override, payment reconciliation va admin audit.

### API

- auth;
- ownership;
- role;
- validation;
- idempotency;
- pagination/filtering;
- error envelope.

### E2E

1. Register -> STIR lookup -> edit -> confirm.
2. Register -> skip STIR -> restricted feature.
3. Add STIR later -> gate opens.
4. Business -> generate -> edit -> approve -> export.
5. Business -> competitor dashboard.
6. Superadmin -> user/company -> subscription override -> audit.
7. Superadmin -> operations alert -> retry/kill switch -> audit.

### Non-functional

- LIKE search benchmark;
- registry timeout;
- document generation latency;
- concurrent editor conflict;
- aggregation idempotency;
- security scans.
- admin privilege escalation, step-up va stale metric tests.

---

## 19. Definition of Ready

Work package implementatsiyaga tayyor, agar:

- scope va non-goal yozilgan;
- model/API contract tasdiqlangan;
- migration va rollback rejasi mavjud;
- permission matrix mavjud;
- acceptance criteria test qilinadigan;
- dependency va secretlar aniqlangan;
- UX state'lar mavjud;
- threat review bajarilgan;
- ochiq savol qolmagan yoki aniq owner/deadline bor.

---

## 20. Definition of Done

- implementation acceptance criteria'ga mos;
- unit/integration/API testlar green;
- lint/build/migration check green;
- ownership va feature gate testlangan;
- observability qo'shilgan;
- documentation va OpenAPI yangilangan;
- staging smoke test o'tgan;
- rollback sinovdan o'tgan;
- product owner tasdiqlagan.

---

## 21. Ochiq Savollar

Kodlashdan oldin yopilishi kerak:

1. Qaysi Soliq/Statistika registry API rasmiy va foydalanishga ruxsatli?
2. Registry API sandbox, auth, limit va SLA qanday?
3. Business document generation va team seat limiti qanday bo'ladi?
4. Template'larni kim huquqiy tasdiqlaydi?
5. PDF/DOCX export uchun talab etilgan rasmiy formatlar qaysi?
6. Completed tender participant/bid data qaysi portalda ochiq?
7. Competitor identity uchun STIR har doim mavjudmi; bo'lmasa qaysi
   deterministic fallback key ishlatiladi?
8. Business beta uchun competitor freshness SLO 30 daqiqami yoki boshqa
   qiymatmi?
9. Superadmin rollarini kimlarga berish vakolati bor?
10. Subscription manual override uchun maksimal muddat va approval siyosati?
11. Refund action bir yoki ikki admin tasdig'ini talab qiladimi?
12. Moliyaviy dashboardda MRR va churnning biznes formulasi qanday?
13. Telegram bot username, webhook domain va production bot token owneri kim?
14. TMA `initData` uchun maksimal `auth_date` yoshi va replay retention qancha?
15. Telegram relink uchun corporate passwordning o'zi yetarlimi yoki MFA ham
    majburiymi?

---

## 22. Tasdiqlash Ketma-ketligi

1. Product scope review.
2. Legal/data source review.
3. Model va API architecture review.
4. Security review.
5. UX flow review.
6. Milestone va acceptance criteria approval.
7. Shundan keyin alohida implementatsiya topshirig'i.
