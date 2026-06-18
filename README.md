# TenderHelper AI

O'zbekiston kichik va o'rta bizneslari uchun AI Tender Mentor platformasi.

TenderHelper davlat va korporativ tenderlarni topish, hujjatlarni tushunish,
xavflarni aniqlash va ishtirok narxini hisoblashga yordam beradi.

> Loyiha hozir demo/MVP prototip bosqichida. Production arxitekturasi,
> xavfsizlik talablari va roadmap [`Plan.md`](Plan.md) da belgilangan.

**Snapshot:** 2026-06-18. Telegram uchun backend data-contract modellari
mavjud, lekin bot runtime, linking endpointlari va Mini App auth oqimi
[`docs/TELEGRAM_TMA_PLAN.md`](docs/TELEGRAM_TMA_PLAN.md) bo'yicha keyingi
Phase D scope hisoblanadi.

## Asosiy Imkoniyatlar

- tender lotlarini qidirish va filtrlash;
- tender hujjatlarini AI orqali tahlil qilish;
- murakkab talablarni oddiy tilda tushuntirish;
- red flag va yetishmayotgan hujjatlarni aniqlash;
- kompaniya profiliga moslik bahosi;
- QQS, komissiya, Stop-Loss va foyda kalkulyatori;
- Business/Enterprise uchun backend AI hujjat generatori, revision,
  approval va PDF/DOCX export;
- Business/Enterprise uchun completed tender natijalaridan hisoblanadigan
  traceable competitor ranking, history va freshness API;
- capability, MFA/step-up, immutable audit, user/company support, plan va
  subscription boshqaruviga ega Superadmin backend control plane;
- responsive landing, split-screen auth, STIR onboarding, legal sahifalar,
  Business Team Hub va Superadmin preview frontend;
- role va explicit permission asosidagi team sidebar, member invitation,
  temporary password, force-change va session revoke;
- ko'p tilli, dark mode'li responsive interfeys.

Rejalashtirilgan imkoniyatlar:

- real portal scraping;
- PostgreSQL, pgvector, Redis va Celery;
- evidence va citation bilan RAG tahlili;
- Telegram bot va Mini App;
- CLICK billing;
- AI hujjat generatorining yakuniy rich-text inline editori;
- team task va competitor trend/export kengaytmalari;
- payment, scraper, queue va to'liq AI operations adapterlari.

Tariflar:

| Tarif | Oylik | Yillik |
|---|---:|---:|
| Free | 0 UZS | 0 UZS |
| Pro | 350,000 UZS | 3,360,000 UZS |
| Business | 950,000 UZS | 9,120,000 UZS |

Business Team, Document Generator va Competitor Intelligence uchun STIR
talab qilinadi. Checkout payment provider tasdig'isiz obunani faollashtirmaydi.

## Texnologiyalar

| Qatlam | Hozirgi holat | Target |
|---|---|---|
| Frontend | React 19, Vite, Tailwind CSS | PWA va Telegram Mini App |
| Backend | Django 5, Django REST Framework | Async worker arxitekturasi |
| Database | SQLite local fallback, PostgreSQL 16 config/CI | PostgreSQL va pgvector |
| AI | Google Gemini prototipi | Provider gateway, Gemini va Groq |
| Auth | JWT, OTP, Google OAuth | Xavfsiz cookie yoki one-time code |
| Queue | Celery task boundary, local eager mode | Production Redis workers |

## Repository Tuzilmasi

```text
TenderHelper/
|-- backend/              # Django REST API
|   |-- users/            # Auth va foydalanuvchilar
|   |-- companies/        # Kompaniya profillari
|   |-- tenders/          # Tenderlar va scraping
|   |-- analysis/         # AI tahlil va kalkulyator
|   |-- documents/        # Generator, editor lifecycle va export
|   |-- subscriptions/    # Tarif va billing
|   |-- controlplane/     # Superadmin capability, audit va orchestration
|   |-- teams/            # Enterprise team
|   `-- competitors/      # Competitor intelligence
|-- frontend/             # React PWA
|-- docs/
|   |-- API.md
|   `-- archive/          # Eski reja va texnik topshiriqlar
|-- Plan.md               # Canonical strategik va texnik reja
|-- IMPLEMENTATION_PLAN.md # Work package va acceptance criteria
|-- DESIGN.md             # Canonical UI/UX spetsifikatsiyasi
`-- README.md
```

## Local Ishga Tushirish

Talablar:

- Python 3.11+
- Node.js 20.19+ yoki 22.12+

Backend:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
python manage.py migrate
python manage.py runserver
```

