# 🏗️ TENDERHELPER — TO'LIQ TEXNIK TOPSHIRIQ (TZ)

**Versiya:** 3.0 | **Sana:** 2026-05-22  
**Status:** MVP Development Ready

---

## 📌 1-QISM: LOYIHA KONSEPSIYASI VA TEXNOLOGIK EKOSISTEMA

### 1.1. LOYIHA HAQIDA UMUMIY MA'LUMOT

**Loyiha nomi:** TenderHelper AI  
**Falsafa:** *"Biz tender platformasi emasmiz, biz tender yutishga yordam beruvchi shaxsiy mentormiz"*

**Muammo:**  
O'zbekistonda davlat va korporativ tenderlar hajmi yiliga trillionlab so'mni tashkil etsa-da, kichik tadbirkorlarning aksariyati quyidagi sabablarga ko'ra bu bozordan quruq qolmoqda:

1. **Yuridik til tushunarsiz** — tender hujjatlari murakkab rasmiy tilda yozilgan, oddiy tadbirkor tushunmaydi
2. **Hujjatlar noaniq** — noto'liq ariza topshirib diskvalifikatsiya bo'ladi
3. **Narx strategiyasi yo'q** — ya foydadan mahrum bo'ladi, ya juda qimmat taklif berib yutqazadi
4. **Yashirin shartlar** — jarimalar, qattiq muddatlar shartnomadan keyin moliyaviy zarar keltiradi
5. **Raqobatchilar haqida ma'lumot yo'q** — ko'r-ko'rona raqobatga kirishadi

**Yechim:**  
AI-asosidagi mentor tizim — tender matnini tahlil qiladi, oddiy tilga o'giradi, kerakli hujjatlar ro'yxatini tuzadi, xavflarni ko'rsatadi, raqobatbardosh narx strategiyasini beradi va tijorat taklifini generatsiya qiladi.

**Maqsadli auditoriya:**

| Persona | Profil | Og'riq nuqtasi |
|---------|--------|----------------|
| 👤 Anvar, 34 | MChJ rahbari (mebel ishlab chiqarish) | Birinchi marta tender — qayerdan boshlashni bilmaydi |
| 👤 Dilnoza, 28 | YaTT (oziq-ovqat yetkazib berish) | Hujjat noto'liq bo'lgani uchun rad etilgan |
| 👤 Sherzod, 42 | Qurilish MChJ | Narx strategiyasida xato qiladi, demping tufayli zarar ko'radi |

**Til:** O'zbek tili (Lotin yozuvi). Sodda, rag'batlantiruvchi, "Siz qila olasiz" ruhida.

---

### 1.2. TEXNOLOGIK STEK (TECH STACK)

```
┌──────────────────────────────────────────────────────────────────────┐
│                      TENDERHELPER CORE STACK                         │
├──────────────────────────────────────────────────────────────────────┤
│  FRONTEND:    React.js + Vite + Redux Toolkit                        │
│  MOBILE:      PWA (Progressive Web App) Mobile-First                 │
│  BACKEND:     Python 3.11+ / Django 5.0+ / Django REST Framework     │
│  DATABASE:    PostgreSQL (LIKE / __icontains qidiruv)                │
│  AI ENGINE:   Google Gemini API (Free Tier) — MVP                    │
│               LangChain + RAG — V2+                                  │
│  ASYNC:       Django Background Tasks — MVP                          │
│               Celery + Redis — V2+                                   │
│  AUTH:        Phone + OTP + Google OAuth — MVP                       │
│               + OneID — V2+                                          │
│  PAYMENTS:    Payme / Click / Uzum — MVP (merchant keyinroq)         │
└──────────────────────────────────────────────────────────────────────┘
```

**Nima uchun bu texnologiyalar:**

| Texnologiya | Sabab |
|-------------|-------|
| **Django + DRF** | Python AI kutubxonalari bilan to'g'ridan-to'g'ri integratsiya, kuchli ORM, xavfsizlik |
| **React + Vite** | Tezkor SPA, real-time UI yangilanish, PWA qo'llab-quvvatlash |
| **PostgreSQL** | MVP'da `__icontains` (LIKE) qidiruv yetarli, keyinroq full-text search |
| **Gemini Free API** | MVP uchun bepul, o'zbek tilini qo'llab-quvvatlaydi, JSON output |
| **PWA** | App Store/Play Market'siz telefonga o'rnatiladi |

