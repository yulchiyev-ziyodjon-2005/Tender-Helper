# TenderHelper — Asosiy Strategik va Texnik Reja

**Versiya:** 4.3
**Yangilangan:** 2026-06-14  
**Status:** Canonical plan — barcha texnik qarorlar uchun yagona boshqaruvchi hujjat

---

## 1. Hujjat Maqsadi

Ushbu `Plan.md` TenderHelper loyihasining yagona amaldagi strategik va
texnik rejasidir. Eski texnik topshiriqlar va rejalar tarixiy ma'lumot sifatida
`docs/archive/` ichida saqlanadi.

Qarorlar ustuvorligi:

1. Foydalanuvchi va biznes ma'lumotlari xavfsizligi.
2. Tender tahlilining tekshirilishi va izohlanishi.
3. Tizim barqarorligi va kuzatuvchanligi.
4. MVP'ni tez va o'lchanadigan tarzda bozorga chiqarish.
5. Infratuzilma xarajatlarini oqilona past saqlash.

Har bir implementatsiya tafsiloti ADR (Architecture Decision Records),
OpenAPI schema va issue trackerda yuritiladi. Hujjat va kod o'rtasida
ziddiyat bo'lsa — **hujjat yangilanadi yoki kod to'g'rilanadi**, lekin
ular parallel va bir-biriga zid holatda qolmasligi shart.

Ushbu strategiyaning bajarilish ketma-ketligi, work package'lar, model va API
spetsifikatsiyasi hamda acceptance criteria'lari `IMPLEMENTATION_PLAN.md`
kanonik companion hujjatida yuritiladi.

UI/UX ekranlari va interaction contractlari `DESIGN.md`da yuritiladi.
`docs/API.md` esa amaldagi implementatsiya qilingan API'ning snapshotidir;
target endpointlar ushbu reja va `IMPLEMENTATION_PLAN.md`da belgilanadi.

---

## 2. Loyiha Maqsadi

TenderHelper — O'zbekiston davlat va korporativ xaridlarida qatnashuvchi
kichik va o'rta bizneslar uchun AI Tender Mentor SaaS platformasi.

Platforma:

- milliy xarid portallaridan tender lotlarini yig'adi;
- lot va hujjatlarni qidirish va filtrlash imkonini beradi;
- tender shartlarini oddiy tilda tushuntiradi;
- kompaniya profiliga nisbatan moslik ballini hisoblaydi;
- hujjatlar checklisti va xavf signallarini beradi;
- STIR orqali ochiq davlat reyestrlaridan kompaniya rekvizitlarini topib,
  onboarding formasini editable draft sifatida avtomatik to'ldiradi;
- kompaniya va tender konteksti asosida ariza, kafolat xati va tijorat
  takliflarini generatsiya qilib, inline tahrirlash imkonini beradi;
- tannarx, QQS, komissiya va foyda chegarasini hisoblaydi;
- mos lotlar haqida Telegram orqali xabar beradi;
- Business tarifida jamoaviy ish va real ochiq ma'lumotlarga asoslangan
  raqobatchilar tahlilini taqdim etadi.

Platforma tenderda g'alabani kafolatlamaydi va yuridik maslahat o'rnini
bosmaydi. Har bir AI natijasi dalil, manba va disclaimer bilan berilishi kerak.

### 2.1. Asosiy foydalanuvchilar

| Persona | Ehtiyoj |
|---|---|
| YaTT va kichik biznes | Tenderni tushunish, hujjat va narx xatolarini kamaytirish |
| MChJ va yetkazib beruvchi | Mos lotlarni tez topish va tahlil qilish |
| Tender menejeri | Bir nechta lot, hujjat va vazifani boshqarish |
| Administrator | Scraping, AI, billing va foydalanuvchi holatini kuzatish |

---

## 3. Hozirgi Holat

Repository hozir demo/MVP prototip bosqichida:

- Django REST Framework backend mavjud;
- React 19, Vite 8 va Tailwind CSS 4 frontend mavjud;
- email, OTP va Google OAuth oqimlarining bir qismi mavjud;
- tender qidiruvi va qo'lda tender kiritish mavjud;
- Gemini orqali sinxron AI tahlil prototipi mavjud;
- Smart Calculator prototipi mavjud;
- i18n (5 til) va dark mode interfeysi mavjud;
- SQLite ishlatilmoqda;
- scraper, subscription, team va competitor modullari to'liq emas.

### 3.1. Production'ga chiqishdan oldin yopilishi shart bo'lgan muammolar

| # | Muammo | Jiddiylik | Tegishli bo'lim |
|---|--------|-----------|-----------------|
| 1 | `analysis/views.py` dagi barcha endpointlar `AllowAny` — autentifikatsiyasiz ochiq | 🔴 Kritik | §7.3, §17 |
| 2 | `_current_company()` har doim demo kompaniya yaratadi, `DEMO_MODE` flag'ni tekshirmaydi | 🔴 Kritik | §4.3, §7.3 |
| 3 | AI xatosida soxta `COMPLETED` status va mock "92%" natija qaytarilmoqda | 🔴 Kritik | §4.1, §10.3 |
| 4 | `settings.py` va `views.py` da turli model nomlari hardcode qilingan | 🟡 O'rta | §10.2 |
| 5 | Production'da ham ishlaydigan `print()` debug satrlari mavjud | 🟡 O'rta | §4.3, §18 |
| 6 | QQS va komissiya stavkalari global konstanta, platformaga bog'lanmagan | 🟡 O'rta | §12.2 |
| 7 | Groq SDK `requirements.txt` da yo'q | 🟡 O'rta | §10.2 |
| 8 | OAuth callback tokenni URL query parametrida qaytaradi | 🟡 O'rta | §7.2 |
| 9 | Manual tender yaratish `AllowAny` | 🔴 Kritik | §7.3, §17 |
| 10 | Frontend private/public route guard vaqtincha o'chirilgan | 🔴 Kritik | §7.2, §16 |
| 11 | Amaldagi tarif modeli faqat Free/Pro/Enterprise | 🟡 O'rta | §14.1 |
| 12 | `subscriptions` modeli va payment lifecycle hali yo'q | 🔴 Kritik | §14 |
| 13 | `documents` app va document editor route'lari mavjud emas | 🟡 O'rta | §6.4, §10.6 |
| 14 | `teams` va `competitors` applari placeholder | 🟡 O'rta | §6.7, §11.1 |
| 15 | API error envelope endpointlar bo'yicha bir xil emas | 🟡 O'rta | §15 |
| 16 | `docs/API.md` faqat amaldagi demo API snapshoti | 🟢 Axborot | §15 |
| 17 | `_current_company()` olib tashlangan `username` field orqali demo user qidiradi | 🔴 Kritik | §4.3, §7.3 |
| 18 | `.env.example`da `DEMO_MODE` ko'rsatilmagan | 🟡 O'rta | §7.3, §20 |
| 19 | OTP `random` bilan yaratiladi va console/loggerga kod chiqaradi | 🔴 Kritik | §17 |
| 20 | `CompanyProfile.user` bitta egaga bog'langan, membership modeli yo'q | 🟡 O'rta | §6.1, §7.3 |
| 21 | Tender identity global unique `lot_number`, target `(source, external_id)` emas | 🟡 O'rta | §6.2, §8.2 |
| 22 | Ko'p app testlari placeholder, analysis testi mock success'ni legitimlashtiradi | 🔴 Kritik | §19 |

---

## 4. Mahsulot Prinsiplari

### 4.1. Ishonch

- AI xatosi muvaffaqiyatli natija sifatida ko'rsatilmaydi.
  **Amaliy talab:** API xato berganda `analysis_status = FAILED` qaytariladi,
  foydalanuvchiga "Tahlil muvaffaqiyatsiz, qayta urinib ko'ring" ko'rsatiladi.
  Soxta mock natija `COMPLETED` status bilan qaytarilishi **qat'iyan man etiladi**.
- Aniqlanmagan ma'lumot `unknown` yoki `not_found` deb qaytariladi.
- Muhim xulosa tender hujjatidagi manba bo'lagi bilan bog'lanadi.
- Moliyaviy formulalar versiyalanadi va faqat backendda hisoblanadi.

### 4.2. Soddalik

- Asosiy oqim: topish → tahlil → qaror → hisoblash → kuzatish.
- Foydalanuvchiga bir ekranda ortiqcha texnik tafsilot berilmaydi.
- Mobil interfeys birinchi darajali hisoblanadi.

### 4.3. Xavfsizlik

- Default holatda barcha shaxsiy va write endpointlar `IsAuthenticated`.
  **Amaliy talab:** `AllowAny` faqat ommaviy tender ro'yxati va health-check
  endpointlarida ishlatiladi. Boshqa barcha endpointlarda `permission_classes`
  `IsAuthenticated` bo'lishi shart. Bu CI testlari orqali tekshiriladi.
- Har bir obyektga company ownership tekshiruvi qo'llanadi.
- Secret va tokenlar URL, log yoki frontend bundle ichiga chiqmaydi.
  **Amaliy talab:** `print()` debug chiqarishlari o'rniga `logging` moduli
  ishlatiladi. Production'da log darajasi `WARNING` yoki undan yuqori.
- Demo rejim faqat `DEMO_MODE=True` environment variable orqali yoqiladi
  va production konfiguratsiyasida ishga tushmaydi. Demo bypass funksiyalari
  `if settings.DEMO_MODE` sharti ichida yoziladi.

### 4.4. O'lchanadigan sifat

Mutlaq "100% aniqlik" yoki "100% test coverage" va'da qilinmaydi.
Quyidagi metrikalar ishlatiladi:

- strukturaviy JSON javoblar muvaffaqiyati;
- manba bilan tasdiqlangan xulosalar ulushi;
- ekspert baholagan precision/recall;
- p95 API va AI javob vaqti;
- scraping freshness;
- kritik oqim test coverage;
- foydalanuvchi qaytishi va pullik tarifga o'tish.

---

## 5. Target Arxitektura

```text
React PWA / Telegram Mini App
              |
              v
     api.tender-helper.uz
       Nginx + HTTPS
              |
              v
       Django REST API
        |     |      |
        |     |      +--> AI Provider Gateway
        |     |             |--> Gemini (tahlil, embedding)
        |     |             +--> Groq (tezkor chat, fallback)
        |     |
        |     +--> Celery Workers --> Scraping / Parsing / Analysis
        |
        +--> PostgreSQL + pgvector
        +--> Redis (broker + cache)
        +--> Object/File Storage (S3-compatible)
        +--> Telegram Bot Worker (Aiogram)
```

### 5.1. Frontend

