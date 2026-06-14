# 🏗️ TenderHelper AI — To'liq Dasturiy Ishlab Chiqish Rejasi

**Versiya:** 1.0 | **Sana:** 2026-05-22  
**Maqsad:** MVP platformasini bosqichma-bosqich professional darajada qurish

---

## 📋 Umumiy Ko'rinish

### Loyiha Tuzilmasi (Monorepo)

```
TenderHelper/
├── TZ.md                          # Texnik topshiriq
├── TZ.txt                         # Asl versiya (arxiv)
├── .env.example                   # Environment variables namunasi
├── .gitignore
├── README.md
│
├── backend/                       # Django 5.0 + DRF
│   ├── manage.py
│   ├── requirements.txt
│   ├── core/                      # Django project settings
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── asgi.py
│   ├── users/                     # Auth: Phone+OTP, Google OAuth
│   │   ├── models.py              # CustomUser
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── services/
│   │       ├── otp_service.py     # SMS OTP (Eskiz/PlayMobile)
│   │       └── google_auth.py     # Google OAuth token verification
│   ├── companies/                 # Korxona profili
│   │   ├── models.py              # CompanyProfile
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   ├── tenders/                   # Tender lotlari
│   │   ├── models.py              # TenderLot, TenderDocumentChunk
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── filters.py             # 25+ filtr logikasi
│   │   └── services/
│   │       └── scraper.py         # Portal scraping service
│   ├── analysis/                  # AI tahlil
│   │   ├── models.py              # AITenderAnalysis, SmartCalculator
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── services/
│   │       ├── gemini_service.py   # Gemini API wrapper
│   │       ├── prompt_templates.py # System prompt va JSON schema
│   │       └── json_parser.py      # SafeJSONParser
│   ├── subscriptions/             # Tarif va to'lovlar
│   │   ├── models.py              # Subscription, Payment
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── services/
│   │       ├── payme.py
│   │       ├── click.py
│   │       └── uzum.py
│   ├── teams/                     # Enterprise jamoaviy ishlash
│   │   ├── models.py              # TeamCollaborationTask
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   └── competitors/               # Raqobatchi razvedkasi
│       ├── models.py              # CompetitorDossier
│       ├── serializers.py
│       ├── views.py
│       └── urls.py
│
├── frontend/                      # React 18 + Vite + Tailwind
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── public/
│   │   ├── manifest.json          # PWA manifest
│   │   ├── sw.js                  # Service Worker
│   │   ├── favicon.ico
│   │   └── icons/                 # PWA ikonkalar
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       ├── index.css              # Tailwind imports + custom tokens
│       ├── api/
│       │   ├── client.js          # Axios instance + interceptors
│       │   ├── auth.js            # Auth API calls
│       │   ├── tenders.js         # Tender API calls
│       │   ├── analysis.js        # Analysis API calls
│       │   └── subscriptions.js   # Payment API calls
│       ├── store/
│       │   ├── authStore.js       # Zustand — auth holati
│       │   ├── tenderStore.js     # Zustand — tenderlar
│       │   └── uiStore.js         # Zustand — dark mode, sidebar
│       ├── hooks/
│       │   ├── useAuth.js
│       │   ├── useTenders.js
│       │   └── useAnalysis.js
│       ├── components/
│       │   ├── ui/                # Shadcn-style base components
│       │   │   ├── Button.jsx
│       │   │   ├── Input.jsx
│       │   │   ├── Card.jsx
│       │   │   ├── Badge.jsx
│       │   │   ├── Modal.jsx
│       │   │   ├── Tabs.jsx
│       │   │   ├── Skeleton.jsx
│       │   │   ├── ProgressBar.jsx
│       │   │   └── Toast.jsx
│       │   ├── layout/
│       │   │   ├── Navbar.jsx
│       │   │   ├── Sidebar.jsx
│       │   │   ├── MobileNav.jsx
│       │   │   └── Footer.jsx
│       │   ├── auth/
│       │   │   ├── PhoneLoginForm.jsx
│       │   │   ├── OTPVerification.jsx
│       │   │   ├── GoogleLoginButton.jsx
│       │   │   └── OnboardingStepper.jsx
│       │   ├── dashboard/
│       │   │   ├── SearchBar.jsx
│       │   │   ├── FilterPanel.jsx
│       │   │   ├── TenderCard.jsx
│       │   │   └── TenderList.jsx
│       │   ├── analysis/
│       │   │   ├── TextInputArea.jsx
│       │   │   ├── FileUpload.jsx
│       │   │   ├── AnalysisProgress.jsx
│       │   │   ├── SummaryCard.jsx
│       │   │   ├── RedFlagsList.jsx
│       │   │   ├── RequirementsList.jsx
│       │   │   ├── DocumentChecklist.jsx
│       │   │   ├── DecisionCard.jsx
│       │   │   └── SmartCalculator.jsx
│       │   ├── subscription/
│       │   │   ├── PricingTable.jsx
│       │   │   └── PaymentModal.jsx
│       │   └── team/              # Enterprise
│       │       ├── TaskBoard.jsx
│       │       └── CompetitorCard.jsx
│       ├── pages/
│       │   ├── LoginPage.jsx
│       │   ├── OnboardingPage.jsx
│       │   ├── DashboardPage.jsx
│       │   ├── AnalysisPage.jsx
│       │   ├── CalculatorPage.jsx
│       │   ├── PricingPage.jsx
│       │   ├── ProfilePage.jsx
│       │   ├── TeamPage.jsx       # Enterprise
│       │   └── NotFoundPage.jsx
│       ├── routes/
│       │   ├── AppRouter.jsx
│       │   ├── PrivateRoute.jsx
│       │   └── PublicRoute.jsx
│       └── utils/
│           ├── formatters.js      # Raqamlarni formatlash (10 000 000)
│           ├── validators.js      # Phone, STIR validatsiya
│           └── constants.js       # Ranglar, API URL, limitlar
│
└── docs/                          # Loyiha hujjatlari
    ├── API.md                     # API dokumentatsiyasi
    └── DEPLOYMENT.md              # Deploy qo'llanmasi
```