---

### 1.3. FOYDALANUVCHI ROLLARI

| Rol | Interfeys | Imkoniyatlar |
|-----|-----------|-------------|
| **YaTT / Kichik biznes** | Mentor interfeysi — sodda, yo'naltiruvchi | Tahlil, checklist, kalkulyator |
| **MChJ / Yirik kompaniya** | Team mode — jamoaviy panel | + Raqobatchi razvedkasi, vazifalar doskasi |
| **Admin** | Boshqaruv paneli | Scraping monitoring, tariflar, AI yuklamasi |

---

## 📌 2-QISM: MA'LUMOTLAR BAZASI ARXITEKTURASI

### 2.1. FOYDALANUVCHILAR VA KOMPANIYALAR BLOKI

#### Model 1: `CustomUser` — Tizim foydalanuvchilari

Django `AbstractUser` dan kengaytiriladi.

| Maydon | Tur | Izoh |
|--------|-----|------|
| `id` | UUIDField (PK) | Xavfsizlik uchun UUID |
| `phone_number` | CharField(15, unique) | Asosiy login identifikatori |
| `email` | EmailField(unique, null, blank) | Google OAuth uchun |
| `full_name` | CharField(255) | To'liq ism |
| `role` | CharField (choices: admin, user, manager, viewer) | Huquq doirasi |
| `auth_provider` | CharField (choices: phone, google) | Ro'yxatdan o'tish usuli |
| `is_active` | BooleanField(default=True) | |
| `date_joined` | DateTimeField(auto_now_add) | |

**MVP Auth strategiya:**
- **Telefon + OTP** — asosiy (SMS provider: Eskiz yoki PlayMobile)
- **Google OAuth** — qo'shimcha (django-allauth orqali)
- **OneID** — V2 da qo'shiladi (davlat shartnomasi kerak)

---

#### Model 2: `CompanyProfile` — Korxona Raqamli Dosyasi

| Maydon | Tur | Izoh |
|--------|-----|------|
| `id` | UUIDField (PK) | |
| `user` | ForeignKey(CustomUser) | Profil egasi |
| `stir` | CharField(9, unique) | Korxona STIR (INN) |
| `company_name` | CharField(500) | Rasmiy to'liq nomi |
| `company_type` | CharField (choices: yatt, mchj, aj, tt) | Huquqiy shakli |
| `industry` | CharField(255) | Asosiy soha |
| `experience_level` | CharField (choices: beginner, intermediate, expert) | Tender tajribasi |
| `registration_date` | DateField(null, blank) | Davlat ro'yxatidan o'tgan sana |
| `ustav_fondi` | DecimalField(18, 2, default=0) | Milliy valyutada (UZS) |
| `has_vat` | BooleanField(default=False) | QQS (12%) to'lovchimi |
| `current_tariff` | CharField (choices: free, pro, enterprise, default=free) | |
| `tariff_expires_at` | DateTimeField(null, blank) | Obuna tugash vaqti |
| `raw_tax_data` | JSONField(default=dict) | Soliq API dan kelgan qo'shimcha ma'lumotlar |

**MVP yondashuvlari:**
- `raw_tax_data` — MVP'da foydalanuvchi qo'lda to'ldiradi. Soliq API ulanganda avtomatlashtiriladi
- `stir` — MVP'da majburiy emas, ixtiyoriy kiritiladi

---

### 2.2. TENDER LOTLARI VA AGREGATOR BLOKI

#### Model 3: `TenderLot` — Yagona Tenderlar Ombori

4 ta milliy portaldan olinadigan barcha lotlar.

| Maydon | Tur | Izoh |
|--------|-----|------|
| `id` | UUIDField (PK) | |
| `lot_number` | CharField(100, unique) | Rasmiy lot raqami |
| `platform_source` | CharField (choices: xarid_uzex, dxarid_uzex, exarid_uzex, e_auksion, manual) | Manba |
| `title` | TextField | Tender e'loni nomi (LIKE qidiruv) |
| `buyer_name` | CharField(500) | Buyurtmachi (LIKE qidiruv) |
| `start_price` | DecimalField(18, 2) | Boshlang'ich narx (UZS) |
| `zakalat_amount` | DecimalField(18, 2, default=0) | Zakalat puli |
| `region` | CharField(100) | Hudud (viloyat/shahar) |
| `category` | CharField(255) | Soha klassifikatsiyasi |
| `posted_date` | DateTimeField | E'lon sanasi |
| `deadline` | DateTimeField | Ariza topshirish muddati |
| `status` | CharField(50, default=active) | active / completed / cancelled |
| `raw_portal_url` | URLField | Rasmiy manbaga havola |

