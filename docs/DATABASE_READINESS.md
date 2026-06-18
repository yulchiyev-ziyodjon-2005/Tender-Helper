# Database Readiness

**Yangilangan:** 2026-06-18

## Joriy Foundation

Quyidagi talablar schema va migratsiya darajasida mavjud:

- local SQLite fallback va staging/production uchun majburiy PostgreSQL;
- PostgreSQL `pg_trgm` qidiruv indekslari va 100k benchmark CI gate;
- source-aware tender identity: `TenderSource` va
  `(source, external_id)` unique contract;
- portal source katalogi va eski lotlar uchun data backfill;
- STIR format va STIR/skip consistency constraintlari;
- user login identity va case-insensitive email uniqueness;
- user MFA state holderlari;
- `CompanyMember` company-scoped Owner/Admin/Manager/Analyst/Viewer rollari,
  explicit permissionlar va Search/AI/Documents/Competitor visual flaglari;
- `TeamSession` JTI, audience, auth version, MFA, expiry, device, browser, IP,
  last-active va revoke metadata;
- owner membership backfill va yangi kompaniyalar uchun automatic owner signal;
- fixture-safe owner signal;
- Telegram numeric identity, dynamic username sync metadata, link challenge va
  Mini App session/replay context modellari;
- Telegram/email/push notification preference va idempotent delivery
  modellari;
- WP7 append-only admin audit log va invariant diagnostic counterlari;
- tender narxi, zakalat va deadline integrity constraintlari;
- analysis score va calculator amount constraintlari;
- subscription period, schedule pair, trial va price constraintlari;
- document version/export size constraintlari;
- competitor rank, source count va metric range constraintlari;
- CLICK-backed `PaymentTransaction` va idempotent `WebhookEvent` payment
  ledger modellari;
- subscription, usage, document version va competitor snapshot unique
  constraintlari.

## Keyingi Phase Modellari

Canonical `Plan.md`dagi quyidagi modellar hali joriy work package scope'ida
implement qilinmagan:

| Phase | Qolgan modellar |
|---|---|
| Membership | `UserConsent` |
| RAG/AI audit | `AnalysisCitation` |
| Recommendation | `CompanyTenderMatch`, `SavedSearch`, `Watchlist` |
| Billing | reconciliation job, refund/reversal audit modellari zarur bo'lsa |
| Enterprise | `TeamTask`, `TaskComment`, trend/export modellari |

Bu ro'yxat joriy schema xatosi emas. Har bir guruh tegishli provider,
permission contracti va work package bilan additive migration orqali
qo'shiladi.

## Ochiq Gate

- PostgreSQL 16 muhitida 100 ming lot uchun p95 <= 300 ms benchmark.
- Off-host backup restore va rollback drill.
- Browser token storage: standart sessiya `sessionStorage`, explicit
  `Remember me` esa `localStorage`; keyingi security phase'da refresh tokenni
  HttpOnly cookie'ga ko'chirish.
- Real portal, registry va payment provider contractlari.
- Telegram bot secret ownership, webhook domain, `initData` freshness va
  replay-retention policy.
- Barcha production subdomainlari HTTPS ekanligi tasdiqlangach
  `SECURE_HSTS_INCLUDE_SUBDOMAINS=True` va `SECURE_HSTS_PRELOAD=True` bilan
  yakuniy deploy check.

## 2026-06-15 Tekshiruv Natijasi

- migration drift: yo'q (`makemigrations --check --dry-run`);
- pending migration: yo'q (`migrate --plan`);
- PostgreSQL 16.14 Windows xizmati ishga tushirilgan;
- `tender_helper_prod` bazasi alohida `tender_admin` roli bilan ishlaydi;
- `pg_trgm` 1.6 faol va lot qidiruvi uchun 4 ta GIN trigram indeks mavjud;
- SQLite backup olindi va 110 obyektli UTF-8 fixture PostgreSQLga tiklandi;
- source/target obyekt sonlari mos: 110/110;
- full backend suite local test muhitida: 160 test o'tdi;
- PostgreSQL lock portability auditi bajarildi: nullable outer joinlar bilan
  `select_for_update(of=('self',))` ishlatiladi;
- frontend lint va production build o'tdi;
- local data audit: 4 company va 4 owner membership; orphan owner yo'q;
- seed pricing: Free 0, Pro 350000, Business 950000 UZS/oy;
- production security defaults: SSL redirect, secure session cookie, secure
  CSRF cookie va bir yillik HSTS faol;
- HSTS preload faqat DNS/subdomain HTTPS auditi tugagach yoqiladi.

## 2026-06-16 Provisioning Natijasi

- `settings.py` deploy muhitlari uchun `DATABASE_URL`ni yagona database
  manbasi sifatida ishlatadi;
- `DATABASE_URL` bo'lmaganda faqat local/test execution cycle uchun
  in-memory SQLite fallback ishlaydi; staging/production PostgreSQLsiz
  start bo'lmaydi;
- production default host/origin/email/SMS sozlamalari
  `tenderhelperai.com`, `api.tenderhelperai.com`, Zoho SMTP 465/SSL va
  Eskiz provider kontraktiga moslandi;
- PostgreSQL role: `tender_admin`;
- `tender_admin` uchun `CREATEDB` smoke testi create/drop orqali o'tdi;
- database: `tender_helper_prod`;
- `pg_trgm` extension `tender_helper_prod` ichida faol: version 1.6;
- `python manage.py migrate --noinput`: pending migration yo'q;
- PostgreSQL test runner: oldingi drillda 141 test o'tdi, test database
  yaratish/o'chirish muvaffaqiyatli; joriy lokal SQLite gate 160 testga
  kengaydi;
- `ruff`, `manage.py check`, `makemigrations --check --dry-run` va frontend
  production build o'tdi;
- test suite production HTTPS redirect sababli test contextda
  `SECURE_SSL_REDIRECT=False` override bilan yuritiladi;
- `check --deploy` faqat `SECURE_HSTS_INCLUDE_SUBDOMAINS` va
  `SECURE_HSTS_PRELOAD` bo'yicha ogohlantiradi; bu DNS/subdomain HTTPS
  auditi tugagach yoqiladigan ataylab ochiq security gate.