Frontend:

```powershell
cd frontend
npm install
npm run dev
```

Manzillar:

- Frontend: `http://localhost:5173`
- API: `http://localhost:8000/api/v1/`
- Health check: `http://localhost:8000/api/health/`
- Admin: `http://localhost:8000/admin/`

## Environment

Root katalogdagi `.env.example` faylidan `.env` yarating. Secret va API
kalitlarini Git repositoryga qo'shmang.

Muhim o'zgaruvchilar:

- `SECRET_KEY`
- `APP_ENV`
- `DATABASE_URL`
- `DATABASE_CONN_MAX_AGE`
- `DEBUG`
- `ALLOWED_HOSTS`
- `CORS_ALLOWED_ORIGINS`
- `GEMINI_API_KEY`
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `CELERY_BROKER_URL`
- `COMPETITOR_MIN_SAMPLE_SIZE`
- `COMPETITOR_FRESHNESS_SECONDS`
- `COMPETITOR_PERIOD_DAYS`
- `ADMIN_MFA_PROVIDER`
- `ADMIN_MFA_SESSION_SECONDS`
- `ADMIN_STEP_UP_SECONDS`
- Phase D uchun rejalashtirilgan `TELEGRAM_BOT_TOKEN`,
  `TELEGRAM_WEBHOOK_SECRET`, `TELEGRAM_TMA_AUTH_MAX_AGE_SECONDS`
- SMS va payment provider sozlamalari

## Tekshiruv

Windows lokal quality gate:

```powershell
.\scripts\quality-backend.ps1
cd frontend
npm run lint
npm run build
```

Frontend/API contract smoke:

```powershell
# 1) backend server alohida terminalda ishlasin: http://127.0.0.1:8000
cd frontend
$env:API_CONTRACT_API_BASE_URL='http://127.0.0.1:8000/api/v1'
npm run contract:api

# Authenticated dashboard/team/admin contract uchun ixtiyoriy:
$env:API_CONTRACT_EMAIL='user@example.uz'
$env:API_CONTRACT_PASSWORD='strong-password'
npm run contract:api
```

`contract:api` frontend endpoint registrysini real backendga qarshi tekshiradi:
health, public tenders, Google config, 401 auth guard envelope, invalid login
va credential berilsa authenticated session/profile/entitlement/team/admin
contractlari.

Frontend:

```powershell
npm run lint
npm run build
```

Backend:

```powershell
$env:APP_ENV='test'
$env:SECRET_KEY='ci-only-secret-key-long-enough-for-database-tests'
$env:DEBUG='False'
$env:ALLOWED_HOSTS='localhost,testserver'
$env:CORS_ALLOWED_ORIGINS='http://localhost:5173'
$env:DEMO_MODE='False'
$env:CELERY_TASK_ALWAYS_EAGER='True'
python manage.py check
python manage.py makemigrations --check --dry-run
python -m ruff check . --no-cache
python manage.py test
python manage.py benchmark_tender_search --query server --allow-sqlite
```

## Hujjatlar

- [Asosiy reja](Plan.md)
- [Implementation reja](IMPLEMENTATION_PLAN.md)
- [UI/UX dizayn spetsifikatsiyasi](DESIGN.md)
- [Amaldagi demo API snapshoti](docs/API.md)
- [Database readiness va qolgan schema bosqichlari](docs/DATABASE_READINESS.md)
- [VPS deployment runbook](docs/DEPLOYMENT.md)
- [Telegram Bot va Mini App Phase D rejasi](docs/TELEGRAM_TMA_PLAN.md)
- [Tarixiy hujjatlar](docs/archive/README.md)

Rasmiy aloqa:

- `info@tenderhelperai.com`
- `+998 (94) 994-05-04`
- Telegram kanal: <https://t.me/+fg-PELSnruU0NjVi>
- Admin support: <https://t.me/Zdn_Ychv>

`Plan.md` strategik ustuvor manba. `IMPLEMENTATION_PLAN.md` bajarilish
contractini, `DESIGN.md` target interfeysni, `docs/API.md` esa hozir kodda
mavjud demo endpointlarni ko'rsatadi.

## Litsenziya

Xususiy loyiha. Barcha huquqlar himoyalangan.