**MVP ma'lumot manbasi strategiyasi:**
1. **Birinchi harakat:** Portallardan rasmiy API olish
2. **Fallback:** API bo'lmasa — HTML scraping (BeautifulSoup / Scrapy)
3. **Qo'shimcha:** Foydalanuvchi tender matnini qo'lda paste qilishi ham mumkin (`platform_source = manual`)

**Qidiruv logikasi (Django ORM):**
```python
queryset = TenderLot.objects.filter(status='active')
if search_query:
    queryset = queryset.filter(
        Q(title__icontains=search_query) | 
        Q(buyer_name__icontains=search_query)
    )
```

---

#### Model 4: `TenderDocumentChunk` — Hujjat bo'laklari

| Maydon | Tur | Izoh |
|--------|-----|------|
| `id` | UUIDField (PK) | |
| `tender_lot` | ForeignKey(TenderLot, CASCADE, related_name='chunks') | |
| `file_name` | CharField(255) | Asl fayl nomi |
| `chunk_index` | IntegerField | Matn tartib raqami |
| `raw_text` | TextField | Toza matn parchasi |

> **MVP qaror:** `embedding: VectorField` olib tashlandi. MVP'da faqat `raw_text` ustida matnli qidiruv ishlaydi. Pgvector + semantic search V2 da qo'shiladi.

---

### 2.3. AI TAHLIL VA RISK BLOKI

#### Model 5: `AITenderAnalysis` — Shaffof Tahlil Natijalari

| Maydon | Tur | Izoh |
|--------|-----|------|
| `id` | UUIDField (PK) | |
| `company` | ForeignKey(CompanyProfile, CASCADE) | |
| `tender_lot` | ForeignKey(TenderLot, CASCADE) | |
| `analysis_status` | CharField (choices: pending, processing_docs, checking_compliance, detecting_red_flags, completed, failed) | Progress tracking |
| `eligibility_score` | IntegerField(default=0) | Moslik balli (0-100%) |
| `summary_text` | TextField(null) | Oddiy tildagi xulosa |
| `missing_documents` | JSONField(default=list) | Yetishmayotgan hujjatlar |
| `red_flags` | JSONField(default=list) | Aniqlangan risklar ro'yxati |
| `requirements` | JSONField(default=list) | Texnik talablar tahlili |
| `standards` | JSONField(default=list) | O'zDSt, GOST, ISO talablari |
| `decision` | JSONField(default=dict) | Qatnashish tavsiyasi |
| `created_at` | DateTimeField(auto_now_add) | |

**Red Flag signallar (AI avtomatik aniqlaydi):**
- ⚠️ Faqat bitta ishlab chiqaruvchi → raqobat cheklangan
- ⚠️ Muddati < 10 kun → tayyorlanish qiyin
- ⚠️ Jarima shartlari > 10% → moliyaviy risk yuqori
- ⚠️ Texnik spesifikatsiya juda tor → muayyan brendga yo'naltirilgan
- ⚠️ Litsenziya ro'yxati uzun → hujjat yig'ish qimmat va uzoq

---

### 2.4. MOLIYAVIY STRATEGIYA BLOKI

#### Model 6: `SmartCalculator` — Anti-Demping va Stop-Loss

| Maydon | Tur | Izoh |
|--------|-----|------|
| `id` | UUIDField (PK) | |
| `analysis` | OneToOneField(AITenderAnalysis, CASCADE, related_name='calculator') | |
| `raw_material_cost` | DecimalField(18, 2, default=0) | Xomashyo tannarxi |
| `logistics_cost` | DecimalField(18, 2, default=0) | Transport xarajati |
| `labor_cost` | DecimalField(18, 2, default=0) | Ish haqi |
| `other_expenses` | DecimalField(18, 2, default=0) | Qo'shimcha xarajatlar |
| `calculated_vat` | DecimalField(18, 2, default=0) | Avtomat 12% QQS |
| `calculated_operator_fee` | DecimalField(18, 2, default=0) | Avtomat 0.15% UzEx haqi |
| `min_safe_price` | DecimalField(18, 2, default=0) | Stop-Loss narxi |
| `recommended_price` | DecimalField(18, 2, default=0) | AI tavsiya optimal narx |

