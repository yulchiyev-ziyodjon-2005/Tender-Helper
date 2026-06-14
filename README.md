# TenderHelper AI

O'zbekiston kichik va o'rta bizneslari uchun AI Tender Mentor platformasi.

TenderHelper davlat va korporativ tenderlarni topish, hujjatlarni tushunish,
xavflarni aniqlash va ishtirok narxini hisoblashga yordam beradi.

> Loyiha hozir demo/MVP prototip bosqichida. Production arxitekturasi,
> xavfsizlik talablari va roadmap [`Plan.md`](Plan.md) da belgilangan.

## Asosiy Imkoniyatlar

- tender lotlarini qidirish va filtrlash;
- tender hujjatlarini AI orqali tahlil qilish;
- murakkab talablarni oddiy tilda tushuntirish;
- red flag va yetishmayotgan hujjatlarni aniqlash;
- kompaniya profiliga moslik bahosi;
- QQS, komissiya, Stop-Loss va foyda kalkulyatori;
- ko'p tilli, dark mode'li responsive interfeys.

Rejalashtirilgan imkoniyatlar:

- real portal scraping;
- PostgreSQL, pgvector, Redis va Celery;
- evidence va citation bilan RAG tahlili;
- Telegram bot va Mini App;
- CLICK billing;
- Business tarifida AI hujjat generatori va inline editor;
- team va competitor intelligence;
- user, obuna, payment va operatsiyalar uchun Superadmin Console.

## Texnologiyalar

| Qatlam | Hozirgi holat | Target |
|---|---|---|
| Frontend | React 19, Vite, Tailwind CSS | PWA va Telegram Mini App |
| Backend | Django 5, Django REST Framework | Async worker arxitekturasi |
| Database | SQLite | PostgreSQL va pgvector |
| AI | Google Gemini prototipi | Provider gateway, Gemini va Groq |
| Auth | JWT, OTP, Google OAuth | Xavfsiz cookie yoki one-time code |
| Queue | Yo'q | Redis va Celery |

## Repository Tuzilmasi

```text
TenderHelper/
|-- backend/              # Django REST API
|   |-- users/            # Auth va foydalanuvchilar
|   |-- companies/        # Kompaniya profillari
|   |-- tenders/          # Tenderlar va scraping
|   |-- analysis/         # AI tahlil va kalkulyator
|   |-- subscriptions/    # Tarif va billing
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
pip install -r requirements.txt
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
- `DEBUG`
- `ALLOWED_HOSTS`
- `CORS_ALLOWED_ORIGINS`
- `GEMINI_API_KEY`
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- SMS va payment provider sozlamalari

## Tekshiruv

Frontend:

```powershell
npm run lint
npm run build
```

Backend:

```powershell
python manage.py check
python manage.py test
```

## Hujjatlar

- [Asosiy reja](Plan.md)
- [Implementation reja](IMPLEMENTATION_PLAN.md)
- [UI/UX dizayn spetsifikatsiyasi](DESIGN.md)
- [Amaldagi demo API snapshoti](docs/API.md)
- [Tarixiy hujjatlar](docs/archive/README.md)

`Plan.md` strategik ustuvor manba. `IMPLEMENTATION_PLAN.md` bajarilish
contractini, `DESIGN.md` target interfeysni, `docs/API.md` esa hozir kodda
mavjud demo endpointlarni ko'rsatadi.

## Litsenziya

Xususiy loyiha. Barcha huquqlar himoyalangan.