- React 19 + Vite 8.
- Tailwind CSS 4.
- React Router v7.
- TanStack Query v5.
- Zustand faqat lokal UI holati uchun (auth, sidebar, theme).
- `react-i18next`: `uz`, `ru`, `en`; `kaa` va `tg` keyingi bosqich.
  Tarjima fayllari `src/i18n/locales/{lang}/common.json` da saqlanadi.
- PWA va Telegram Mini App uchun bitta frontend codebase.
- Route-level lazy loading va code splitting.

Hosting:

- Vercel yoki unga teng CDN hosting.
- Asosiy domen: `tender-helper.uz`.

### 5.2. Backend

- Python 3.11+.
- Django 5 + Django REST Framework 3.15+.
- API domeni: `api.tender-helper.uz`.
- Gunicorn/Uvicorn, Nginx reverse proxy va Let's Encrypt HTTPS.
- OpenAPI schema va versiyalangan `/api/v1/` endpointlar.

### 5.3. Database

- PostgreSQL 16+ asosiy ma'lumotlar bazasi.
- `pgvector` extension faqat semantic retrieval zarur bo'lgan hujjatlar uchun.
- Indekslar real query plan (`EXPLAIN ANALYZE`) asosida qo'shiladi.
- SQLite faqat yengil local development va tez unit test uchun.
  **Production va staging muhitlarida SQLite ishlatilmaydi.**
- Kunlik backup va restore testi majburiy.

### 5.4. Async Queue

- Redis broker/cache.
- Celery worker:
  - portal scraping;
  - hujjat yuklash;
  - PDF/DOCX parsing va OCR;
  - embedding yaratish;
  - AI tahlil (async);
  - match score hisoblash;
  - Telegram notification yuborish.
- Celery Beat davriy vazifalarni ishga tushiradi.
- Vazifalar idempotent va retry-safe bo'lishi kerak.
- Har bir task `task_id`, `company_id`, `analysis_id` bilan loglanadi.

### 5.5. Fayl Saqlash

- Tender hujjatlari database ichida binary shaklda saqlanmaydi.
- Local development uchun `media/` storage.
- Production uchun S3-compatible object storage (MinIO yoki AWS S3).
- Fayl turi (MIME), hajmi (max 50MB), checksum (SHA-256) tekshiruvi qo'llanadi.
- Antivirus scanning production'da majburiy.

---

## 6. Asosiy Ma'lumot Modellari

### 6.1. Identity va kompaniya

- `CustomUser` — telefon, email, Google OAuth.
- `CompanyProfile` — STIR, tashkiliy shakl, soha, QQS holati.
- `CompanyProfile` registry maydonlari — rahbar, yuridik manzil, registry
  manbasi/statusi, oxirgi lookup va STIR skip holati.
- `CompanyMember` — foydalanuvchi↔kompaniya bog'lanishi va roli.
- `UserConsent` — shaxsiy ma'lumotlar qayta ishlashga rozilik.
- `NotificationPreference` — kanal va chastota sozlamalari.

Bir foydalanuvchi bir yoki bir nechta kompaniyaga tegishli bo'lishi mumkin.
Ruxsatlar user roli emas, kompaniya a'zoligi orqali boshqariladi:
`owner`, `manager`, `analyst`, `viewer`.

### 6.2. Tenderlar

- `TenderSource` — portal konfiguratsiyasi.
- `TenderLot` — asosiy lot ma'lumotlari.
- `TenderDocument` — yuklangan hujjat metadata.
- `TenderDocumentChunk` — hujjat bo'laklari (matn + embedding).
- `ScrapeRun` — har bir scraping sessiyasi statistikasi.
- `ScrapeError` — xatolar va retry holati.

`TenderLot` uchun `(source, external_id)` unique constraint ishlatiladi.
Portal ma'lumotining asl JSON nusxasi audit uchun `raw_json` maydonida saqlanadi.

### 6.3. Tahlil

- `AITenderAnalysis` — tahlil natijalari va status.
- `AnalysisFinding` — alohida topilma (red flag, requirement, standard).
- `AnalysisCitation` — topilmaning manba hujjatdagi joyi.
- `AnalysisRun` — AI chaqiruv sessiyasi (prompt, model, vaqt).
- `ModelInvocation` — har bir LLM chaqiruvi auditi (model, token, narx, status).

AI natijasi faqat JSON blob bo'lib qolmasligi kerak. Muhim findinglar,
ularning severity (`blocker`, `warning`, `info`), confidence (0.0–1.0) va
citation (hujjat, sahifa, chunk, evidence) ma'lumotlari alohida saqlanadi.

### 6.4. Generatsiya qilinadigan hujjatlar

- `TenderDocumentTemplate` — versiyalangan ariza, kafolat xati va taklif
  shablonlari, talab qilinadigan company fieldlar va prompt konfiguratsiyasi.
- `GeneratedDocument` — kompaniya va tender kontekstidan yaratilgan,
  canonical rich-text JSON asosida inline tahrirlanadigan hujjat drafti.
- `GeneratedDocumentRevision` — autosave'dan tashqari muhim versiyalar,
  muallif, vaqt va o'zgarish metadata'si.
- `DocumentExport` — PDF/DOCX export holati va object storage metadata'si.

Ushbu modellar `analysis` ichida emas, alohida `documents` Django app'ida
joylashadi. Sanitizatsiyalangan HTML va plain text canonical JSON'dan hosil
qilinadigan projection hisoblanadi.

### 6.5. Tavsiyalar

- `CompanyTenderMatch` — kompaniya↔lot moslik balli.
- `SavedSearch` — saqlangan qidiruv filtrlari.
- `Watchlist` — kuzatiladigan lotlar.
- `NotificationDelivery` — yuborilgan xabarlar logi.

### 6.6. Billing

- `SubscriptionPlan` — tarif parametrlari.
- `CompanySubscription` — kompaniyaning aktiv tarifi.
- `UsageRecord` — AI tahlil, qidiruv va export sarfi.
- `PaymentTransaction` — to'lov tranzaksiyalari.
- `WebhookEvent` — provider webhook logi (idempotency key bilan).
- `AdminAuditEvent` — superadminning kritik boshqaruv amallari uchun
  append-only audit yozuvi.

To'lov holati faqat tekshirilgan provider webhookidan keyin o'zgaradi.
Client-side callback **hech qachon** subscriptionni faollashtirmaydi.

### 6.7. Business Intelligence va Enterprise

- `TeamTask` — jamoa vazifalari.
- `TaskComment` — vazifa izohlari.
- `Competitor` — raqobatchi kompaniyalar.
- `CompetitorTenderResult` — raqobatchi tender natijalari.
- `CompetitorAnalytics` — lot yoki kategoriya kesimida hisoblangan rank,
  g'alabalar, ishtiroklar va o'rtacha demping statistikasi.

Competitor analytics'ning lot/category bo'yicha baseline ko'rinishi Business
beta sifatida MVP tarkibiga kiradi. Team task, trend/comparison export,
kengaytirilgan audit va yuqori limitlar core MVP barqarorlashgandan keyingi
Business/Enterprise bosqichida yoqiladi.

---

## 7. Authentication va Authorization

### 7.1. Login usullari

MVP:

- email va parol;
- telefon OTP (Eskiz.uz);
- Google OAuth 2.0.

Keyingi bosqich:

- Telegram Mini App `initData` authentication;
- OneID, faqat rasmiy shartnoma va xavfsizlik talablari aniqlangach.

### 7.2. Token strategiyasi

- Access token: qisqa muddatli (default 60 daqiqa, env orqali sozlanadi).
- Refresh token: uzoq muddatli (default 7 kun), rotation va reuse detection.
- OAuth tokenlari URL query parametrida **yuborilmaydi**.
  **Amaliy talab:** Google OAuth callback bir martalik `authorization_code`
  beradi, frontend uni `POST /auth/google/callback/` orqali backendga
  yuboradi va backend JWT juftligini qaytaradi. Token **hech qachon**
  URL `?token=xxx` shaklida qaytarilmaydi.
- Tavsiya etilgan browser oqimi: Secure, HttpOnly, SameSite cookie.
- Logout refresh tokenni revoke qiladi (blacklist).

### 7.3. Permission qoidalari

- Tender ro'yxatini ommaviy qilish mahsulot qaroriga bog'liq.
  Hozircha `GET /tenders/` uchun `AllowAny` ruxsat etiladi.
- Manual tender yaratish (`POST /tenders/`) faqat `IsAuthenticated`.
- Analysis, calculator, history, profile va billing — faqat `IsAuthenticated`.
- Har bir company-scoped query membership bilan filtrlanadi:
  `CompanyProfile.objects.filter(members__user=request.user)`.
- Admin endpointlari audit logga yoziladi.
- Demo mode:
  - `DEMO_MODE=True` bo'lganda `_current_company()` demo kompaniya yaratadi.
  - `DEMO_MODE=False` (production default) bo'lganda `_current_company()`
    faqat foydalanuvchining haqiqiy kompaniyasini qaytaradi yoki `None`.
  - Demo mode production `.env` da **hech qachon** `True` bo'lmaydi.

### 7.4. STIR onboarding va registry lookup

Onboarding foydalanuvchini STIR kiritishga majburlamaydi, lekin STIR mavjud
bo'lsa rasmiy rekvizitlar bilan ishlaydigan imkoniyatlarni ochadi.

Oqim:

1. Foydalanuvchi STIR kiritadi.
2. Frontend `POST /api/v1/companies/registry/lookup/` endpointini chaqiradi.
3. Backend Soliq yoki Statistika ochiq reyestri adapteriga murojaat qiladi.
4. Tashqi javob normalizatsiya qilinadi va quyidagilar editable draft sifatida
   qaytariladi:
   - kompaniyaning rasmiy nomi;
   - tashkiliy-huquqiy shakli;
   - rahbar F.I.Sh.;
   - yuridik manzil;
   - ro'yxatdan o'tgan sana;
   - QQS holati;
   - faoliyat sohasi, mavjud bo'lsa.
5. Foydalanuvchi avtomatik to'ldirilgan qiymatlarni tahrirlaydi va tasdiqlaydi.
6. Asl registry payload `raw_tax_data` ichida audit uchun, foydalanuvchi
   tasdiqlagan qiymatlar esa `CompanyProfile` maydonlarida saqlanadi.

Registry adapter talablari:

- `CompanyRegistryProvider` interfeysi va provider-specific adapterlar;
- timeout 5 soniya, retry 1 marta;
- natijani STIR bo'yicha 24 soat cache qilish;
- provider ishlamasa onboarding bloklanmaydi, qo'lda kiritish taklif qilinadi;
- `registry_status`: `not_checked`, `pending`, `verified`, `not_found`,
  `failed`, `manual`;
- lookup va user edit audit logga yoziladi;
- tashqi ma'lumot foydalanuvchi tasdig'isiz yakuniy profilga yozilmaydi.