**Hisoblash formulasi:**
```
tannarx = xomashyo + logistika + ish_haqi + boshqa
qqs = tannarx × 0.12
operator_haqi = tannarx × 0.0015
min_safe_price = tannarx + qqs + operator_haqi + zakalat
recommended_price = min_safe_price × 1.15  (15% foyda marjasi)
```

---

### 2.5. JAMOAVIY ISHLASH BLOKI (Enterprise)

#### Model 7: `TeamCollaborationTask` — Virtual Xona

| Maydon | Tur | Izoh |
|--------|-----|------|
| `id` | UUIDField (PK) | |
| `tender_lot` | ForeignKey(TenderLot, CASCADE) | |
| `company` | ForeignKey(CompanyProfile, CASCADE) | |
| `assigned_to` | ForeignKey(CustomUser, SET_NULL, null, related_name='tasks') | Mas'ul xodim |
| `task_title` | CharField(255) | Vazifa nomi |
| `status` | CharField (choices: todo, in_progress, done, default=todo) | |
| `due_date` | DateTimeField | Muddat |
| `updated_at` | DateTimeField(auto_now) | |

> **MVP qaror:** Enterprise tarifda mavjud. Free va Pro da yopiq.

---

### 2.6. RAQOBATCHILAR RAZVEDKASI BLOKI (Enterprise)

#### Model 8: `CompetitorDossier` — B2B Razvedka

| Maydon | Tur | Izoh |
|--------|-----|------|
| `id` | UUIDField (PK) | |
| `competitor_name` | CharField(500) | Raqobatchi kompaniya nomi |
| `competitor_stir` | CharField(9, null, blank) | STIR raqami |
| `dominant_category` | CharField(255) | Ko'p yutadigan sohasi |
| `total_wins` | IntegerField(default=0) | G'olib bo'lgan tenderlar soni |
| `avg_price_drop_percentage` | DecimalField(5, 2, default=0) | O'rtacha narx tushirish % |

**Ma'lumot manbasi:** Real-time tender platformalardan — API mavjud bo'lsa API orqali, bo'lmasa scraping orqali.

> **MVP qaror:** Enterprise tarifda mavjud. Ma'lumotlar portallardan real-time olinadi.

---

## 📌 3-QISM: UI/UX INTERFEYS LAYOUTLARI VA FOYDALANUVCHI OQIMI

### 3.1. DIZAYN FALSAFASI

- **Uslub:** Minimalist, professional FinTech interfeysi — cartoon/multfilm elementlar **mutlaq yo'q**
- **Ranglar:** Professional ko'k (#1E3A5F) + ishonch yashil (#10B981) + ogohlantirish sariq (#F59E0B)
- **Tipografiya:** Inter yoki Roboto (Google Fonts)
- **Yondashuv:** Mobile-first responsive
- **Qo'shimcha:** Dark mode, skeleton loading, silliq animatsiyalar

---

### 3.2. FOYDALANUVCHI OQIMI (USER JOURNEY)

```
[ Telefon+OTP / Google Login ]
            │
            ▼
[ 3 ta Savolli Onboarding ] ──► Profil va kompaniya ma'lumotlarini kiritish
            │
            ▼
[ Smart Dashboard ] ──► Mos lotlarni LIKE qidiruv orqali topish
            │
            ▼
[ AI Skaner ] ──► Lot hujjatlarini tahlil, progress bar ko'rinishida
            │
            ▼
[ Xulosa + Kalkulyator ] ──► Red Flags, Stop-Loss, QQS hisob
            │
            ▼
[ Tijorat Taklifi ] ──► PDF/Word formatda yuklab olish (V2)
```

---

### 3.3. EKRANLAR STRUKTURASI

#### EKRAN 1: Login va Onboarding