---

## 🔷 BOSQICH 1: Loyiha Infratuzilmasi (Foundation)
**Muddat:** 1-2 kun

### 1.1. Backend Initsializatsiya

| # | Vazifa | Tafsilot |
|---|--------|----------|
| 1.1.1 | Django loyiha yaratish | `django-admin startproject core backend/` |
| 1.1.2 | Virtual environment | `python -m venv venv` |
| 1.1.3 | Requirements.txt | Django 5.0, DRF, cors-headers, simplejwt, python-dotenv, google-auth, requests |
| 1.1.4 | Settings sozlash | INSTALLED_APPS, CORS, JWT config, AUTH_USER_MODEL |
| 1.1.5 | .env fayl | SECRET_KEY, DEBUG, GEMINI_API_KEY, SMS_API_KEY, GOOGLE_CLIENT_ID |
| 1.1.6 | .gitignore | venv/, .env, __pycache__, db.sqlite3, node_modules/ |

**Settings.py muhim sozlamalar:**
```python
AUTH_USER_MODEL = 'users.CustomUser'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '15/minute',
        'user': '60/minute',
    },
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}
```

### 1.2. Frontend Initsializatsiya

| # | Vazifa | Tafsilot |
|---|--------|----------|
| 1.2.1 | Vite + React yaratish | `npm create vite@latest frontend -- --template react` |
| 1.2.2 | Tailwind CSS o'rnatish | `npm install -D tailwindcss postcss autoprefixer` |
| 1.2.3 | Asosiy paketlar | axios, react-router-dom, zustand, @tanstack/react-query, lucide-react |
| 1.2.4 | Tailwind config | Ranglar palitrasi, shriftlar, dark mode='class' |
| 1.2.5 | Folder tuzilmasi | api/, store/, components/, pages/, hooks/, utils/, routes/ |
| 1.2.6 | PWA sozlash | vite-plugin-pwa, manifest.json, service worker |