#### Skip STIR va feature gating

`STIRsiz davom etish` tugmasi `stir_skipped=True` holatini saqlaydi.
STIRsiz foydalanuvchi:

- tender qidiruvi va filtrlaridan;
- umumiy AI tahlilidan;
- kalkulyatordan;
- watchlist va notificationlardan foydalanishi mumkin.

Quyidagi rasmiy rekvizit talab qiladigan funksiyalar STIR kiritilmaguncha
yopiq bo'ladi:

- rasmiy ariza, kafolat xati va tijorat taklifini generatsiya qilish;
- rasmiy tender paketiga export;
- davlat reyestri bilan tasdiqlangan company badge;
- STIR asosidagi competitor/company matching.

Gate foydalanuvchiga sabab va `STIR qo'shish` actioni bilan ko'rsatiladi.
STIR keyinroq profil sozlamalaridan qo'shilishi va registry lookup qayta
ishga tushirilishi mumkin.

---

## 8. Tender Data Pipeline

### 8.1. Manbalar

Rejalashtirilgan manbalar:

| # | Portal | URL | Ustuvorlik |
|---|--------|-----|-----------|
| 1 | UzEx xarid | `xarid.uzex.uz` | MVP — birinchi integratsiya |
| 2 | UzEx dxarid | `dxarid.uzex.uz` | Bosqich 2 |
| 3 | UzEx exarid | `exarid.uzex.uz` | Bosqich 2 |
| 4 | E-Auksion | `e-auksion.uz` | Bosqich 2 |

Har bir portal bo'yicha avval:

- rasmiy API mavjudligi;
- foydalanish shartlari (ToS 7.3, 8.1 bandlari);
- `robots.txt` va rate-limit;
- ma'lumotni tijorat maqsadida qayta ishlatish huquqi

tekshiriladi. HTML scraping faqat ruxsat va barqarorlik bahosidan keyin
ishlatiladi. Huquqiy tekshiruv natijasi ADR-006 da hujjatlanadi.

### 8.2. Pipeline

```text
Fetch → Validate → Normalize → Upsert → Download documents
      → Parse/OCR → Chunk → Embed → Match companies → Notify
```

Talablar:

- har bir `ScrapeRun` uchun status, vaqt va statistikalar;
- source-specific adapter pattern (`XaridAdapter`, `EAuksionAdapter`);
- timeout (30s), retry (3 marta) va exponential backoff (2^n * 1s);
- `(source, external_id)` unique constraint orqali duplicate oldini olish;
- portal HTML/API schema o'zgarishini aniqlash va alert berish;
- dead-letter queue: 3 marta failed task monitoring va admin notification;
- lot statusi va deadline yangilanishini kuzatish.

Yakunlangan tenderlar alohida analytics pipeline orqali qayta ishlanadi:

```text
Completed lots -> normalize participants/winner/bids
    -> calculate discount and win metrics
    -> aggregate by lot/category/period
    -> upsert CompetitorAnalytics
```

Analytics pipeline faqat ochiq va huquqiy qayta ishlatishga ruxsat etilgan
ma'lumotlardan foydalanadi. Har bir agregat `source_count`, davr va
`calculated_at` bilan kuzatiladi.

### 8.3. Freshness

MVP maqsadi:

| Metrik | Maqsad |
|--------|--------|
| Portal tekshiruv chastotasi | Har 30 daqiqa |
| Yangi lot bazaga tushish vaqti | ≤ 45 daqiqa |
| Scraper xatosi monitoring'ga chiqishi | ≤ 5 daqiqa |
| Hujjat yuklash va parsing | ≤ 15 daqiqa (lotdan keyin) |

### 8.4. LIKE qidiruv strategiyasi

MVP tender qidiruvining asosiy mexanizmi PostgreSQL `LIKE`/`ILIKE`
operatorlari bo'ladi. Django ORM'da bu `__icontains` lookup orqali amalga
oshiriladi:

```python
TenderLot.objects.filter(
    Q(title__icontains=query)
    | Q(buyer_name__icontains=query)
    | Q(lot_number__icontains=query)
)
```

Qidiruv quyidagi maydonlarda ishlaydi:

- `title`;
- `buyer_name`;
- `lot_number`;
- `category`;
- zarur bo'lsa `region`.

Talablar:

- foydalanuvchi matni ORM parametrizatsiyasi orqali uzatiladi, raw SQL string
  concatenation ishlatilmaydi;
- qidiruv case-insensitive bo'lishi uchun PostgreSQL `ILIKE` ishlatiladi;
- bo'sh yoki faqat whitespace query barcha aktiv lotlarni pagination bilan
  qaytaradi;
- qidiruv `status=active` filtri va region, category, narx, platforma,
  deadline filtrlariga birga qo'llanadi;
- minimal query uzunligi UI'da 2 belgi;
- frontend debounce: 300-500 ms;
- natijalar default 20 ta, maksimal 100 ta sahifalanadi;
- natijalar `deadline`, `posted_date` yoki `start_price` bo'yicha saralanadi.

#### Tezlik uchun PostgreSQL indekslari

Oddiy B-tree indeks `%query%` ko'rinishidagi substring qidiruvni samarali
tezlashtirmaydi. Shuning uchun production va staging PostgreSQL bazalarida
`pg_trgm` extension va GIN trigram indekslar ishlatiladi:

```sql
CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE INDEX tender_lot_title_trgm_idx
ON tender_lots USING gin (title gin_trgm_ops);

CREATE INDEX tender_lot_buyer_name_trgm_idx
ON tender_lots USING gin (buyer_name gin_trgm_ops);

CREATE INDEX tender_lot_lot_number_trgm_idx
ON tender_lots USING gin (lot_number gin_trgm_ops);
```

`status`, `deadline`, `platform_source`, `region` va `category` uchun oddiy
B-tree indekslar saqlanadi. Indekslar Django migration orqali yaratiladi va
`EXPLAIN ANALYZE` bilan tekshiriladi.

Performance maqsadi:

| Dataset | LIKE qidiruv p95 |
|---------|------------------|
| 100 ming lotgacha | ≤ 300 ms |
| 1 million lotgacha | ≤ 500 ms |

MVP'da Elasticsearch yoki alohida search engine ishlatilmaydi. Semantic
RAG qidiruvi tender hujjatlari ichidagi AI kontekstni topish uchun ishlaydi;
foydalanuvchining lot qidiruvi esa avval `ILIKE` + `pg_trgm` orqali bajariladi.

---

## 9. Hujjatlarni Qayta Ishlash va RAG

### 9.1. Qo'llab-quvvatlanadigan formatlar

| Format | Qo'llab-quvvatlash | Izoh |
|--------|-------------------|------|
| PDF | To'liq | Matn va jadval ajratish |
| DOCX | To'liq | python-docx orqali |
| XLSX | Asosiy | Jadval ma'lumotlarini matn sifatida |
| Image PDF | OCR | Tesseract yoki Google Vision API |

### 9.2. Pipeline

1. MIME type va fayl hajmini tekshirish (max 50MB).
2. SHA-256 checksum hisoblash (duplicate oldini olish).
3. Matn va jadvalni ajratish (pdfplumber / python-docx).
4. Sahifa va bo'lim metadata bilan chunklash.
5. Embedding yaratish (Gemini text-embedding-004).
6. PostgreSQL/pgvector ichida saqlash.
7. Retrieval natijasini semantic similarity bo'yicha rerank qilish.

### 9.3. Chunking strategiyasi

Chunklar faqat `1000 character` qat'iy qiymatiga bog'lanmaydi.
Token-based strategiya benchmark orqali tanlanadi:

| Parametr | Boshlang'ich qiymat | Sozlash usuli |
|----------|-------------------|---------------|
| Chunk hajmi | 512 token (~2000 belgi) | Tender bo'lim strukturasiga mos |
| Overlap | 64 token (~250 belgi) | Bo'limlar orasidagi kontekst saqlanishi uchun |
| Splitter | Bo'lim sarlavhasi → paragraf → jumla | Tender hujjat strukturasiga mos |

### 9.4. Embedding konfiguratsiyasi

| Parametr | Qiymat | Sabab |
|----------|--------|-------|
| Model | `text-embedding-004` (Gemini) | Bepul tier, O'zbek/Rus/Ingliz qo'llab-quvvatlaydi |
| Dimension | 768 | Model output o'lchami |
| Distance metric | Cosine similarity | Matn semantik o'xshashlik uchun standart |
| Index turi | IVFFlat (lists=100) | <100K chunk uchun optimal; 100K+ da HNSW ga o'tish |
| pgvector column | `embedding vector(768)` | `TenderDocumentChunk` modelida |

**Muhim:** Embedding model o'zgartilganda dimension o'zgarishi mumkin.
Bu holda mavjud embeddinglar qayta yaratilishi va index qayta qurilishi kerak.
Bu jarayon `management command` orqali avtomatlashtiriladi.

### 9.5. Citation talablari

Har bir AI finding quyidagiga bog'lanishi kerak:

- hujjat (`TenderDocument`);
- sahifa yoki bo'lim raqami;
- chunk (`TenderDocumentChunk`);
- qisqa evidence (asl matndan 1-3 jumla);
- confidence balli (0.0–1.0).

Evidence bo'lmagan topilma `confidence < 0.3` bilan belgilanadi va
foydalanuvchiga "Tasdiqlangan emas" sifatida ko'rsatiladi.

---

## 10. AI Arxitekturasi

### 10.1. Provider Gateway

Backendda umumiy interfeys (`AIProviderInterface` abstract class):

```python
class AIProviderInterface(ABC):
    @abstractmethod
    def analyze_tender(self, prompt: str, schema: dict) -> dict: ...

    @abstractmethod
    def answer_question(self, context: str, question: str) -> str: ...

    @abstractmethod
    def extract_structured_data(self, text: str, schema: dict) -> dict: ...

    @abstractmethod
    def generate_embedding(self, text: str) -> list[float]: ...
```

Har bir provider uchun alohida adapter: `GeminiAdapter`, `GroqAdapter`.
Business logika to'g'ridan-to'g'ri Gemini yoki Groq SDK'ga bog'lanmaydi —
faqat gateway interfeysi orqali ishlaydi.

**Qaror (ADR-004):** LangChain, LlamaIndex va boshqa orchestration
frameworklar **ishlatilmaydi**. Sabablari:

1. Oddiy REST API chaqiruv uchun ortiqcha abstraksiya murakkabligi.
2. Provider Gateway allaqachon framework'siz adapter pattern'ni qo'llaydi.
3. LangChain chain'lari ichidagi xatolarni debug qilish vaqt talab etadi.
4. Dependency soni va versiya conflictlarini kamaytirish.