**Layout:**
- Markazda toza login bloki
- 2 ta login usuli: **Telefon + OTP** va **Google bilan kirish**
- Birinchi kirishda 3 ta savolli modal:
  1. Sohangizni tanlang (Qurilish, IT, Logistika, Tibbiyot, Ta'minot)
  2. Tenderlardagi tajribangiz (Yangi boshlovchi / O'rtacha / Professional)
  3. Maqsadingiz (Hujjat tayyorlash / Narx hisoblash / Raqobatchilarni kuzatish)
- Kompaniya ma'lumotlarini kiritish formasi: STIR, nomi, turi, soha

---

#### EKRAN 2: Smart Dashboard

```
┌──────────────────────────────────────────────────────────┐
│  🏛️ TenderHelper AI — Sizning tender mentoringiz        │
│  ─────────────────────────────────────────────────────── │
│  [📊 Tenderlar] [📋 Tahlillarim] [💰 Kalkulyator] [👥 Jamoa] │
│  ═══════════════════════════════════════════════════════ │
│                                                          │
│  🔍 [══════ Qidiruv paneli ══════] [⚙️ Filtrlar]        │
│                                                          │
│  ┌──────────────────────────────────────┐                │
│  │ 📦 Lot #12345                        │                │
│  │ Mebel yetkazib berish — Toshkent     │                │
│  │ 💰 150,000,000 UZS  ⏰ 5 kun qoldi  │                │
│  │ Moslik: ████████░░ 85%               │                │
│  │ [🔍 Tahlil qilish]                  │                │
│  └──────────────────────────────────────┘                │
│                                                          │
│  ┌──────────────────────────────────────┐                │
│  │ 📦 Lot #12346 ...                   │                │
│  └──────────────────────────────────────┘                │
└──────────────────────────────────────────────────────────┘
```

**Elementlar:**
- Yuqorida: Aqlli qidiruv paneli (LIKE qidiruv)
- O'ngda: 25+ filtr (hudud, narx, platforma, soha, muddat)
- Markazda: Lot kartochkalari — raqam, narx, deadline, moslik balli
- Mobilda: Pastki tab navigatsiya

---

#### EKRAN 3: AI Skaner — Shaffof Tahlil Paneli

Foydalanuvchi lotni tanlaganda ochiladi. **Ikki ustunli layout** (mobilda ketma-ket):

**Chap ustun — Foydalanuvchi hujjatlari:**
- Drag-and-drop hujjat yuklash maydoni
- Yoki tender matnini paste qilish textarea

**O'ng ustun — AI Progress:**
- 🟢 "Lot hujjatlari yuklab olindi" ✓
- 🟡 "O'zDSt va GOST standartlari tahlil qilinmoqda..." ⟳
- ⚪ "Hujjatlaringiz tender talablariga solishtirilmoqda..." (kutish)
- ⚪ "Red Flag tekshiruvi..." (kutish)

---

#### EKRAN 4: Yakuniy Xulosa va Kalkulyator

**Tab 1 — AI Xulosasi:**
```
┌─────────────────────────────────────────┐
│  TENDER QISQACHA:                       │
│  Buyurtmachi: [tashkilot nomi]          │
│  Nima kerak: [oddiy til]                │
│  Narx: [boshlang'ich narx] so'm         │
│  Muddati: [sana]                        │
│  Joyi: [viloyat/shahar]                 │
│  Asosiy talab: [eng muhim shart]        │
└─────────────────────────────────────────┘

⚠️ RED FLAGS:
🔴 BLOKLAYDI: [sabab] → [yechim]
🟡 MUAMMO: [ehtimol] → [tavsiya]
🟢 E'TIBOR: [kichik risk]

📋 YETISHMAYOTGAN HUJJATLAR:
 ☐ [hujjat 1] — qayerdan olish
 ☐ [hujjat 2] — qayerdan olish

UMUMIY BAHOLASH:
 Mos kelish: ████████░░ 80%
 Risk:       ███░░░░░░░ 30%
 TAVSIYA: 🟢 Qatnashing!
```

**Tab 2 — Smart Kalkulyator:**
```
┌──────────────────────────────────────────┐
│  💰 NARX KALKULYATORI                    │
│                                          │
│  Xomashyo:     [___________] so'm        │
│  Transport:    [___________] so'm        │
│  Ish haqi:     [___________] so'm        │
│  Boshqa:       [___________] so'm        │
│  ──────────────────────────────────────  │
│  Tannarx:          45,000,000 so'm       │
│  + QQS (12%):       5,400,000 so'm       │
│  + UzEx (0.15%):       67,500 so'm       │
│  ──────────────────────────────────────  │
│  🔴 STOP-LOSS:     50,467,500 so'm       │
│  ⭐ TAVSIYA NARX:  58,037,625 so'm       │
│  Boshlang'ich:     70,000,000 so'm       │
│  Sizning foydangiz: 11,962,375 so'm      │
└──────────────────────────────────────────┘
```

---

#### EKRAN 5: Jamoaviy Virtual Xona (Enterprise)

**Layout:** Kanban doskasi uslubida

```
┌─────────────┬─────────────┬─────────────┐
│  📋 TODO    │ 🔄 JARAYONDA │ ✅ TAYYOR   │
├─────────────┼─────────────┼─────────────┤
│ Balans olish│ Sertifikat  │ STIR nusxa  │
│ @Anvar      │ tayyorlash  │ @Dilnoza    │
│ 3 kun qoldi │ @Sherzod    │ ✓ Bajarildi │
└─────────────┴─────────────┴─────────────┘

📊 RAQOBATCHI DOSYASI:
┌──────────────────────────────────┐
│ 🏢 AlphaStroy MChJ              │
│ Yutgan tenderlar: 47 ta         │
│ O'rtacha narx tushirishi: 18%   │
│ Asosiy soha: Qurilish           │
└──────────────────────────────────┘
```

---

### 3.4. PWA XUSUSIYATLARI

| Xususiyat | Tavsif |
|-----------|--------|
| **Service Workers** | CSS, shriftlar, interfeys keshlanadi — sekin internetda ham ishlaydi |
| **Push Notifications** | Deadline'ga 3 kun / 1 kun / 12 soat qolganda eslatma |
| **Offline Lite** | Internetsis — oxirgi ko'rilgan tahlillar va kalkulyator natijalari ko'rinadi |
| **Install Prompt** | Telefonga App Store'siz o'rnatish |

---

## 📌 4-QISM: BACKEND API VA ASINXRON JARAYONLAR

### 4.1. MA'LUMOTLAR AGREGATSIYASI (DATA PIPELINE)

#### Lot Skreperi

**Manbalar:**
1. `xarid.uzex.uz` — davlat xaridlari
2. `dxarid.uzex.uz` — davlat xaridlari (alternativ)
3. `exarid.uzex.uz` — elektron xaridlar
4. `e-auksion.uz` — auksionlar

**Strategiya:**
- **Birinchi:** Rasmiy API olishga harakat qilinadi
- **Fallback:** API bo'lmasa — HTML scraping (BeautifulSoup + requests)
- **Davriylik:** Har 30 daqiqada (MVP'da Django management command + cron, V2'da Celery Beat)
- **Mantiq:** Faqat yangi lotlar qo'shiladi. Mavjud lotlarning muddati va narxi yangilanadi (upsert)

#### Hujjat Yuklash

1. Foydalanuvchi lotni tanlab "Tahlil qilish" tugmasini bosadi
2. Backend lot hujjatlarini (.pdf, .docx) yuklab oladi
3. Matnni bo'laklarga ajratadi (chunk_size=1000, overlap=200)
4. `TenderDocumentChunk` jadvaliga saqlaydi
5. AI tahlilni boshlaydi

**MVP yondashuv:** Sinxron jarayon (timeout 60 sek). V2'da Celery Worker'ga ko'chiriladi.

---

### 4.2. API ENDPOINTS

#### 🔐 Auth & Profile

| Method | Endpoint | Vazifa |
|--------|----------|--------|
| POST | `/api/v1/auth/send-otp/` | Telefon raqamiga OTP yuborish |
| POST | `/api/v1/auth/verify-otp/` | OTP tasdiqlash → Token olish |
| POST | `/api/v1/auth/google/` | Google OAuth token → Tizim token |
| GET | `/api/v1/auth/me/` | Joriy foydalanuvchi ma'lumotlari |
| POST | `/api/v1/company/onboarding/` | 3 ta onboarding savoli + kompaniya ma'lumotlari |
| GET | `/api/v1/company/profile/` | Raqamli dosye |
| PATCH | `/api/v1/company/profile/` | Profil yangilash |

#### 🧭 Tenders & Search

| Method | Endpoint | Vazifa |
|--------|----------|--------|
| GET | `/api/v1/tenders/` | Lotlar ro'yxati (LIKE qidiruv + 25 filtr) |
| GET | `/api/v1/tenders/<uuid>/` | Bitta lot tafsiloti |
| POST | `/api/v1/tenders/manual/` | Qo'lda tender matni kiritish |

**Filtr parametrlari:**
```
?search=mebel
&region=Toshkent
&min_price=10000000
&max_price=500000000
&source=xarid_uzex
&category=qurilish
&status=active
&deadline_before=2026-06-01
&sort=-posted_date
```

#### 🤖 AI Analysis

| Method | Endpoint | Vazifa |
|--------|----------|--------|
| POST | `/api/v1/analysis/start/` | AI tahlilni boshlash (lot_id + foydalanuvchi hujjatlari) |
| GET | `/api/v1/analysis/<uuid>/status/` | Progress polling |
| GET | `/api/v1/analysis/<uuid>/result/` | To'liq tahlil natijasi |
| POST | `/api/v1/analysis/<uuid>/calculate/` | Kalkulyator (xarajatlar → narx) |

#### 💰 Subscription & Payments

| Method | Endpoint | Vazifa |
|--------|----------|--------|
| GET | `/api/v1/subscription/plans/` | Tarif rejalari ro'yxati |
| POST | `/api/v1/subscription/checkout/` | To'lov boshlash |
| POST | `/api/v1/subscription/webhook/` | To'lov tizimi callback |
| GET | `/api/v1/subscription/status/` | Joriy obuna holati |

#### 👥 Team & Competitors (Enterprise)

| Method | Endpoint | Vazifa |
|--------|----------|--------|
| GET/POST | `/api/v1/team/tasks/` | Vazifalar ro'yxati / yaratish |
| PATCH | `/api/v1/team/tasks/<uuid>/` | Vazifa statusini yangilash |
| GET | `/api/v1/competitors/` | Raqobatchilar ro'yxati |
| GET | `/api/v1/competitors/<uuid>/` | Raqobatchi dosyasi |

---

### 4.3. AI INTEGRATION PIPELINE

```
[ Tender matni / Hujjat chunks ]
              │
              ▼
[ System Prompt (O'zbekiston qonunchiligi + qoidalar) ]
              │
              ▼
[ Gemini API (Free Tier) ] ──► [ Structured JSON Output ]
              │
              ▼
[ SafeJSONParser ] ──► [ AITenderAnalysis jadvaliga saqlash ]
              │
              ▼
[ Frontend render ]
```

**System Prompt:**
```
Siz TenderHelper tizimining yetakchi huquqiy va texnik tahlilchisiz. 
Berilgan tender matni ichidan:
1. Asosiy ma'lumotlarni ajratib oling (buyurtmachi, predmet, narx, muddat)
2. O'zDSt, GOST va ISO standartlarini aniqlang
3. Murakkab iboralarni oddiy tilga o'giring
4. Raqobatni cheklovchi, bitta brendga moslangan shartlarni "Red Flags" 
   ro'yxatiga kiriting
5. Yetishmayotgan hujjatlarni aniqlang
6. Qatnashish tavsiyasini bering

Javobni faqat belgilangan JSON formatida qaytaring.
Ton: sodda, do'stona, "Siz qila olasiz" ruhida.
5 qatordan uzun paragraf yozmaslik.
```

**MVP AI provider:** Google Gemini API (Free Tier — 15 RPM, 1M tokens/kun)

---

### 4.4. XAVFSIZLIK VA XATO BOSHQARUVI

#### Rate Limiting

| Tarif | AI tahlil | Qidiruv |
|-------|-----------|---------|
| **Free** | 4 ta / oy | 15 ta / daqiqa |
| **Pro** | Cheksiz | 60 ta / daqiqa |
| **Enterprise** | Cheksiz | 100 ta / daqiqa |

#### Xato holatlari

| Holat | Tizim reaktsiyasi |
|-------|-------------------|
| Tender matni noto'liq | "Tender matnida [X] bo'lim yo'q. To'liq hujjatni yuboring" |
| AI javob bermadi (10 sek) | Status → `failed`, 1 marta retry |
| JSON parse xato | SafeJSONParser tozalab standart formatga keltiradi |
| Internet uzildi | Oxirgi natijalarni localStorage / cache'dan ko'rsatish |
| API limit tugadi | "Oylik limitingiz tugadi. Pro tarifga o'ting" |

#### AI xavfsizlik qoidalari
- ❌ Yuridik maslahat bermasin — "Huquqshunos bilan maslahat qiling"
- ❌ Aniq g'alaba kafolatini bermasin
- ❌ Foydalanuvchini qo'rqitmasin
- ❌ 10 dan ortiq javob varianti bermasin
- ✅ Har bir natijada disclaimer bo'lsin

---

## 📌 5-QISM: TARIF MODELI VA MONETIZATSIYA

### 5.1. TARIF REJALARI

| | 🆓 FREE | ⭐ PRO | 🏢 ENTERPRISE |
|---|---------|--------|---------------|
| **Narx** | $0 | $15/oy | $50/oy |
| **AI tahlil** | 4 ta/oy | ♾️ Cheksiz | ♾️ Cheksiz |
| **Qidiruv** | Asosiy | 25+ filtr | 25+ filtr |
| **Kalkulyator** | ✅ | ✅ | ✅ |
| **Red Flags** | ✅ | ✅ | ✅ |
| **Hujjatlar checklist** | ✅ | ✅ | ✅ |
| **Raqobatchi razvedkasi** | ❌ | ❌ | ✅ |
| **Jamoaviy xona** | ❌ | ❌ | ✅ |
| **Tijorat taklifi export** | ❌ | ✅ (V2) | ✅ (V2) |
| **Push notifications** | ❌ | ✅ | ✅ |

### 5.2. TO'LOV TIZIMLARI

**MVP integratsiya:**
- 💳 Payme
- 💳 Click
- 💳 Uzum Bank

**V2 da qo'shiladi:**
- Karta to'g'ridan-to'g'ri (Visa/Mastercard)
- Humo / UzCard

> **MVP qaror:** To'lov UI va endpoint tayyor bo'ladi, merchant shartnomalar keyinroq ulanadi. MVP davrida Pro/Enterprise bepul test sifatida berilishi mumkin.

---

## 📌 6-QISM: ROADMAP

### V1 — MVP ⏱️ 2-4 hafta

- ✅ Auth: Telefon + OTP + Google OAuth
- ✅ Onboarding: 3 savol + kompaniya profili
- ✅ TenderLot: Portallardan ma'lumot olish (API/scraping)
- ✅ AI Tahlil: Gemini Free API orqali tender tahlili
- ✅ Smart Kalkulyator: QQS + operator haqi + Stop-Loss
- ✅ Red Flags: Xavflarni avtomatik aniqlash
- ✅ Qidiruv: LIKE + asosiy filtrlar
- ✅ PWA: Mobile-first, offline lite
- ✅ Dark mode
- ✅ Tarif tizimi UI (to'lov merchant keyinroq)

### V2 — Kengaytirish ⏱️ 1-2 oy

- ➕ OneID integratsiya
- ➕ Celery + Redis (asinxron AI va scraping)
- ➕ LangChain + RAG (chuqur tahlil)
- ➕ Pgvector (semantic search)
- ➕ PDF/DOCX tijorat taklifi export
- ➕ Soliq API integratsiya
- ➕ Merchant shartnomalar va real to'lov
- ➕ Push notifications

### V3 — Enterprise ⏱️ 3-6 oy

- ➕ Telegram Bot / Mini App
- ➕ Raqobatchi razvedkasi (real-time)
- ➕ Jamoaviy virtual xona
- ➕ Tender radar (avtomatik bildirishnomalar)
- ➕ Hujjat OCR (PDF/DOCX parsing)
- ➕ To'liq veb-portal yoki mobil ilova

---

## 📌 7-QISM: MUVAFFAQIYAT MEZONLARI (KPIs)

| Mezon | MVP maqsad | V2 maqsad | V3 maqsad |
|-------|-----------|-----------|-----------|
| Kunlik foydalanuvchilar | 50+ | 500+ | 5,000+ |
| Sessiya davomiyligi | 3+ daqiqa | 5+ daqiqa | 7+ daqiqa |
| AI tahlil aniqligi | 75%+ | 85%+ | 92%+ |
| Foydalanuvchi qaytishi | 25%+ | 40%+ | 55%+ |
| Pro konversiya | 3%+ | 8%+ | 12%+ |
| Oylik daromad (MRR) | — | $500+ | $5,000+ |