**tailwind.config.js rang palitrasi:**
```javascript
colors: {
  primary: {
    50: '#EFF6FF', 100: '#DBEAFE', 200: '#BFDBFE',
    500: '#3B82F6', 600: '#2563EB', 700: '#1D4ED8',
    800: '#1E3A8A', 900: '#1E3A5F', 950: '#0F172A',
  },
  success: { 400: '#34D399', 500: '#10B981', 600: '#059669' },
  warning: { 400: '#FBBF24', 500: '#F59E0B', 600: '#D97706' },
  danger:  { 400: '#F87171', 500: '#EF4444', 600: '#DC2626' },
}
```

### 1.3. Git va README

| # | Vazifa |
|---|--------|
| 1.3.1 | Git repozitoriya initsializatsiya |
| 1.3.2 | README.md — loyiha tavsifi, o'rnatish qo'llanmasi |
| 1.3.3 | Birinchi commit: "Initial project structure" |

---

## 🔷 BOSQICH 2: Auth Tizimi (Autentifikatsiya)
**Muddat:** 2-3 kun

### 2.1. Backend — CustomUser modeli

| # | Vazifa | Tafsilot |
|---|--------|----------|
| 2.1.1 | `users` app yaratish | `python manage.py startapp users` |
| 2.1.2 | CustomUser modeli | UUID PK, phone, email, full_name, role, auth_provider |
| 2.1.3 | Custom UserManager | Phone number orqali create_user/create_superuser |
| 2.1.4 | Admin panel registratsiya | CustomUserAdmin |
| 2.1.5 | Migratsiya | `makemigrations` + `migrate` |

### 2.2. Backend — OTP Service

| # | Vazifa | Tafsilot |
|---|--------|----------|
| 2.2.1 | OTP generatsiya | 6 raqamli kod, 3 daqiqa amal muddati |
| 2.2.2 | OTP saqlash | Cache (Django cache framework) yoki alohida OTPVerification modeli |
| 2.2.3 | SMS yuborish | Eskiz.uz yoki PlayMobile API orqali (MVP: console output fallback) |
| 2.2.4 | Rate limit | Bitta raqamga 1 daqiqada 1 ta OTP |

### 2.3. Backend — Auth API Endpoints

| # | Endpoint | Vazifa |
|---|----------|--------|
| 2.3.1 | `POST /api/v1/auth/send-otp/` | Telefon raqamini qabul qilish → OTP yuborish |
| 2.3.2 | `POST /api/v1/auth/verify-otp/` | OTP tasdiqlash → JWT token qaytarish |
| 2.3.3 | `POST /api/v1/auth/google/` | Google ID token → tasdiqlash → JWT token |
| 2.3.4 | `POST /api/v1/auth/refresh/` | JWT refresh token |
| 2.3.5 | `GET /api/v1/auth/me/` | Joriy foydalanuvchi profili |

### 2.4. Backend — Google OAuth

| # | Vazifa | Tafsilot |
|---|--------|----------|
| 2.4.1 | Google Cloud Console | OAuth 2.0 Client ID olish |
| 2.4.2 | Token verification | `google-auth` kutubxonasi orqali ID token tekshirish |
| 2.4.3 | Auto-register | Google'dan kelgan email + ism bilan avtomatik ro'yxatdan o'tkazish |

### 2.5. Frontend — Auth UI

| # | Komponent | Tafsilot |
|---|-----------|----------|
| 2.5.1 | `LoginPage.jsx` | Markazlashtirilgan login bloki, mobil moslashgan |
| 2.5.2 | `PhoneLoginForm.jsx` | Telefon raqami kiritish, O'zbekiston formati (+998) |
| 2.5.3 | `OTPVerification.jsx` | 6 xonali OTP input, avtomatik fokus, countdown timer |
| 2.5.4 | `GoogleLoginButton.jsx` | Google Sign-In tugmasi |
| 2.5.5 | Auth store (Zustand) | Token saqlash, login/logout, isAuthenticated |
| 2.5.6 | Axios interceptor | Har bir so'rovga JWT token qo'shish, 401 da logout |
| 2.5.7 | PrivateRoute | Token yo'q bo'lsa login'ga yo'naltirish |