### 10.2. Model rollari va taqsimoti

| Vazifa | Provider | Model | Sabab | Fallback |
|--------|----------|-------|-------|----------|
| Tender tahlili (structured JSON) | Gemini | `gemini-2.5-flash` | 1M context, native JSON mode, O'zbek tili sifati | Groq `llama-3.3-70b-versatile` |
| Tezkor savol-javob (chat) | Groq | `llama-3.3-70b-versatile` | <200ms TTFT, bepul tier yetarli | Gemini `gemini-2.5-flash` |
| Function calling / extraction | Gemini | `gemini-2.5-flash` | Structured output ishonchliligi yuqori | — |
| Embedding | Gemini | `text-embedding-004` | 768-dim, bepul tier, ko'p tilli | — |

**Muhim qoidalar:**

- Model nomlari kodda hardcode qilinmaydi. Faqat `settings.py` dagi
  environment variable'lar orqali boshqariladi:

  ```python
  GEMINI_MODEL_ANALYSIS = os.getenv('GEMINI_MODEL_ANALYSIS', 'gemini-2.5-flash')
  GEMINI_MODEL_EMBEDDING = os.getenv('GEMINI_MODEL_EMBEDDING', 'text-embedding-004')
  GROQ_MODEL_CHAT = os.getenv('GROQ_MODEL_CHAT', 'llama-3.3-70b-versatile')
  ```

- `views.py` yoki boshqa fayllarda model nomi to'g'ridan-to'g'ri URL'ga
  yozilmaydi — faqat `settings.GEMINI_MODEL_ANALYSIS` ishlatiladi.
- Model availability, narx va limitlar o'zgarishi sabab konfiguratsiya
  mustaqil bo'lishi shart.

### 10.3. Ishonchlilik qoidalari

- JSON Schema yoki typed serializer validatsiyasi.
- Temperature past qiymatda (0.1–0.3, task turiga qarab).
- Prompt va schema versiyalanadi (`prompt_v`, `schema_v` maydonlari).
- Provider timeout bo'lsa task `analysis_status = FAILED` bo'ladi.
  Foydalanuvchiga xato holati ko'rsatiladi va retry tugmasi beriladi.
- **Production'da soxta muvaffaqiyatli mock natija qaytarilmaydi.**
  `except` blokida `analysis_status = COMPLETED` berish **man etiladi**.
  Faqat `FAILED` va aniq xato xabari qaytariladi.
- Fallback boshqa providerga o'tishi mumkin (Gemini → Groq), lekin
  bu `ModelInvocation` audit jadvalida yoziladi.
- Yetarli evidence bo'lmasa model xulosa bermasligi kerak —
  `confidence < 0.3` bo'lgan finding "Tasdiqlangan emas" deb belgilanadi.
- LLM hisoblagan moliyaviy raqamlar yakuniy manba hisoblanmaydi —
  kalkulyator faqat backend formulasi orqali ishlaydi.

### 10.4. Quality Evaluation

Kamida 100 ta ekspert tomonidan belgilangan tenderdan eval dataset tuziladi.

O'lchovlar:

| Metrik | Maqsad |
|--------|--------|
| Red flag precision | ≥ 80% |
| Red flag recall | ≥ 70% |
| Hujjat talablari extraction accuracy | ≥ 75% |
| Citation correctness | ≥ 85% |
| JSON validity | 100% (schema validation) |
| O'zbek tili tushunarliligi | Ekspert baho ≥ 4/5 |
| False positive rate | ≤ 15% |
| Provider narx (per analysis) | ≤ $0.01 |
| P95 latency (per analysis) | ≤ 15 soniya |

Model yoki prompt production'ga faqat oldingi versiyadan yomonlashmagan
eval natijasi bilan chiqariladi.

### 10.5. AI xavfsizligi

- Prompt injection: hujjat ichidagi ko'rsatma system prompt sifatida
  bajarilmaydi. System va user prompt qat'iy ajratiladi.
- PII va secretlar modelga zarur bo'lmasa yuborilmaydi.
  Masalan, STIR va bank rekvizitlari tahlil uchun kerak emas.
- Chat tool'lari allowlist bilan cheklanadi.
- AI hech qachon to'lov, subscription yoki ruxsatni bevosita o'zgartirmaydi.
- Prompt va natijalar `ModelInvocation` jadvalida saqlanadi (audit uchun),
  lekin PII filtrlangan holda.

### 10.6. AI Document Generator va Inline Editor

Document Generator faqat aktiv Business/Enterprise subscription va STIR
mavjud kompaniya uchun ishlaydi. Company membership roli kamida `manager`
bo'lishi kerak; `viewer` hujjatni faqat o'qiydi.

Qo'llab-quvvatlanadigan boshlang'ich hujjatlar:

- tenderda qatnashish arizasi;
- kafolat xati;
- tijorat taklifi;
- texnik muvofiqlik xati;
- erkin shakldagi tenderga oid rasmiy xat.

Generation pipeline:

```text
Template + company snapshot + tender facts + user instructions
    -> typed AI generation
    -> policy/schema validation
    -> sanitized HTML draft
    -> inline editor
    -> version save
    -> PDF/DOCX export
```

Company context faqat zarur maydonlardan tuziladi:

- STIR;
- kompaniya nomi;
- rahbar F.I.Sh.;
- yuridik manzil;
- tashkiliy shakl;
- tender loti rekvizitlari.

Talablar:

- template versiyalanadi va aktiv versiya alohida belgilanadi;
- generatsiya vaqtida company/tender context snapshot saqlanadi;
- AI yaratgan matn `draft` statusida bo'ladi va avtomatik topshirilmaydi;
- foydalanuvchi Rich Text Editor orqali inline tahrirlaydi;
- backend HTML allowlist orqali sanitizatsiya qiladi;
- autosave va optimistic locking uchun `updated_at`/version tekshiruvi;
- har bir generatsiya va export audit logga yoziladi;
- hujjat foydalanuvchi tasdig'isiz `approved` yoki `exported` bo'lmaydi;
- generatsiya xatosi soxta hujjat bilan almashtirilmaydi;
- mualliflik yoki tashqi shablon matni ruxsatsiz ko'chirilmaydi; shablonlar
  ichki ishlab chiqilgan yoki litsenziyalangan bo'lishi shart.

---

## 11. Match Score va Tavsiya Mexanizmi

MVP score deterministic bo'ladi:

| Faktor | Boshlang'ich vazn | Izoh |
|---|---:|---|
| Soha/category mosligi | 40% | Kompaniya industry ↔ tender category |
| Keyword va mahsulot mosligi | 25% | Kompaniya profili ↔ lot matn tahlili |
| Hudud | 15% | Kompaniya viloyati ↔ tender joyi |
| Tender summasi va kompaniya imkoniyati | 10% | Narx diapazoni mosligi |
| Tajriba va sertifikatlar | 10% | ISO, GOST, litsenziya mavjudligi |

Vaznlar real foydalanuvchi va tender ma'lumotida kalibrlanadi.
Boshlang'ich qiymatlar faqat starting point hisoblanadi.

Talablar:

- score izohlanadigan bo'lishi — har bir faktor alohida ko'rsatilishi;
- foydalanuvchi noto'g'ri tavsiyani feedback qilishi;
- notification threshold (default 80%) foydalanuvchi tomonidan sozlanishi;
- `match_score` (deterministic) va `eligibility_score` (AI-generated)
  bir xil tushuncha sifatida **aralashtirilmasligi**:
  - `match_score` — kompaniya profili va lot metadata bo'yicha hisoblangan;
  - `eligibility_score` — AI tahlili natijasi, hujjat va shartlarni o'qib chiqadi.

### 11.1. Competitor Intelligence

Competitor Intelligence Business/Enterprise tariflar uchun yakunlangan
tenderlarning ochiq natijalaridan statistik dashboard yaratadi.

Asosiy metrikalar:

- lot yoki kategoriya bo'yicha TOP raqobatchilar;
- ishtiroklar soni;
- g'alabalar soni;
- win rate;
- o'rtacha taklif summasi;
- boshlang'ich narxdan o'rtacha demping foizi;
- hisoblangan davr va ma'lumot manbalari soni.

Demping formulasi:

```text
discount_percent = ((start_price - winning_bid) / start_price) * 100
```

Faqat `start_price > 0` va tasdiqlangan winning bid mavjud natijalar
agregatsiyaga kiradi. Manfiy yoki 100% dan yuqori qiymatlar data-quality
tekshiruviga yuboriladi.

Dashboard:

- tanlangan lot uchun o'xshash kategoriya TOP raqobatchilari;
- kategoriya va davr filtrlari;
- rank, win rate va average discount;
- oxirgi yangilanish va data freshness;
- yetarli sample bo'lmasa `insufficient_data` holati.

Bu statistik tahlil noqonuniy kelishuv yoki g'alaba kafolatini anglatmaydi.
Har bir ko'rsatkich ochiq tarixiy ma'lumotga asoslangan estimate sifatida
ko'rsatiladi.

---

## 12. Smart Calculator

Moliyaviy hisob faqat backenddagi versiyalangan servisda bajariladi.
Frontend faqat input va backend natijasini ko'rsatadi.

### 12.1. Inputlar

- xomashyo yoki mahsulot tannarxi;
- logistika xarajatlari;
- ish haqi va qo'shimcha xarajatlar;
- QQS holati (kompaniyaga bog'liq);
- platforma va xarid turi;
- zakalat/kafolat summasi;
- maqsad foyda marjasi;
- kutiladigan taklif narxi.

### 12.2. Muhim qarorlar

- **QQS:** Har bir kompaniyaga bir xil qo'llanmaydi.
  QQS holati `CompanyProfile.has_vat` maydonidan olinadi.
  `settings.py` dagi `VAT_RATE = 0.12` faqat standart stavka.
  QQS hisobi kalkulyator servisida kompaniya holati asosida amalga oshiriladi.

- **Operator komissiyasi:** Platforma va amaldagi tarifga bog'liq.
  Yagona global `OPERATOR_FEE_RATE` o'rniga platforma-specific konfiguratsiya:

  ```python
  OPERATOR_FEES = {
      'xarid_uzex': {'rate': 0.0015, 'min': 0, 'max': None, 'effective_date': '2026-01-01'},
      'dxarid_uzex': {'rate': 0.002, 'min': 0, 'max': None, 'effective_date': '2026-01-01'},
      'e_auksion': {'rate': 0.001, 'min': 0, 'max': None, 'effective_date': '2026-01-01'},
  }
  ```

- **Zakalat:** Qaytariladigan pul bo'lishi mumkin. Uni xarajat va cash-flow
  talabidan alohida ko'rsatish kerak. Kalkulyator natijasida `zakalat_amount`
  alohida maydon, `net_cost` ga qo'shilmaydi.

- **Formula versiyalash:** Har bir kalkulyator formulasi `formula_version`
  maydoni bilan saqlanadi. Formula o'zgarganda eski natijalar qayta
  hisoblanmaydi, lekin yangi versiya haqida foydalanuvchiga xabar beriladi.

- **Tasdiqlash:** Formula huquqshunos yoki moliyachi tomonidan tasdiqlanadi.
  Tasdiqlash sanasi va shaxsi ADR-005 da hujjatlanadi.

### 12.3. Natijalar

| Natija | Izoh |
|--------|------|
| Ishlab chiqarish tannarxi | Xomashyo + logistika + ish haqi |
| Majburiy xarajatlar | QQS + operator komissiya + zakalat |
| Cash requirement | Zakalat (qaytariladigan) + boshqa oldindan to'lovlar |
| Break-even narx | Tannarx + majburiy xarajatlar |
| Stop-loss narx | Break-even dan past — qatnashish tavsiya etilmaydi |
| Tavsiya narx diapazoni | Break-even + maqsad marja |
| Sof foyda va marja | Taklif narxi — tannarx — xarajatlar |
| Formula versiyasi | `v1.0`, `v1.1` ... |

---

## 13. Telegram Ekotizimi

### 13.1. Bot

- Aiogram 3.x.
- VPS ichida long polling (`dp.start_polling()`).
- systemd yoki Docker container service sifatida ishga tushiriladi.
- Foydalanuvchini xavfsiz account linking orqali bog'lash:
  Backend bir martalik `linking_code` beradi, foydalanuvchi botga yuboradi.
- Notification preference va unsubscribe (`/settings`, `/stop`).

### 13.2. Mini App

- Mavjud React PWA qayta ishlatiladi (alohida Mini App codebase yozilmaydi).
- Telegram `initData` backendda HMAC-SHA256 imzo bilan tekshiriladi.
- `initData` verification'dan keyin backend standart JWT token beradi
  (access + refresh). Mini App sessiyasi JWT lifetime'ga bog'liq.
- `start_param` lotga deep link uchun ishlatiladi.

#### Deep Link strategiyasi

- `start_param` Telegram tomonidan **64 belgi** bilan cheklangan.
  `lot_id` UUID (36 belgi) bo'lganligi sababli `base62(lot_id)` encoding
  ishlatiladi (max 22 belgi).
- HTTPS fallback URL: `https://tender-helper.uz/t/{base62_lot_id}`
  — Telegram Mini App ishlamagan holatda ham lot sahifasini ochadi.
- Bot `/start {base62_lot_id}` va Mini App `startapp={base62_lot_id}`
  parallel kelganda oxirgi sessiya ustuvor, lekin ikkala holat ham
  backend'da `NotificationDelivery` logiga yoziladi.

#### Edge case'lar

- `tg://` havolaga yagona tayanch bo'lmaydi — rasmiy HTTPS Mini App link
  fallback sifatida har doim mavjud.
- Android WebView'da `window.open()` cheklovlari mavjud — barcha
  navigatsiya `window.location.href` orqali amalga oshiriladi.

### 13.3. Notification

| Hodisa | Vaqt | Kanal |
|--------|------|-------|
| Yangi yuqori moslikdagi lot | Match score ≥ threshold | Telegram + Push |
| Deadline yaqinlashmoqda | 3 kun, 1 kun, 12 soat qolganda | Telegram |
| Tahlil yakunlandi | Darhol | Telegram + Push |
| To'lov/subscription holati | O'zgarganda | Telegram + Email |

Duplicate notification `idempotency_key` (`{event_type}:{entity_id}:{timestamp_bucket}`)
orqali oldini olinadi.

---

## 14. Billing va Huquqiy Poydevor

### 14.1. Tariflar

| Tarif | Imkoniyat | Narx (boshlang'ich) |
|---|---|---|
| Free | 4 ta AI tahlil/oy, asosiy qidiruv, kalkulyator | Bepul |
| Pro | Kengaytirilgan AI tahlil, filtrlar, notification | TBD (buxgalter bilan) |
| Business | Document Generator, inline editor, competitor intelligence, team | TBD |
| Enterprise | Business imkoniyatlari, yuqori limit, audit va priority support | TBD |

"Cheksiz" tariflar ham abuse va provider xarajatlari uchun fair-use limitiga
ega bo'ladi. Boshlang'ich fair-use: Pro — 100 tahlil/oy, Business — 250
tahlil/oy, Enterprise — 500 tahlil/oy. Limitlar real provider xarajatlari
asosida qayta kalibrlanadi.

Feature gating backend permission/service qatlamida bajariladi, faqat frontend
tugmasini yashirish bilan cheklanmaydi:

- Document Generator: Business/Enterprise + STIR + manager/owner;
- Competitor Intelligence: Business/Enterprise;
- team management: Business/Enterprise;
- katta export va audit: Enterprise.

### 14.2. Superadmin boshqaruvi

Superadmin tarif emas, platforma darajasidagi alohida ishonchli rol. U
Business yoki Enterprise obunasini sotib olmaydi va oddiy company membership
bilan cheklanmaydi. Superadmin paneli yangi parallel billing yoki analytics
backendini yaratmaydi; mavjud `users`, `companies`, `subscriptions`,
`payments`, `UsageRecord`, AI invocation, scraping va monitoring servislarini
bitta himoyalangan operatsion interfeysda boshqaradi.

#### Asosiy imkoniyatlar

| Modul | Superadmin amallari |
|---|---|
| Overview | user, company, active subscription, MRR, churn, AI usage, payment va system health statistikasi |
| Userlar | qidirish, profil/company ko'rish, aktiv/blok holati, session revoke, support context |
| Kompaniyalar | STIR/registry holati, a'zolar, tarif, usage, hujjat va tahlil agregatlari |
| Tariflar | Free/Pro/Business/Enterprise feature, limit, narx va visibility konfiguratsiyasi |
| Obunalar | activate, upgrade, downgrade, pause, cancel, expiry uzaytirish va entitlement preview |
| To'lovlar | transaction, webhook, reconciliation, refund review va failed payment retry holati |
| Business funksiyalar | Document Generator, competitor intelligence, team va export entitlement/usage nazorati |
| AI operatsiyasi | provider/model holati, token va xarajat, failure rate, feature kill switch |
| Tender pipeline | source, scrape run, freshness, retry/dead-letter va data-quality holati |
| Kontent | document template versionlarini publish/unpublish qilish |
| Support | user/company timeline, impersonation'siz read-only troubleshooting context |
| Audit | kim, qachon, nima sababdan, oldingi va yangi qiymat bilan barcha kritik amallar |
| System settings | feature flag, maintenance banner, rate/usage limit va notification template |

Tarif yoki obunaga admin override kiritilganda:

- mavjud subscription va entitlement service ishlatiladi;
- majburiy `reason` va ixtiyoriy support ticket/reference yoziladi;
- oldingi va yangi qiymat auditga tushadi;
- moliyaviy holat tarixdan o'chirilmaydi;
- webhook orqali tasdiqlangan payment yozuvi qo'lda tahrirlanmaydi;
- bulk action preview va explicit confirmation talab qiladi.

#### Real-time statistika

Dashboard yangilanishi WebSocket majburiyatini anglatmaydi. MVP'da 30-60
soniyalik polling va cache qilingan agregatlar yetarli; incident, payment yoki
queue alertlari tezroq kanal orqali yangilanadi. Ko'rsatiladigan vaqt oralig'i
`today`, `7d`, `30d`, `90d` va custom range:

- yangi/aktiv userlar, DAU/WAU/MAU;
- onboarding va STIR completion funnel;
- tariflar bo'yicha active/trial/expired/cancelled subscriptionlar;
- MRR, yangi revenue, failed payment, refund va churn;
- Business feature adoption va limit sarfi;
- AI request, token, provider cost, latency va failure rate;
- tender, scraping freshness, queue depth va API health.

Metrikada `updated_at`, timezone va data freshness ko'rinadi. Moliyaviy
statistika reconciliation qilingan transactionlardan olinadi; taxminiy va
tasdiqlangan qiymatlar aralashtirilmaydi.

#### Ruxsat va xavfsizlik

- superadmin route va API'lari `is_superuser`ning o'zi bilan cheklanmaydi:
  MFA, qayta autentifikatsiya va capability-based admin permission ishlatiladi;
- rollar: `support_viewer`, `billing_operator`, `operations_admin`,
  `content_admin`, `superadmin`;
- payment refund, subscription override, user block va feature kill switch
  kabi amallar step-up authentication talab qiladi;
- maxfiy maydonlar default maskalanadi, export va reveal auditlanadi;
- impersonation MVP'da yo'q; keyin qo'shilsa user roziligi, banner, vaqt
  limiti va to'liq audit majburiy;
- superadmin o'z audit yozuvini o'chira yoki tahrirlay olmaydi.

### 14.3. CLICK

CLICK API **v2** (Merchant API) ishlatiladi.

- Alohida endpointlar:
  - `POST /api/v1/payments/click/prepare/` — tranzaksiya tayyorlash.
  - `POST /api/v1/payments/click/complete/` — tranzaksiya yakunlash.

- **Prepare** va **Complete** action'lari alohida handler'lar bilan handle qilinadi.

- **Signature tekshiruvi:**
  ```
  MD5(click_trans_id + service_id + secret_key + merchant_trans_id
      + merchant_prepare_id + amount + action + sign_time)
  ```

- **merchant_trans_id formati:** `sub_{subscription_id}_{unix_timestamp}`

- **IP whitelist:** CLICK webhook faqat ruxsat etilgan IP'lardan qabul qilinadi.
  IP ro'yxati `CLICK_ALLOWED_IPS` environment variable'da saqlanadi.

- **Error kodlar mapping:**

  | Kod | Ma'nosi | Backend harakati |
  |-----|---------|-----------------|
  | `0` | Muvaffaqiyat | Tranzaksiya tasdiqlash |
  | `-1` | SIGN_CHECK xatosi | 403 qaytarish, alert |
  | `-2` | Noto'g'ri summa | Tranzaksiya rad etish |
  | `-4` | Allaqachon to'langan | Idempotent javob |
  | `-5` | Buyurtma topilmadi | 404 qaytarish |
  | `-9` | Tranzaksiya bekor qilingan | Subscription o'zgartirmaslik |

- **Idempotency:** `click_trans_id` + `action` juftligi `WebhookEvent`
  jadvalida unique. Takroriy webhook xuddi shu javobni qaytaradi.

- **Payment state machine:**
  ```
  PENDING → PREPARED → COMPLETED
                ↘ CANCELLED
                ↘ FAILED
  ```

- Client callback (redirect) subscriptionni **faollashtirmaydi** —
  faqat webhook orqali.

- **Replay attack himoyasi:** `sign_time` ning hozirgi vaqtdan 5 daqiqadan
  ko'p farqi bo'lsa webhook rad etiladi.

Payme va boshqa providerlar xuddi shu adapter pattern orqali keyin qo'shiladi.

### 14.4. Huquqiy masalalar

Biznes shakli va soliq rejimi professional buxgalter/yurist bilan
tasdiqlanadi.

#### Darhol tekshiriladigan huquqiy masalalar

| # | Masala | Sabab |
|---|--------|-------|
| 1 | Biznes shakli (YaTT vs MChJ) va SaaS daromad limitiga mosligi | YaTT yillik daromad limiti ~1 mlrd so'm (2026), Enterprise tarif oshishi mumkin |
| 2 | Shaxsiy ma'lumotlar inspeksiyasiga ro'yxatdan o'tish | "Shaxsiy ma'lumotlar to'g'risida" qonun (2019) talabi |
| 3 | AI disclaimer matnining O'zbekiston fuqarolik kodeksiga mosligi | AI maslahat javobgarligi hali rasmiy belgilanmagan |
| 4 | Portal ma'lumotlarini tijorat maqsadida qayta ishlash huquqi | UzEx ToS 7.3 va 8.1 bandlari |
| 5 | CLICK/Payme shartnoma talablari | Yuridik shaxs yoki YaTT talab etilishi |

#### Tayyorlanadigan hujjatlar

- Terms of Service (O'zbek va Rus tillarida);
- Privacy Policy (shaxsiy ma'lumotlar qonuniga mos);
- AI disclaimer (har bir tahlil natijasi bilan ko'rsatiladi);
- Data Processing Policy;
- Refund va subscription qoidalari;
- Portal scraping huquqiy bahosi (ADR-006).

---

## 15. API Standartlari

- `/api/v1/` versiyalash.
- OpenAPI 3.1 schema.
- Bir xil error envelope:

```json
{
  "code": "profile_required",
  "message": "Kompaniya profilini yarating",
  "details": {}
}
```

- Cursor yoki page pagination (default 20, max 100).
- Tender matnli qidiruvi `GET /api/v1/tenders/?search=<query>` orqali,
  Django `__icontains` va PostgreSQL `ILIKE` asosida bajariladi.
- Idempotency key: analysis start, payment va notification.
- Request ID (`X-Request-ID` header) va structured logging.
- UTC storage, UI'da `Asia/Tashkent`.
- API schema frontend CI bilan tekshiriladi (OpenAPI diff).

Asosiy endpoint guruhlari:

| Guruh | Asosiy endpointlar | Auth |
|-------|-------------------|------|
| `/auth/` | login, register, otp, google, refresh, logout | Aralash |
| `/companies/` | CRUD, members, onboarding | IsAuthenticated |
| `/companies/registry/` | STIR lookup, refresh, confirm draft | IsAuthenticated |
| `/tenders/` | list, detail, search, manual create | list=AllowAny, boshqasi=Auth |
| `/analyses/` | start, status, result, history | IsAuthenticated |
| `/documents/` | templates, generate, edit, versions, export | Business + STIR |
| `/calculator/` | calculate | IsAuthenticated |
| `/matches/` | list, feedback | IsAuthenticated |
| `/notifications/` | preferences, history | IsAuthenticated |
| `/subscriptions/` | plans, current, usage | IsAuthenticated |
| `/payments/` | click webhook, history | Webhook=IP whitelist |
| `/teams/` | members, tasks | Business/Enterprise + membership role |
| `/competitors/` | list, analytics | Business/Enterprise + membership |
| `/admin/overview/` | KPI, revenue, usage, health, freshness | Admin capability + MFA |
| `/admin/users/` | users, sessions, status, support timeline | Support/Admin capability |
| `/admin/companies/` | company, STIR, members, usage, entitlement | Support/Admin capability |
| `/admin/subscriptions/` | plans, overrides, lifecycle, usage | Billing capability + step-up |
| `/admin/payments/` | transactions, webhook, reconciliation, refund review | Billing capability + step-up |
| `/admin/operations/` | scraping, queues, AI provider, feature flags | Operations capability |
| `/admin/audit/` | immutable admin action history | Superadmin/Auditor |

---

## 16. Frontend UX

Asosiy ekranlar:

1. Landing va tariflar.
2. Login/register (email, OTP, Google).
3. Onboarding va company profile.
   STIR lookup, editable draft va `STIRsiz davom etish` oqimini o'z ichiga oladi.
4. Tender dashboard (qidiruv, filtrlar, ro'yxat).
5. Tender detail va hujjatlar.
6. AI analysis progress/result (real status, evidence, citation).
7. Calculator (input va natija).
8. Saved searches va watchlist.
9. Notification settings.
10. Billing va to'lov tarixi.
11. Business/Enterprise: team, competitors, audit va kengaytirilgan export.
12. Business Document Editor: template tanlash, AI generation, inline edit,
    autosave, preview va export.
13. Competitor Intelligence Dashboard: TOP raqobatchilar, g'alabalar va
    o'rtacha demping statistikasi.
14. Superadmin Console: platform overview, user/company, tarif-obuna,
    payment, Business usage, AI/scraping operatsiyasi va audit.

Talablar:

- mobile-first responsive dizayn;
- light/dark mode;
- keyboard navigation va ko'rinadigan focus state;
- loading, empty va error state har bir komponentda;
- foydalanuvchiga **haqiqiy** backend statusini ko'rsatish;
- soxta progress simulyatsiyasidan **foydalanmaslik** — agar AI tahlil
  10 soniya davom etsa, 10 soniya kutish ko'rsatiladi;
- Uzbek UI matnlarini toza UTF-8 saqlash;
- Vite template asset va matnlarini olib tashlash;
- Route-level lazy loading (React.lazy + Suspense).

---

## 17. Security Baseline

Production release bloklovchi talablar:

| # | Talab | Tekshiruv usuli |
|---|-------|----------------|
| 1 | `DEBUG=False` | `.env` va CI test |
| 2 | Kuchli `SECRET_KEY` (≥50 belgi, random) | CI secret scan |
| 3 | Aniq `ALLOWED_HOSTS` va CORS (wildcard yo'q) | Settings review |
| 4 | HTTPS va secure cookie | Nginx + Let's Encrypt |
| 5 | HSTS, CSP, X-Frame-Options headerlar | Middleware check |
| 6 | API secretlar environment/secret manager'da | `.env` + `.gitignore` |
| 7 | Loglarda token, OTP, parol va tender maxfiy hujjatlari **yo'q** | Log audit |
| 8 | OTP: secure random, rate limit (5/soat), 3 daqiqa expiry | Unit test |
| 9 | File upload: MIME check, 50MB limit, antivirus | Integration test |
| 10 | SQL/ORM ownership testlari | CI test suite |
| 11 | Dependency va secret scanning | `pip-audit` + `gitleaks` |
| 12 | Database backup va restore drill | Oylik |
| 13 | Admin uchun MFA | Django admin config |
| 14 | Audit log (admin harakatlari) | Middleware |
| 15 | `AllowAny` faqat ommaviy endpointlarda (CI test) | Custom CI check |
| 16 | `print()` debug yo'q — faqat `logging` moduli | Lint rule |
| 17 | Superadmin uchun MFA, capability permission va step-up auth | Security test |
| 18 | Admin kritik amallari immutable audit bilan | Audit integration test |

Xavfsizlik muammosi topilganda AI yoki billing funksiyasini feature flag bilan
tez o'chirish imkoniyati bo'ladi.

---

## 18. Observability va Operatsiya

Kuzatiladigan metrikalar:

| Kategoriya | Metrikalar |
|-----------|-----------|
| API | Request count, error rate (4xx/5xx), p95 latency |
| Celery | Queue depth, task failure rate, retry count |
| Scraping | Freshness, source error rate, lot count delta |
| AI | Provider latency, token usage, cost per analysis, JSON validation failure |
| Payment | Webhook success/failure rate, reconciliation delta |
| Notification | Delivery rate, duplicate rate |
| Database | Size, slow queries (>100ms), connection pool |
| Business | Plan distribution, feature adoption, limit usage, churn |
| Admin | Privileged action count, failed step-up, sensitive export/reveal |

Vositalar:

- structured JSON logs (Python `logging` + `json-log-formatter`);
- Sentry error tracking;
- Prometheus/Grafana yoki hosting monitoring;
- uptime check (external);
- alert routing (Telegram admin group yoki email).

Loglarda `request_id`, `user_id`, `company_id`, `task_id` va `analysis_id`
bo'lishi mumkin, lekin maxfiy payload (token, parol, OTP, API key)
**yozilmaydi**.

---

## 19. Testing va Quality Gates

### Backend

- model va service unit testlari;
- permission/ownership testlari (`IsAuthenticated` enforcement);
- auth integration testlari (email, OTP, Google, Telegram);
- scraper fixture/contract testlari;
- AI schema va provider mock testlari (mock ≠ soxta natija);
- calculator golden testlari (aniq raqamlar bilan);
- webhook signature va idempotency testlari;
- Celery retry va idempotency testlari;
- STIR registry adapter timeout/cache/normalization testlari;
- STIR skip va feature gate permission testlari;
- document template version va generated document ownership testlari;
- rich-text HTML sanitizatsiya va optimistic locking testlari;
- competitor aggregation, demping formula va insufficient-data testlari;
- superadmin capability, MFA/step-up va privilege escalation testlari;
- subscription override, payment safety va immutable audit testlari;
- dashboard metric formula/freshness testlari;
- **`AllowAny` audit testi** — barcha viewlarni skanlab, kutilmagan
  `AllowAny` topilsa test fail bo'ladi.

### Frontend

- Vitest + React Testing Library;
- kritik component testlari;
- API error va loading testlari;
- Playwright orqali login → onboarding → analysis → calculator E2E.
- Playwright orqali STIR lookup/skip, document editor va Business gate E2E.

### CI quality gate

| # | Check | Blocker? |
|---|-------|---------|
| 1 | Backend lint + format (ruff/black) | ✅ |
| 2 | Migration check (`makemigrations --check`) | ✅ |
| 3 | Backend test suite | ✅ |
| 4 | Frontend lint (ESLint) | ✅ |
| 5 | Frontend test suite | ✅ |
| 6 | Frontend production build | ✅ |
| 7 | Dependency audit (`pip-audit`, `npm audit`) | ⚠️ warning |
| 8 | Secret scan (`gitleaks`) | ✅ |
| 9 | OpenAPI compatibility check | ✅ |
| 10 | `AllowAny` audit | ✅ |

Coverage maqsadi:

- umumiy foizdan ko'ra kritik auth, ownership, billing va calculator
  oqimlarida branch coverage ustuvor;
- yangi core service testlarsiz merge qilinmaydi.

---

## 20. Deployment

### Muhitlar

| Muhit | Database | Redis | Secretlar | AI Provider |
|-------|----------|-------|-----------|------------|
| Local | SQLite | Optional | `.env` fayl | Gemini (bepul tier) |
| Staging | PostgreSQL | Redis | Environment vars | Gemini (bepul tier) |
| Production | PostgreSQL + pgvector | Redis | Secret manager | Gemini + Groq |

Har bir muhit alohida database, Redis va secretlarga ega.
**DEMO_MODE faqat local muhitda `True` bo'lishi mumkin.**

### Production

- Frontend: Vercel.
- Backend: Linux VPS (2 vCPU, 4GB RAM minimum).
- Nginx + HTTPS (Let's Encrypt).
- Docker Compose boshlang'ich deploy uchun.
- PostgreSQL va Redis private network/localhost.
- Celery worker, Celery Beat va Telegram bot alohida service/container.
- Zero-downtime migration imkon qadar expand/migrate/contract usulida.

Deploy checklist:

1. Database backup.
2. Migration plan review (breaking changes?).
3. CI green (barcha quality gates o'tgan).
4. Staging smoke test (login → analysis → calculator).
5. Rollback version tayyor.
6. Deploy va post-deploy monitoring (15 daqiqa).

---

## 21. Bosqichma-Bosqich Roadmap

### 21.1. Kritik funksiyalar uchun 4 haftalik ishchi reja

#### Hafta 1 — STIR onboarding

- [ ] `CompanyRegistryProvider` interfeysi va birinchi Soliq/Statistika adapteri.
- [ ] `CompanyProfile` registry, rahbar, manzil va skip maydonlari.
- [ ] STIR lookup cache, timeout va normalization.
- [ ] Editable draft confirm endpointi.
- [ ] `STIRsiz davom etish` va backend feature gate.
- [ ] Registry adapter va permission testlari.

**Hafta natijasi:** foydalanuvchi STIR orqali draft oladi yoki STIRsiz qo'lda
profil yaratib, cheklangan funksiyalar bilan tizimga kiradi.

#### Hafta 2 — AI Document Generator backend

- [ ] `TenderDocumentTemplate` va `GeneratedDocument` modellari/migratsiyasi.
- [ ] Template versioning va admin boshqaruvi.
- [ ] Company/tender context snapshot builder.
- [ ] Async generation service va typed output validation.
- [ ] Business + STIR + membership permission.
- [ ] Generate, retrieve, update va version API'lari.

**Hafta natijasi:** ruxsatli foydalanuvchi tender uchun xavfsiz draft hujjat
yaratadi va backendda saqlaydi.

#### Hafta 3 — Inline Editor va export

- [ ] Rich Text Editor integratsiyasi.
- [ ] HTML sanitizatsiya allowlist.
- [ ] Autosave va optimistic locking.
- [ ] Preview, DOCX/PDF export.
- [ ] User approval va audit trail.
- [ ] Frontend component va E2E testlar.

**Hafta natijasi:** draft platforma ichida tahrirlanadi, tasdiqlanadi va
eksport qilinadi.

#### Hafta 4 — Competitor Intelligence

- [ ] Yakunlangan tender participant/winner normalizatsiyasi.
- [ ] `CompetitorAnalytics` modeli va aggregation task.
- [ ] Rank, win rate va average discount hisoblari.
- [ ] Lot/category/period API.
- [ ] Business dashboard va freshness holati.
- [ ] Data-quality va aggregation testlari.

**Hafta natijasi:** Business foydalanuvchi lot yoki kategoriya bo'yicha
tekshiriladigan TOP competitor statistikalarini ko'radi.

#### Superadmin planning track

- [ ] Superadmin information architecture va capability matrix.
- [ ] KPI/revenue/usage metric dictionary va freshness qoidalari.
- [ ] User/company support timeline va sensitive-data masking.
- [ ] Tarif, entitlement va subscription override state transitionlari.
- [ ] Payment/reconciliation amallari va step-up confirmation.
- [ ] AI, scraping, queue va feature flag operations paneli.
- [ ] Immutable admin audit va privileged-action alertlari.

**Natija:** mavjud Business/subscription va operatsion servislar ustidan
xavfsiz, auditlanadigan yagona control plane spetsifikatsiyasi tayyor bo'ladi.

### Bosqich 0 — Xavfsizlik stabilizatsiyasi va canonical plan

- [ ] Eski hujjatlarni `docs/archive/` ga ko'chirish.
- [ ] `analysis/views.py`: `AllowAny` → `IsAuthenticated` (barcha write endpointlar).
- [ ] `_current_company()`: `settings.DEMO_MODE` tekshiruvini qo'shish.
- [ ] Demo user lookupni mavjud `email`/`phone_number` identifikatori bilan
  ishlaydigan va productionda butunlay o'chadigan qilish.
- [ ] AI xatosida mock fallback → `analysis_status = FAILED` + xato xabari.
- [ ] `settings.py`: model nomlarini `GEMINI_MODEL_ANALYSIS`, `GROQ_MODEL_CHAT` ga o'tkazish.
- [ ] `views.py`: `settings.GEMINI_MODEL_ANALYSIS` ishlatish, URL'da hardcode olib tashlash.
- [ ] `print()` debug → `logging.debug()` ga o'tkazish.
- [ ] OTP generatsiyasini `secrets`ga o'tkazish; OTP qiymatini log va
  production console outputdan olib tashlash.
- [ ] `requirements.txt` ga `groq>=0.9,<1.0` qo'shish.
- [ ] OAuth callback: tokenni URL'dan chiqarish, one-time code oqimiga o'tish.
- [ ] Frontend private route guard'larni tiklash.
- [ ] Backend va frontend lint/test muhitini barqaror qilish.
- [ ] `.env.example`ga `DEMO_MODE=False` va target model settinglarini qo'shish.
- [ ] Kalkulyator formulasini tasdiqlash va yagona backend servisiga ko'chirish.
- [ ] `AllowAny` audit testini CI ga qo'shish.
- [ ] Mavjud testlarni soxta `COMPLETED` natijadan `FAILED`/provider mock
  contractiga o'tkazish va placeholder app testlarini real smoke testlar bilan
  almashtirish.

**Exit criteria:** kritik security finding yo'q, CI mavjud, auth va analysis
ownership testlari o'tadi, `AllowAny` audit testi green.

### Bosqich 1 — PostgreSQL, Redis, Celery va Docker

- [ ] PostgreSQL 16 konfiguratsiyasi va migratsiya.
- [ ] pgvector extension o'rnatish va `vector(768)` column qo'shish.
- [ ] `pg_trgm` extension va tender LIKE qidiruvi uchun GIN indekslar.
- [ ] Redis va Celery worker/beat setup.
- [ ] Docker Compose (backend, worker, beat, redis, postgres).
- [ ] Environment-specific settings (`local`, `staging`, `production`).
- [ ] Core modellarni yangi schema bo'yicha migratsiya qilish.
- [ ] `CompanyProfile.user` ownershipini `CompanyMember`ga migrate qilish.
- [ ] Tender identity'ni `TenderSource + external_id` unique contractiga
  migrate qilish va eski `lot_number`ni business field sifatida saqlash.
- [ ] S3-compatible object storage abstraction.
- [ ] Structured logging (`json-log-formatter`) va Sentry.

**Exit criteria:** stagingda API, worker va beat barqaror ishlaydi,
PostgreSQL + pgvector ishlaydi.

### Bosqich 2 — Real data aggregation

- [ ] Portal huquqiy/texnik tekshiruvi (ADR-006).
- [ ] Source adapter interfeysi (`BaseSourceAdapter`).
- [ ] `xarid.uzex.uz` birinchi real portal integratsiyasi.
- [ ] `ILIKE` qidiruvini title, buyer, lot number va category bo'yicha
  `EXPLAIN ANALYZE` bilan benchmark qilish.
- [ ] `ScrapeRun` monitoring va admin dashboard.
- [ ] Document download, parsing va OCR pipeline.
- [ ] Yakunlangan tenderlar, participantlar va winning bid ingestion.
- [ ] Duplicate/upsert testlari.
- [ ] Dead-letter queue va failed task monitoring.

**Exit criteria:** kamida bir portal real lotlarni avtomatik va kuzatiladigan
tarzda yangilaydi, freshness SLO bajariladi.

### Bosqich 3 — Ishonchli AI va RAG

- [ ] `AIProviderInterface` va `GeminiAdapter`, `GroqAdapter`.
- [ ] Typed JSON schema validation (Pydantic yoki DRF serializer).
- [ ] Async analysis pipeline (Celery task).
- [ ] Embedding pipeline: chunk → embed → pgvector upsert.
- [ ] Semantic retrieval va rerank.
- [ ] `AnalysisFinding`, `AnalysisCitation` modellari.
- [ ] Prompt injection himoyasi.
- [ ] Eval dataset (100 ta tender) va baseline metrikalar.
- [ ] Provider fallback (Gemini → Groq) va cost monitoring.
- [ ] `ModelInvocation` audit logging.
- [ ] Versiyalangan `TenderDocumentTemplate` va async document generation.
- [ ] Generated document context snapshot va HTML sanitizatsiya.

**Exit criteria:** AI natijalari evidence bilan chiqadi, eval threshold'lardan
o'tadi, JSON validation 100%.

### Bosqich 4 — Product flow va recommendation

- [ ] To'liq onboarding: STIR lookup, editable draft va skip oqimi.
- [ ] Company profile va membership CRUD.
- [ ] Saved search/watchlist.
- [ ] Deterministic match score (5 faktor).
- [ ] User feedback mexanizmi.
- [ ] Real analysis progress (WebSocket yoki polling).
- [ ] Frontend test va code splitting.
- [ ] Rich Text Editor, autosave va document export.

**Exit criteria:** foydalanuvchi login'dan tavsiya va tahlilgacha to'liq oqimni
demo bypass'siz bajaradi.

### Bosqich 5 — Telegram

- [ ] Aiogram 3.x long polling bot.
- [ ] Account linking (one-time code).
- [ ] Mini App `initData` HMAC-SHA256 verification.
- [ ] Deep link: `base62(lot_id)` encoding.
- [ ] HTTPS fallback URL.
- [ ] Notification preferences (`/settings`, `/stop`).
- [ ] Deadline va match notification (idempotent).

**Exit criteria:** duplicate bo'lmagan xavfsiz notification va lot deep link
ishlaydi, Android va iOS'da Mini App sinab ko'rilgan.

### Bosqich 6 — Billing

- [ ] `SubscriptionPlan`, `CompanySubscription`, `UsageRecord` modellari.
- [ ] Fair-use va limit enforcement middleware.
- [ ] CLICK v2 adapter: prepare, complete, signature, IP whitelist.
- [ ] Payment state machine va idempotency.
- [ ] `WebhookEvent` audit log.
- [ ] Billing UI (tarif tanlash, to'lov tarixi).
- [ ] Refund va legal hujjatlar.
- [ ] Reconciliation: webhook vs backend holati kunlik tekshiruv.

**Exit criteria:** test va production CLICK oqimi reconciliation bilan
tekshirilgan, subscription lifecycle to'liq ishlaydi.

### Bosqich 6.1 — Superadmin Console

- [ ] Alohida `/superadmin/` layout va capability-based route guard.
- [ ] Real-time overview: growth, revenue, subscription, usage va health.
- [ ] User/company qidiruvi, support timeline va account controls.
- [ ] Tarif/feature/limit konfiguratsiyasi va entitlement preview.
- [ ] Subscription lifecycle va xavfsiz manual override.
- [ ] Payment, webhook va reconciliation operatsiyalari.
- [ ] Business feature usage, AI cost va scraping operations.
- [ ] Template publish/unpublish va system feature flags.
- [ ] Immutable admin audit, MFA va step-up authentication.

**Exit criteria:** superadmin barcha platforma operatsiyalarini mavjud domain
servislari orqali boshqaradi; kritik action sababsiz yoki auditsiz bajarilmaydi.

### Bosqich 7 — Business Intelligence va Enterprise

- [ ] Team membership va role (owner, manager, analyst, viewer).
- [ ] Task board (lot bo'yicha vazifalar).
- [ ] MVP competitor dataset va completed tender ingestion'ni kengaytirish.
- [ ] Lot/category/period kesimidagi advanced `CompetitorAnalytics`.
- [ ] Business dashboardga trend, comparison va export qo'shish.
- [ ] Enterprise permission va audit.

---

## 22. MVP Scope

MVP ichiga kiradi:

- auth va company profile;
- STIR registry lookup, editable onboarding draft va skip/feature gating;
- bitta real tender source (`xarid.uzex.uz`);
- PostgreSQL `ILIKE`/Django `__icontains` asosidagi tez qidiruv,
  `pg_trgm` GIN indekslari va asosiy filtrlar;
- hujjat parsing (PDF, DOCX);
- evidence va citation bilan AI tahlil;
- backend calculator (versiyalangan formula);
- deterministic match score;
- Business tarif uchun AI document generator va inline editor;
- yakunlangan tenderlar asosidagi competitor analytics;
- Telegram notification (lot va deadline);
- Free va Pro usage tracking;
- superadminning user/company, tarif-obuna, payment, usage, AI/scraping
  monitoringi va auditlangan boshqaruv paneli;
- staging va production monitoring.

MVP'dan tashqarida:

- barcha portallarni birdan integratsiya qilish;
- to'liq competitor intelligence;
- murakkab team workflow;
- OneID;
- mobil native app;
- AI tomonidan avtomatik huquqiy hujjat topshirish.

---

## 23. KPI va SLO

### Mahsulot KPI

| KPI | Maqsad (6 oy) |
|-----|--------------|
| Onboarding completion rate | ≥ 70% |
| Birinchi tahlilgacha vaqt | ≤ 10 daqiqa |
| Haftalik faol foydalanuvchi (WAU) | ≥ 200 |
| Notification open rate | ≥ 40% |
| Tahlildan keyingi save/watch action | ≥ 30% |
| Free → Pro conversion | ≥ 5% |
| Monthly churn | ≤ 10% |
| Business feature adoption | ≥ 30% active Business company |
| Admin critical action audit coverage | 100% |

### Texnik SLO

| SLO | Maqsad |
|-----|--------|
| API availability | 99.5% (MVP) |
| Oddiy API p95 latency | ≤ 500 ms |
| Tender LIKE qidiruv p95 | ≤ 300 ms (100 ming lotgacha) |
| AI task completion p95 | ≤ 15 soniya (hujjat hajmiga qarab) |
| Yangi lot freshness | ≤ 45 daqiqa |
| Payment webhook success | 99.9% |
| Backup restore | Oylik drill |
| Scraper error detection | ≤ 5 daqiqa |
| Superadmin dashboard freshness | ≤ 60 soniya (operatsion), ≤ 5 daqiqa (biznes agregat) |

---

## 24. Darhol Bajariladigan Backlog

Ustuvorlik bo'yicha tartibda:

| # | Vazifa | Ustuvorlik | Tegishli bo'lim |
|---|--------|-----------|-----------------|
| 1 | `analysis/views.py`: `AllowAny` → `IsAuthenticated` | 🔴 P0 | §7.3, §17 |
| 2 | `_current_company()`: demo bypass'ni `DEMO_MODE` ga bog'lash | 🔴 P0 | §4.3, §7.3 |
| 3 | AI xatosida `FAILED` status qaytarish, mock olib tashlash | 🔴 P0 | §4.1, §10.3 |
| 4 | Model nomini `settings.GEMINI_MODEL_ANALYSIS` env orqali boshqarish | 🟡 P1 | §10.2 |
| 5 | OAuth callback: one-time code oqimi | 🟡 P1 | §7.2 |
| 6 | Manual tender endpoint: `IsAuthenticated` + owner maydoni | 🟡 P1 | §7.3 |
| 7 | Calculator formula versiyalash va biznes tasdiqlash | 🟡 P1 | §12.2 |
| 8 | Frontend router auth guard'larini yoqish | 🟡 P1 | §16 |
| 9 | Onboardingni real `/companies/onboarding/` endpointiga ulash | 🟡 P1 | §16 |
| 10 | ESLint xatolarini yopish va frontend test runner qo'shish | 🟢 P2 | §19 |
| 11 | Python venv va backend CI yaratish | 🟢 P2 | §19 |
| 12 | PostgreSQL/Celery migratsiya uchun issue'lar ochish | 🟢 P2 | §20 |
| 13 | `requirements.txt` ga `groq`, `celery`, `redis` qo'shish | 🟢 P2 | §5.4, §10.2 |
| 14 | `print()` → `logging` migratsiyasi | 🟢 P2 | §4.3, §18 |
| 15 | LIKE qidiruv uchun `pg_trgm` + GIN indeks migration va benchmark | 🟢 P2 | §8.4 |
| 16 | STIR registry adapter, editable draft va skip feature gate | 🔴 P0 | §7.4 |
| 17 | Document template/generated document backend va Business gate | 🟡 P1 | §10.6 |
| 18 | Completed tender competitor aggregation va dashboard API | 🟡 P1 | §11.1 |
| 19 | Superadmin capability matrix, dashboard va audit contract | 🔴 P0 | §14.2 |

---

## 25. Definition of Done

Vazifa bajarilgan hisoblanadi, agar:

- acceptance criteria bajarilgan;
- permission va error holatlari hisobga olingan;
- kerakli testlar yozilgan (unit + integration);
- lint, test va build o'tgan;
- migration rollback yoki compatibility ko'rib chiqilgan;
- monitoring/logging qo'shilgan;
- API yoki foydalanuvchi oqimi o'zgarsa hujjat yangilangan;
- demo va production xatti-harakati aralashtirilmagan;
- `AllowAny` audit testi o'tgan;
- code review bajarilgan.

---

## 26. Qarorlar Jurnali (ADR)

Muhim arxitektura qarorlari `docs/adr/` ichida ADR sifatida yuritiladi.

| ADR | Mavzu | Status |
|-----|-------|--------|
| ADR-001 | PostgreSQL va pgvector tanlovi | Qabul qilingan |
| ADR-002 | Celery/Redis async arxitekturasi | Qabul qilingan |
| ADR-003 | Browser token storage strategiyasi (HttpOnly cookie vs Bearer) | Muhokama |
| ADR-004 | AI provider gateway: LangChain'siz adapter pattern | Qabul qilingan |
| ADR-005 | Calculator formulasi va tasdiqlash jarayoni | Kutilmoqda |
| ADR-006 | Portal scraping huquqiy va texnik yondashuvi | Kutilmoqda |
| ADR-007 | Telegram Mini App authentication oqimi | Kutilmoqda |
| ADR-008 | Embedding model va pgvector konfiguratsiyasi | Qabul qilingan |
| ADR-009 | CLICK API v2 integratsiya protokoli | Kutilmoqda |
| ADR-010 | STIR registry provider, cache va user-confirmed draft | Qabul qilingan |
| ADR-011 | Document generator template/version/editor modeli | Kutilmoqda |
| ADR-012 | Competitor analytics aggregation va data quality | Kutilmoqda |
| ADR-013 | Superadmin capability, step-up auth va immutable audit | Kutilmoqda |

Ushbu `Plan.md` strategiyani belgilaydi. Implementatsiya tafsiloti ADR,
OpenAPI schema va issue trackerda yuritiladi.

---

## 27. Dependencies (requirements.txt roadmap)

Hozirgi va rejalashtirilgan Python dependencylar:

| Paket | Versiya | Bosqich | Maqsad |
|-------|---------|---------|--------|
| Django | ≥5.0 | Hozir | Web framework |
| djangorestframework | ≥3.15 | Hozir | REST API |
| djangorestframework-simplejwt | ≥5.3 | Hozir | JWT auth |
| django-cors-headers | ≥4.3 | Hozir | CORS |
| django-filter | ≥24.0 | Hozir | API filtering |
| python-dotenv | ≥1.0 | Hozir | Environment vars |
| requests | ≥2.31 | Hozir | HTTP client |
| google-auth | ≥2.29 | Hozir | Google OAuth |
| google-generativeai | ≥0.8 | Hozir | Gemini SDK |
| groq | ≥0.9 | Bosqich 0 | Groq SDK |
| psycopg2-binary | ≥2.9 | Bosqich 1 | PostgreSQL driver |
| pgvector | ≥0.3 | Bosqich 1 | pgvector Python client |
| celery[redis] | ≥5.4 | Bosqich 1 | Async tasks |
| redis | ≥5.0 | Bosqich 1 | Cache/broker |
| beautifulsoup4 | ≥4.12 | Bosqich 2 | HTML parsing |
| pdfplumber | ≥0.11 | Bosqich 2 | PDF parsing |
| python-docx | ≥1.1 | Bosqich 2 | DOCX parsing |
| bleach | ≥6.1 | Hafta 3 | Rich-text HTML sanitizatsiya |
| aiogram | ≥3.7 | Bosqich 5 | Telegram bot |
| sentry-sdk[django] | ≥2.0 | Bosqich 1 | Error tracking |