---

## 🔷 BOSQICH 3: Kompaniya Profili va Onboarding
**Muddat:** 1-2 kun

### 3.1. Backend — CompanyProfile

| # | Vazifa | Tafsilot |
|---|--------|----------|
| 3.1.1 | `companies` app yaratish | `python manage.py startapp companies` |
| 3.1.2 | CompanyProfile modeli | TZ.md dagi barcha maydonlar |
| 3.1.3 | Serializer | Create + Update serializer (nested user) |
| 3.1.4 | ViewSet | Profile CRUD (faqat o'z profilini ko'rish/tahrirlash) |
| 3.1.5 | Onboarding endpoint | `POST /api/v1/company/onboarding/` — 3 savol + kompaniya ma'lumotlari |

### 3.2. Frontend — Onboarding UI

| # | Komponent | Tafsilot |
|---|-----------|----------|
| 3.2.1 | `OnboardingPage.jsx` | 3 bosqichli stepper sahifasi |
| 3.2.2 | `OnboardingStepper.jsx` | Silliq animatsiyali qadamlar (framer-motion) |
| 3.2.3 | Qadam 1 | Sohangizni tanlang (ikonkali kartochkalar: Qurilish, IT, Logistika, ...) |
| 3.2.4 | Qadam 2 | Tajribangiz (Yangi boshlovchi / O'rtacha / Professional — radio buttons) |
| 3.2.5 | Qadam 3 | Kompaniya ma'lumotlari formasi (nomi, STIR, turi, QQS holati) |
| 3.2.6 | Yakunlash | Profil saqlanadi → Dashboard'ga yo'naltiriladi |

---

## 🔷 BOSQICH 4: Tender Lotlari va Qidiruv Tizimi
**Muddat:** 3-4 kun

### 4.1. Backend — TenderLot va Scraping

| # | Vazifa | Tafsilot |
|---|--------|----------|
| 4.1.1 | `tenders` app yaratish | `python manage.py startapp tenders` |
| 4.1.2 | TenderLot modeli | TZ.md dagi barcha maydonlar |
| 4.1.3 | TenderDocumentChunk modeli | lot FK, file_name, chunk_index, raw_text |
| 4.1.4 | Scraper service | `services/scraper.py` — requests + BeautifulSoup |
| 4.1.5 | Management command | `python manage.py scrape_tenders` — qo'lda ishga tushirish |
| 4.1.6 | Upsert logikasi | lot_number bo'yicha — yangi bo'lsa qo'shish, eski bo'lsa yangilash |
| 4.1.7 | Demo (Seed) ma'lumotlar | 20-30 ta real formatdagi test lotlar (fixture) |

### 4.2. Backend — Qidiruv va Filtr API

| # | Vazifa | Tafsilot |
|---|--------|----------|
| 4.2.1 | `filters.py` | django-filter orqali TenderLot uchun FilterSet |
| 4.2.2 | LIKE qidiruv | `title__icontains`, `buyer_name__icontains` |
| 4.2.3 | Filtrlar | region, category, platform_source, status, min/max price, deadline |
| 4.2.4 | Saralash (Ordering) | posted_date, deadline, start_price |
| 4.2.5 | Pagination | 20 ta per page |
| 4.2.6 | Manual tender input | `POST /api/v1/tenders/manual/` — foydalanuvchi qo'lda matn kiritishi |

**Filtr misoli:**
```
GET /api/v1/tenders/?search=mebel&region=Toshkent&min_price=10000000&status=active&sort=-deadline
```

### 4.3. Frontend — Dashboard va Qidiruv

| # | Komponent | Tafsilot |
|---|-----------|----------|
| 4.3.1 | `DashboardPage.jsx` | Asosiy sahifa — sidebar + content |
| 4.3.2 | `Sidebar.jsx` | Navigation: Tenderlar, Tahlillarim, Kalkulyator, Jamoa, Profil |
| 4.3.3 | `MobileNav.jsx` | Mobilda pastki tab bar (bottom navigation) |
| 4.3.4 | `SearchBar.jsx` | Debounced qidiruv (300ms kutish) |
| 4.3.5 | `FilterPanel.jsx` | Accordion yoki modal filtr paneli (hudud, narx, platforma...) |
| 4.3.6 | `TenderCard.jsx` | Lot kartochkasi: raqam, nomi, narx, muddat, moslik balli |
| 4.3.7 | `TenderList.jsx` | Infinite scroll yoki pagination bilan lotlar ro'yxati |
| 4.3.8 | Skeleton loading | Ma'lumotlar kelguncha skeleton kartochkalar |
| 4.3.9 | Empty state | "Hech narsa topilmadi" — chiroyli bo'sh holat dizayni |

---

## 🔷 BOSQICH 5: AI Tahlil Tizimi (Core Feature)
**Muddat:** 4-5 kun

### 5.1. Backend — AI Analysis Modellari

| # | Vazifa | Tafsilot |
|---|--------|----------|
| 5.1.1 | `analysis` app yaratish | `python manage.py startapp analysis` |
| 5.1.2 | AITenderAnalysis modeli | TZ.md dagi barcha maydonlar |
| 5.1.3 | SmartCalculator modeli | OneToOne → AITenderAnalysis |

### 5.2. Backend — Gemini API Integratsiya

| # | Vazifa | Tafsilot |
|---|--------|----------|
| 5.2.1 | `gemini_service.py` | Google Generative AI SDK (`google-generativeai`) |
| 5.2.2 | `prompt_templates.py` | System prompt + JSON output schema |
| 5.2.3 | `json_parser.py` | SafeJSONParser — noto'g'ri JSON ni tozalash |
| 5.2.4 | Tahlil pipeline | Matn qabul → chunks → prompt → Gemini → parse → saqlash |
| 5.2.5 | Status tracking | pending → processing_docs → checking_compliance → detecting_red_flags → completed |
| 5.2.6 | Error handling | Timeout (30s), retry (1 marta), failed holati |
| 5.2.7 | Rate limiting | Free: 4/oy, Pro: cheksiz (tarif tekshiruvi) |

**System Prompt tuzilmasi:**
```python
SYSTEM_PROMPT = """
Siz TenderHelper tizimining yetakchi huquqiy va texnik tahlilchisiz.
O'zbekiston Respublikasi "Davlat xaridlari to'g'risida"gi qonuni asosida ishlaysiz.

Vazifalaringiz:
1. Tender matnidan asosiy ma'lumotlarni ajrating (buyurtmachi, predmet, narx, muddat, joy)
2. Murakkab yuridik iboralarni oddiy tilga o'giring
3. O'zDSt, GOST, ISO standartlarini aniqlang va tushuntiring
4. Raqobatni cheklovchi shartlarni "red_flags" ga kiriting
5. Yetishmayotgan hujjatlarni aniqlang
6. Moslik ballini (0-100) va qatnashish tavsiyasini bering

Qoidalar:
- Ton: sodda, do'stona, "Siz qila olasiz" ruhida
- 5 qatordan uzun paragraf yozmaslik
- Yuridik maslahat bermaslik — "Huquqshunos bilan maslahat qiling"
- G'alaba kafolati bermaslik
- Javob faqat JSON formatida

JSON chiqish sxemasi:
{
  "summary": {
    "buyer": "", "subject": "", "budget": "",
    "deadline": "", "location": "", "main_requirement": "",
    "missing_info": []
  },
  "requirements": [
    {"original": "", "plain": "", "action": ""}
  ],
  "standards": [
    {"name": "", "meaning": "", "action": ""}
  ],
  "documents": [
    {"name": "", "reason": "", "category": "common|industry|company_type"}
  ],
  "red_flags": [
    {"level": "blocker|warning|info", "title": "", "reason": "", "recommendation": ""}
  ],
  "decision": {
    "fit_percent": 0, "risk_percent": 0,
    "recommendation": "", "next_actions": []
  }
}
"""
```

### 5.3. Backend — Analysis API Endpoints

| # | Endpoint | Vazifa |
|---|----------|--------|
| 5.3.1 | `POST /api/v1/analysis/start/` | lot_id + qo'shimcha matn → AI tahlil boshlash |
| 5.3.2 | `GET /api/v1/analysis/<uuid>/status/` | Joriy status (polling uchun) |
| 5.3.3 | `GET /api/v1/analysis/<uuid>/result/` | To'liq tahlil natijasi |
| 5.3.4 | `GET /api/v1/analysis/history/` | Foydalanuvchining barcha tahlillari |

### 5.4. Backend — SmartCalculator API

| # | Endpoint | Vazifa |
|---|----------|--------|
| 5.4.1 | `POST /api/v1/analysis/<uuid>/calculate/` | Xarajatlar → QQS + operator haqi + Stop-Loss + tavsiya narx |

**Hisoblash logikasi:**
```python
def calculate(data):
    tannarx = data['raw_material'] + data['logistics'] + data['labor'] + data['other']
    qqs = tannarx * Decimal('0.12')           # 12% QQS
    operator = tannarx * Decimal('0.0015')     # 0.15% UzEx
    zakalat = data['start_price'] * Decimal('0.03')  # 3% zakalat
    
    min_safe = tannarx + qqs + operator        # Stop-Loss
    recommended = min_safe * Decimal('1.15')    # 15% foyda marjasi
    net_profit = data['start_price'] - recommended - zakalat
    
    return {
        'tannarx': tannarx,
        'qqs': qqs,
        'operator_fee': operator,
        'zakalat': zakalat,
        'min_safe_price': min_safe,         # 🔴 Stop-Loss
        'recommended_price': recommended,    # ⭐ Tavsiya
        'net_profit': net_profit,
    }
```

### 5.5. Frontend — AI Tahlil UI

| # | Komponent | Tafsilot |
|---|-----------|----------|
| 5.5.1 | `AnalysisPage.jsx` | Tahlil sahifasi — input + natijalar |
| 5.5.2 | `TextInputArea.jsx` | Katta textarea — tender matnini paste qilish |
| 5.5.3 | `FileUpload.jsx` | Drag-and-drop hujjat yuklash (V2 uchun placeholder) |
| 5.5.4 | `AnalysisProgress.jsx` | 4 bosqichli shaffof progress bar (animatsiyali) |
| 5.5.5 | `SummaryCard.jsx` | Buyurtmachi, predmet, narx, muddat — toza karta |
| 5.5.6 | `RequirementsList.jsx` | Asl ibora → oddiy ma'no → nima qilish kerak |
| 5.5.7 | `RedFlagsList.jsx` | 🔴🟡🟢 darajali risk kartalari |
| 5.5.8 | `DocumentChecklist.jsx` | Interaktiv checklist — bor/yo'q/bilmayman |
| 5.5.9 | `DecisionCard.jsx` | Moslik %, risk %, tavsiya — vizual progress bar'lar |
| 5.5.10 | `SmartCalculator.jsx` | Xarajat inputlar → avtomat hisob → Stop-Loss chizig'i |

**AnalysisProgress vizual rejasi:**
```
┌──────────────────────────────────────────────┐
│  AI Tahlil Jarayoni                           │
│                                               │
│  ✅ Hujjatlar qabul qilindi         [████]   │
│  🔄 Yuridik terminlar tahlil qilinmoqda...   │
│  ⏳ Red Flag tekshiruvi             [░░░░]   │
│  ⏳ Yakuniy xulosa tayyorlanmoqda   [░░░░]   │
│                                               │
│  ████████████░░░░░░░░  45%                   │
└──────────────────────────────────────────────┘
```

---

## 🔷 BOSQICH 6: Tarif va To'lov Tizimi
**Muddat:** 2-3 kun

### 6.1. Backend — Subscription Modeli

| # | Vazifa | Tafsilot |
|---|--------|----------|
| 6.1.1 | `subscriptions` app yaratish | |
| 6.1.2 | `SubscriptionPlan` modeli | name, price_usd, price_uzs, analysis_limit, features (JSON) |
| 6.1.3 | `UserSubscription` modeli | user FK, plan FK, start_date, end_date, is_active |
| 6.1.4 | `PaymentTransaction` modeli | user FK, amount, provider (payme/click/uzum), status, transaction_id |
| 6.1.5 | Tarif tekshiruv middleware | Har bir AI tahlil so'rovida limit tekshiruvi |

### 6.2. Backend — To'lov API

| # | Endpoint | Vazifa |
|---|----------|--------|
| 6.2.1 | `GET /api/v1/subscription/plans/` | 3 tarif ro'yxati (Free/Pro/Enterprise) |
| 6.2.2 | `GET /api/v1/subscription/status/` | Joriy obuna holati + qolgan tahlillar soni |
| 6.2.3 | `POST /api/v1/subscription/checkout/` | To'lov boshlash (provider tanlash) |
| 6.2.4 | `POST /api/v1/subscription/webhook/payme/` | Payme callback |
| 6.2.5 | `POST /api/v1/subscription/webhook/click/` | Click callback |
| 6.2.6 | `POST /api/v1/subscription/webhook/uzum/` | Uzum callback |

> **MVP qaror:** Webhook endpointlar tayyor bo'ladi, lekin merchant shartnomalar keyinroq ulanadi. MVP davrida Pro/Enterprise bepul test sifatida berilishi mumkin.

### 6.3. Frontend — Tarif UI

| # | Komponent | Tafsilot |
|---|-----------|----------|
| 6.3.1 | `PricingPage.jsx` | 3 ta tarif kartasi — Free / Pro / Enterprise |
| 6.3.2 | `PricingTable.jsx` | Xususiyatlarni solishtirish jadvali |
| 6.3.3 | `PaymentModal.jsx` | To'lov tizimini tanlash (Payme/Click/Uzum) |
| 6.3.4 | Limit ko'rsatkichi | Dashboard'da "Qolgan tahlillar: 2/4" badge |

---

## 🔷 BOSQICH 7: Enterprise Funksiyalar
**Muddat:** 2-3 kun

### 7.1. Backend — Team Collaboration

| # | Vazifa | Tafsilot |
|---|--------|----------|
| 7.1.1 | `teams` app yaratish | |
| 7.1.2 | TeamCollaborationTask modeli | TZ.md dagi barcha maydonlar |
| 7.1.3 | CRUD API | Vazifa yaratish, tayinlash, status yangilash |
| 7.1.4 | Permission tekshiruv | Faqat enterprise tarif uchun |

### 7.2. Backend — Competitor Intelligence

| # | Vazifa | Tafsilot |
|---|--------|----------|
| 7.2.1 | `competitors` app yaratish | |
| 7.2.2 | CompetitorDossier modeli | TZ.md dagi barcha maydonlar |
| 7.2.3 | Ma'lumot to'plash | Portal scraping orqali g'oliblar ro'yxatidan |
| 7.2.4 | API endpoints | Ro'yxat va tafsilot ko'rish |

### 7.3. Frontend — Enterprise UI

| # | Komponent | Tafsilot |
|---|-----------|----------|
| 7.3.1 | `TeamPage.jsx` | Kanban doskasi — todo / in_progress / done |
| 7.3.2 | `TaskBoard.jsx` | Drag-and-drop vazifalar (yoki oddiy list) |
| 7.3.3 | `CompetitorCard.jsx` | Raqobatchi kartochkasi — yutishlar, narx tushirish % |
| 7.3.4 | Enterprise gate | Enterprise bo'lmasa "🔒 Upgrade" ko'rsatish |

---

## 🔷 BOSQICH 8: Polish, PWA va Deploy
**Muddat:** 2-3 kun

### 8.1. UI/UX Polish

| # | Vazifa | Tafsilot |
|---|--------|----------|
| 8.1.1 | Dark mode | Tailwind `dark:` classlari, toggle tugma, localStorage saqlash |
| 8.1.2 | Responsive tekshiruv | Mobile (375px), Tablet (768px), Desktop (1280px) |
| 8.1.3 | Loading holatlari | Barcha sahifalarda Skeleton loaders |
| 8.1.4 | Error holatlari | Toast xabarlar, 404 sahifa, network error UI |
| 8.1.5 | Empty states | "Hali tahlil qilmadingiz" — chiroyli bo'sh holatlar |
| 8.1.6 | Animatsiyalar | Sahifa o'tishlari, kartochka hover, progress bar |
| 8.1.7 | Accessibility | Keyboard navigation, focus rings, contrast |
| 8.1.8 | Disclaimer | Har bir tahlil natijasida yuridik ogohlantirish |

### 8.2. PWA Sozlash

| # | Vazifa | Tafsilot |
|---|--------|----------|
| 8.2.1 | manifest.json | App nomi, ranglar, ikonkalar (192px, 512px) |
| 8.2.2 | Service Worker | Statik resurslarni keshlash |
| 8.2.3 | Offline Lite | Oxirgi tahlillar va kalkulyator natijalarini localStorage'dan ko'rsatish |
| 8.2.4 | Install prompt | "Ilovani o'rnating" banner |

### 8.3. Testing

| # | Vazifa | Tafsilot |
|---|--------|----------|
| 8.3.1 | Backend unit testlar | Model validatsiya, API status kodlari |
| 8.3.2 | API integration testlar | Auth flow, analysis flow, calculator |
| 8.3.3 | Frontend manual test | Barcha ekranlar, barcha holatlar |
| 8.3.4 | Cross-browser | Chrome, Edge, Safari (mobile) |
| 8.3.5 | Performance | Lighthouse audit: 90+ ball |

### 8.4. Deployment

| # | Vazifa | Tafsilot |
|---|--------|----------|
| 8.4.1 | Backend deploy | Railway / Render / VPS (PostgreSQL production) |
| 8.4.2 | Frontend deploy | Vercel / Netlify |
| 8.4.3 | Environment | Production .env sozlash |
| 8.4.4 | Domain | Custom domain ulash |
| 8.4.5 | SSL | HTTPS majburiy |

---

## 📊 Umumiy Muddat va Resurslar

| Bosqich | Nomi | Muddat |
|---------|------|--------|
| 1 | Loyiha Infratuzilmasi | 1-2 kun |
| 2 | Auth Tizimi | 2-3 kun |
| 3 | Profil va Onboarding | 1-2 kun |
| 4 | Tenderlar va Qidiruv | 3-4 kun |
| 5 | AI Tahlil (Core) | 4-5 kun |
| 6 | Tarif va To'lov | 2-3 kun |
| 7 | Enterprise Funksiyalar | 2-3 kun |
| 8 | Polish, PWA, Deploy | 2-3 kun |
| **JAMI** | | **17-25 kun (3-4 hafta)** |

---

## ⚡ Ishga Tushirish Tartibi

Kod yozishni boshlash uchun ketma-ketlik:

```
BOSQICH 1 → tasdiqlanganidan keyin → BOSQICH 2 → ... → BOSQICH 8
     │                                    │
     └── Backend + Frontend parallel ─────┘
```

> [!IMPORTANT]
> **Ishni boshlash uchun sizdan kerak:**
> 1. Ushbu rejani tasdiqlash ✅
> 2. Python 3.11+ o'rnatilganligini tasdiqlash
> 3. Node.js 18+ o'rnatilganligini tasdiqlash
> 4. Google Gemini API key (bepul) — [aistudio.google.com](https://aistudio.google.com) dan olish mumkin
> 5. PostgreSQL o'rnatish (yoki MVP uchun SQLite bilan boshlash)

> [!TIP]
> **Tavsiyam:** MVP'ni SQLite bilan boshlash va deploy vaqtida PostgreSQL'ga ko'chish. Bu 1-2 kun vaqt tejaydi va local development'ni osonlashtiradi.
