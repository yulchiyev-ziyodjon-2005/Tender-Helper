# TenderHelper — UI/UX Dizayn Strukturasi va Ekranlar Spesifikatsiyasi

**Versiya:** 1.2
**Yangilangan:** 2026-06-14  
**Status:** Canonical dizayn hujjati — barcha frontend ishlanmalar uchun asosiy manba

---

## 1. Dizayn Tizimi (Design System)

### 1.1. Rang Palitasi

```css
/* Asosiy brendlash ranglari */
--primary-50:  #eef7ff;
--primary-100: #d9eeff;
--primary-200: #bbdeff;
--primary-300: #8ac8ff;
--primary-400: #52aaff;
--primary-500: #2d8fff;   /* Asosiy rang */
--primary-600: #1470f0;
--primary-700: #0d58d6;
--primary-800: #1147ae;
--primary-900: #143e89;

/* Accent — AI va tahlil elementlari */
--accent-400: #a78bfa;
--accent-500: #8b5cf6;   /* AI gradient */
--accent-600: #7c3aed;

/* Semantic ranglar */
--success:  #10b981;
--warning:  #f59e0b;
--error:    #ef4444;
--info:     #3b82f6;

/* Neytral — dark mode */
--surface-900: #0f172a;  /* Background asosiy */
--surface-800: #1e293b;  /* Card background */
--surface-700: #334155;  /* Border */
--surface-600: #475569;  /* Muted text */
--surface-400: #94a3b8;  /* Secondary text */
--surface-100: #f1f5f9;  /* Light mode background */
--surface-50:  #f8fafc;

/* Tarif ranglari */
--free-color:       #6b7280;  /* Kulrang */
--pro-color:        #2d8fff;  /* Ko'k */
--business-color:   #0f9f7f;  /* Yashil */
--enterprise-color: #8b5cf6;  /* Binafsha */
--admin-color:      #dc2626;  /* Privileged action */
```

### 1.2. Tipografiya

```css
/* Google Fonts: Inter */
--font-display: 'Inter', system-ui, sans-serif;

--text-xs:   0.75rem;   /* 12px — badge, caption */
--text-sm:   0.875rem;  /* 14px — secondary */
--text-base: 1rem;      /* 16px — body */
--text-lg:   1.125rem;  /* 18px — subtitle */
--text-xl:   1.25rem;   /* 20px — section title */
--text-2xl:  1.5rem;    /* 24px — card title */
--text-3xl:  1.875rem;  /* 30px — page title */
--text-4xl:  2.25rem;   /* 36px — hero */
--text-5xl:  3rem;      /* 48px — landing hero */
```

### 1.3. Komponent Kutubxonasi

| Komponent | Tavsif |
|-----------|--------|
| `<Button>` | Primary, Secondary, Ghost, Danger, Loading holatlari |
| `<Card>` | Elevated, Outlined, Glassmorphism variantlar |
| `<Badge>` | Free (kulrang), Pro (ko'k), Enterprise (binafsha), Status |
| `<Modal>` | Animated overlay, backdrop blur |
| `<Drawer>` | Mobile sidebar, right panel |
| `<Tooltip>` | Hover va focus trigger |
| `<Toast>` | Success, Error, Warning, Info — top-right |
| `<Skeleton>` | Loading placeholder — barcha card'larda |
| `<Avatar>` | Foydalanuvchi rasm yoki harflar monogrammasi |
| `<Progress>` | Linear va circular (AI tahlil uchun) |
| `<DataTable>` | Sort, filter, pagination bilan |
| `<Tabs>` | Underline va Pill variantlar |
| `<Stepper>` | Ro'yxatdan o'tish bosqichlari uchun |
| `<Alert>` | Inline xabar (success/error/warning) |
| `<SubscriptionGate>` | Tarif cheklovini ko'rsatuvchi wrapper |
| `<MetricCard>` | Value, trend, interval va freshness bilan KPI karta |
| `<AdminActionModal>` | Reason, impact preview va step-up confirmation |
| `<AuditTimeline>` | O'zgarmas admin action tarixini ko'rsatish |

### 1.4. Layout Printsiplari

- **Mobile-first:** 320px minimum. Breakpoints: sm 640px, md 768px, lg 1024px, xl 1280px.
- **Sidebar:** Desktop (270px fixed), Tablet (collapsible), Mobile (bottom sheet).
- **Max content width:** 1440px centered.
- **Grid:** 12-ustunli grid (desktop), 4-ustunli (mobile).
- **Spacing:** 4px base (4, 8, 12, 16, 20, 24, 32, 40, 48, 64, 80, 96px).

---

## 2. Autentifikatsiya Ekranlari

### 2.1. Kirish Sahifasi — `/login`

#### Vizual Tuzilma

```
┌─────────────────────────────────────────────────────────────┐
│  [Logo TenderHelper]                    [O'zbek ▼] [🌙 Dark]│
├────────────────────────┬────────────────────────────────────┤
│                        │                                     │
│   Animatsiyali         │    ╔═══════════════════════════╗   │
│   Background           │    ║   Tizimga kirish          ║   │
│   (tender grafikalari, │    ║                           ║   │
│   floating cards)      │    ║  [Google bilan kirish  🔵]║   │
│                        │    ║  ─────── yoki ──────      ║   │
│   Statistika:          │    ║                           ║   │
│   "12,000+ tender      │    ║  Email                    ║   │
│   tahlil qilindi"      │    ║  [________________]       ║   │
│                        │    ║                           ║   │
│                        │    ║  Parol           [👁 Ko'r]║   │
│                        │    ║  [________________]       ║   │
│                        │    ║                           ║   │
│                        │    ║  [✓] Meni eslab qol       ║   │
│                        │    ║                 [Parolni  ║   │
│                        │    ║                  unutdim?]║   │
│                        │    ║                           ║   │
│                        │    ║  [   Kirish →           ] ║   │
│                        │    ║                           ║   │
│                        │    ║  Hisobingiz yo'qmi?       ║   │
│                        │    ║  [Ro'yxatdan o'ting →]    ║   │
│                        │    ╚═══════════════════════════╝   │
└────────────────────────┴────────────────────────────────────┘
```

#### Elementlar Spesifikatsiyasi

| Element | Tavsif | Validatsiya |
|---------|--------|-------------|
| Google OAuth tugmasi | Google branding, beyaz background, shadow | — |
| Email field | `type="email"`, placeholder "email@company.uz" | RFC 5322 format |
| Parol field | `type="password"`, ko'rish tugmasi | Min 8 belgi |
| Meni eslab qol | Secure HttpOnly refresh session muddati; token localStorage'da saqlanmaydi | — |
| Kirish tugmasi | Loading spinner kirish vaqtida | — |
| Parolni unutdim | Modal yoki `/forgot-password` sahifasi | — |

#### Xato Holatlari

| Xato | Ko'rsatish usuli |
|------|-----------------|
| Noto'g'ri email/parol | Red border + "Email yoki parol noto'g'ri" inline xato |
| Hisob bloklanган | Modal: "Hisobingiz vaqtincha bloklangan. 15 daqiqa kutib ko'ring." |
| Server xatosi | Toast: "Tizimda muammo yuz berdi. Qayta urinib ko'ring." |
| Google xatosi | Toast: "Google orqali kirish muvaffaqiyatsiz." |

---

### 2.2. Ro'yxatdan O'tish — Ko'p Bosqichli Oqim

#### Umumiy Bosqichlar Oqimi

```
Bosqich 1     Bosqich 2      Bosqich 3        Bosqich 4
Hisob yarash → Tasdiqlash → Kompaniya profili → Tarif tanlash
```

Stepper komponenti yuqorida ko'rinadi, foydalanuvchi qaysi bosqichda ekanligi aniq.

---

#### BOSQICH 1 — Hisob Ma'lumotlari `/register`

```
┌──────────────────────────────────────────────────────────┐
│  [Logo]                              [Kirish →]          │
├──────────────────────────────────────────────────────────┤
│                                                          │
│   ●━━━━━○━━━━━○━━━━━○   (Stepper: 1-Hisob)              │
│                                                          │
│   Hisob yaratish                                         │
│   Tender olamiga xush kelibsiz!                          │
│                                                          │
│   [  Google bilan ro'yxatdan o'ting  🔵  ]               │
│   ─────────────── yoki ────────────────                  │
│                                                          │
│   To'liq ism va familiya *                               │
│   ┌─────────────────────────────────────────┐            │
│   │ Ism va Familiya                         │            │
│   └─────────────────────────────────────────┘            │
│                                                          │
│   Email manzil *                                         │
│   ┌─────────────────────────────────────────┐            │
│   │ email@company.uz                        │            │
│   └─────────────────────────────────────────┘            │
│                                                          │
│   Telefon raqam *                                        │
│   ┌──────┐ ┌───────────────────────────────┐            │
│   │ +998 │ │ 90 123 45 67                  │            │
│   └──────┘ └───────────────────────────────┘            │
│   ℹ️ SMS orqali tasdiqlash uchun kerak                    │
│                                                          │
│   Parol * [kuch ko'rsatkichi: ●●●○○ O'rta]               │
│   ┌─────────────────────────────────────────┐            │
│   │ ••••••••••••••                    [👁]  │            │
│   └─────────────────────────────────────────┘            │
│   ✓ 8+ belgi  ✓ Raqam  ✗ Maxsus belgi                   │
│                                                          │
│   Parolni tasdiqlash *                                   │
│   ┌─────────────────────────────────────────┐            │
│   │ ••••••••••••••                    [👁]  │            │
│   └─────────────────────────────────────────┘            │
│                                                          │
│   ☑ Foydalanish shartlari va Maxfiylik siyosatiga        │
│     roziman                                              │
│   ☑ AI tahlil natijalari maslahat emas, tushunaman       │
│                                                          │
│              [ Keyingisi → ]                             │
│                                                          │
│   Allaqachon hisobingiz bormi? [Kirish]                  │
└──────────────────────────────────────────────────────────┘
```

**Validatsiya qoidalari:**

| Maydon | Qoidalar |
|--------|----------|
| Ism | 2–100 belgi, faqat harflar va probel |
| Email | RFC 5322, real-time duplicate tekshiruv (500ms debounce) |
| Telefon | `+998 XX XXX XX XX` format, O'zbekiston raqami |
| Parol | Min 8 belgi, kamida 1 raqam, kuch ko'rsatkichi |
| Parol tasdiq | Aynan mos kelishi kerak |
| Shartlar | Majburiy — belgilanmasa "Keyingisi" tugmasi aktiv emas |

---

#### BOSQICH 2 — Telefon/Email Tasdiqlash `/register/verify`

```
┌──────────────────────────────────────────────────────────┐
│  ○━━━━━●━━━━━○━━━━━○   (Stepper: 2-Tasdiqlash)           │
│                                                          │
│   📱 Telefon raqamingizni tasdiqlang                     │
│                                                          │
│   +998 90 *** ** 67 raqamiga                             │
│   6 xonali kod yuborildi                                 │
│                                                          │
│   ┌──┐ ┌──┐ ┌──┐  ┌──┐ ┌──┐ ┌──┐                       │
│   │  │ │  │ │  │  │  │ │  │ │  │   ← OTP kiritish       │
│   └──┘ └──┘ └──┘  └──┘ └──┘ └──┘                       │
│          (Auto-focus, auto-advance)                      │
│                                                          │
│   Kod 2:47 da tugaydi [████████░░░░░░░]                  │
│                                                          │
│   Kod kelmadimi? [Qayta yuborish] (30s kutish)           │
│                                                          │
│   [← Orqaga]          [Tasdiqlash →]                    │
│                                                          │
│   ─────── yoki ──────────────────────                    │
│   Email orqali tasdiqlash [Email kodni yuborish]         │
└──────────────────────────────────────────────────────────┘
```

**OTP Spesifikatsiyasi:**
- 6 ta alohida input box, har biri 1 raqam
- Paste qilinsa avtomatik tarqaladi
- Auto-submit: 6 ta to'ldirilsa avtomatik yuboradi
- Xato: 3 marta noto'g'ri → 15 daqiqa bloklash
- Tugash: Qolgan vaqt progress bar bilan

---

#### BOSQICH 3 — Kompaniya Profili `/register/company`

Bu bosqich STIR kiritishni majburlamaydi. Foydalanuvchi STIR orqali registry
lookup qiladi yoki `STIRsiz davom etish`ni tanlab profilni qo'lda to'ldiradi.
Registry natijasi user tasdig'isiz yakuniy profilga yozilmaydi.

```
┌──────────────────────────────────────────────────────────┐
│  ○━━━━━○━━━━━●━━━━━○   (Stepper: 3-Kompaniya)            │
│                                                          │
│   🏢 Kompaniya ma'lumotlarini kiriting                   │
│   Bu ma'lumotlar tender tavsiyalarini moslaydi           │
│                                                          │
│   ┌─────────────────────────────────────────────────┐    │
│   │  Kompaniya nomi *                               │    │
│   │  [_______________________________________]      │    │
│   └─────────────────────────────────────────────────┘    │
│                                                          │
│   ┌──────────────────────┐ ┌────────────────────────┐   │
│   │  STIR (ixtiyoriy)    │ │  [Reyestrdan topish]     │   │
│   │  [_______________]   │ │  [STIRsiz davom etish]   │   │
│   └──────────────────────┘ └────────────────────────┘   │
│   ℹ️ 9 xonali soliq raqam; rasmiy hujjatlar uchun kerak │
│                                                          │
│   REGISTRY DRAFT                                         │
│   ✓ "Example MChJ" • Rahbar • Manzil • QQS              │
│   [Qiymatlarni tahrirlash] [Tasdiqlash]                  │
│                                                          │
│   Asosiy faoliyat sohasi *                              │
│   [IT va Dasturlash                                ▼]    │
│   (Kategoriya va tenderlarga ta'sir qiladi)              │
│                                                          │
│   Xizmat ko'rsatuvchi viloyat/shahar *                   │
│   [Toshkent shahri                                 ▼]    │
│                                                          │
│   QQS to'lovchimisiz?                                    │
│   ○ Ha, QQS to'lovchiman   ● Yo'q, QQS to'lovchi emasman│
│   ℹ️ Kalkulyator uchun muhim                             │
│                                                          │
│   Kompaniya tajribasi (ixtyoriy)                         │
│   ┌─────────────────────────────────────────────────┐    │
│   │  Qanday mahsulot/xizmat yetkazib berасиз?       │    │
│   │  [____________________________________]  0/500  │    │
│   └─────────────────────────────────────────────────┘    │
│                                                          │
│   Sertifikatlar va litsenziyalar (ixtyoriy)              │
│   [+ ISO 9001] [+ GOST] [+ Davlat litsenziyasi] [+ ...]  │
│                                                          │
│   [← Orqaga]         [Keyingisi: Tarif →]               │
│                                                          │
│   ⏭ [STIRsiz davom etish]                                │
│   (Tizim ochiladi, rasmiy document funksiyalari gated)   │
└──────────────────────────────────────────────────────────┘
```

Holatlar:

- lookup loading, ready, not-found, timeout va provider-unavailable;
- registry qiymati va user tahriri vizual farqlanadi;
- skip qilinganda yopiladigan funksiyalar ro'yxati ko'rsatiladi;
- STIR keyinroq company settings orqali qo'shilishi mumkin.

---

#### BOSQICH 4 — Tarif Tanlash `/register/plan`

```

Pricing grid desktopda Free, Pro, Business va Enterprise tariflarini
ko'rsatadi. Enterprise Business imkoniyatlarini meros oladi va yuqori limit,
audit hamda priority support bilan farqlanadi. Mobil ekranda kartalar
gorizontal carousel emas, vertikal comparison sifatida beriladi.
┌──────────────────────────────────────────────────────────┐
│  ○━━━━━○━━━━━○━━━━━●   (Stepper: 4-Tarif)                │
│                                                          │
│   🎯 Tarif tanlang                                       │
│   Istalgan vaqt o'zgartirishingiz mumkin                 │
│                                                          │
│   ┌───────────────┐ ┌─────────────────┐ ┌─────────────┐ │
│   │   🆓 BEPUL   │ │   ⚡ PRO        │ │ 🚀 BIZNES  │ │
│   │               │ │   TAVSIYA ⭐   │ │             │ │
│   │  0 so'm/oy   │ │  X so'm/oy     │ │  Y so'm/oy  │ │
│   │               │ │               │ │             │ │
│   │  ✓ 4 tahlil  │ │  ✓ Cheksiz    │ │  ✓ Cheksiz  │ │
│   │    /oy        │ │    tahlil      │ │    tahlil   │ │
│   │               │ │               │ │             │ │
│   │  ✓ Asosiy    │ │  ✓ Barcha     │ │  ✓ Barcha   │ │
│   │    qidiruv    │ │    filtrlar    │ │    filtrlar │ │
│   │               │ │               │ │             │ │
│   │  ✓ Kalkulyat │ │  ✓ Kalkulyat  │ │  ✓ Kalkulya │ │
│   │               │ │               │ │    tor      │ │
│   │  ✗ Telegram  │ │  ✓ Telegram   │ │  ✓ Telegram │ │
│   │               │ │    bildirish  │ │    bildirish│ │
│   │  ✗ Export    │ │  ✓ PDF/Excel  │ │  ✓ PDF/Excel│ │
│   │               │ │    export     │ │    export   │ │
│   │  ✗ Tarix     │ │  ✓ Tahlil    │ │  ✓ Tahlil   │ │
│   │               │ │    tarixi     │ │    tarixi   │ │
│   │  ✗ Jamoa     │ │  ✗ Jamoa     │ │  ✓ 5 nafar  │ │
│   │               │ │               │ │    jamoa    │ │
│   │  ✗ Raqobat   │ │  ✗ Raqobat   │ │  ✓ Raqobat  │ │
│   │    tahlili    │ │    tahlili    │ │    tahlili  │ │
│   │               │ │               │ │             │ │
│   │ [Bepul boshl]│ │ [Pro ni boshl]│ │ [Bog'lanish]│ │
│   └───────────────┘ └─────────────────┘ └─────────────┘ │
│                                                          │
│   ✅ Kredit karta kerak emas     ✅ Istalgan vaqt bekor  │
└──────────────────────────────────────────────────────────┘
```

---

#### BOSQICH YAKUNIY — Xush Kelibsiz Ekrani `/register/welcome`

```
┌──────────────────────────────────────────────────────────┐
│                                                          │
│                    🎉 Confetti animatsiya                │
│                                                          │
│              ✅ Hisob muvaffaqiyatli yaratildi!          │
│                                                          │
│   Salom, [Ism]!                                          │
│   TenderHelper oilasiga xush kelibsiz.                   │
│                                                          │
│   Keyingi qadamlar:                                      │
│   ┌──────────────────────────────────────────────────┐   │
│   │  1️⃣ Birinchi tenderni qidiring          [→]     │   │
│   │  2️⃣ Kompaniya profilingizni to'ldiring   [→]    │   │
│   │  3️⃣ Telegram botini ulang                [→]    │   │
│   └──────────────────────────────────────────────────┘   │
│                                                          │
│          [ 🚀 Dashboard ga o'tish ]                      │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

### 2.3. Parolni Tiklash Oqimi

**3 qadam:**
1. `/forgot-password` — Email kiriting → "Kod yuborildi" xabari
2. `/forgot-password/verify` — 6 xonali kod tasdiqlash (OTP bosqichi kabi)
3. `/forgot-password/new` — Yangi parol o'rnatish + kuch ko'rsatkichi

---

## 3. Asosiy Interfeys Layouti (Authenticated)

### 3.1. Global Layout Tuzilmasi

```
┌─────────────────────────────────────────────────────────────┐
│  HEADER (64px yopishqoq)                                    │
│  [≡ Menu] [🔷 TenderHelper]  [🔍 Qidiruv]  [🔔] [👤 Profil]│
├────────────┬────────────────────────────────────────────────┤
│            │                                                │
│  SIDEBAR   │         ASOSIY KONTENT                        │
│  (270px)   │                                                │
│            │  Breadcrumb: Dashboard > Tenderlar > ...       │
│  [nav]     │                                                │
│  [nav]     │  [Page Title]              [Asosiy harakat]    │
│  [nav]     │                                                │
│  [nav]     │  ┌──────────────────────────────────────────┐  │
│            │  │  Kontent maydoni                         │  │
│  ─────     │  │                                          │  │
│  Tarif     │  │                                          │  │
│  badge     │  │                                          │  │
│  [Upgrade] │  └──────────────────────────────────────────┘  │
│            │                                                │
└────────────┴────────────────────────────────────────────────┘
```

### 3.2. Sidebar Navigatsiya

```
┌────────────────────────────┐
│  🔷 TenderHelper           │
│                            │
│  📊 Dashboard              │
│  🔍 Tenderlar              │
│  📋 Tahlillarim            │
│  🧮 Kalkulyator            │
│  💾 Saqlangan              │
│  🔔 Bildirishnomalar       │
│                            │
│  ─── PRO / BIZNES ───      │
│  👥 Jamoa          [PRO🔒] │
│  🏆 Raqobatchilar  [BIZ🔒] │
│  📈 Hisobotlar     [PRO🔒] │
│  📤 Export         [PRO🔒] │
│                            │
│  ─── SOZLAMALAR ───        │
│  🏢 Kompaniya profili      │
│  💳 Obuna va to'lov        │
│  🤖 Telegram bot           │
│  ⚙️  Sozlamalar            │
│                            │
│  ━━━━━━━━━━━━━━━━━━━━━━    │
│  [🆓 BEPUL]                │
│  4 tahlildan 4 ta          │
│  ████████░░ 100%           │
│  [⚡ Pro ga o'ting]        │
└────────────────────────────┘
```

**Tarif cheklov ko'rsatish:**
- Pullik funksiyalar kerakli tarif bilan (`PRO`, `BUSINESS`, `ENTERPRISE`)
  badge va aniq upgrade action orqali ko'rsatiladi.
- Ustiga bosish → "Bu funksiya Pro tarifida mavjud" modal ochiladi
- Sidebar pastida tarif holati va qolgan limit progress bar'i

---

## 4. Dashboard — `/dashboard`

```
┌─────────────────────────────────────────────────────────────┐
│  Xayrli kun, [Ism]! 👋                  2026-yil 14-iyun    │
│                                                             │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌────┐ │
│  │  📋          │ │  ✅          │ │  💰          │ │ ⏰ │ │
│  │  Faol        │ │  Bugun yangi │ │  O'rtacha    │ │Dea │ │
│  │  tenderlar   │ │  tenderlar   │ │  moslik      │ │dli │ │
│  │              │ │              │ │  balli       │ │ne  │ │
│  │  1,247 ta    │ │  +43 ta      │ │  78%         │ │3   │ │
│  │  ↑ 5% (hafta)│ │              │ │              │ │kun │ │
│  └──────────────┘ └──────────────┘ └──────────────┘ └────┘ │
│                                                             │
│  ── Sizga mos yangi tenderlar ─────────────────────────── │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 🟢 IT xizmatlar  •  UzEx  •  Toshkent  •  250M so'm │  │
│  │ "Axborot tizimini modernizatsiya qilish"              │  │
│  │ Moslik: ████████░░ 82%    Deadline: 3 kun qoldi       │  │
│  │ [Tahlil qilish] [Saqlash ♥] [Ko'rish →]              │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 🔵 Qurilish  •  E-Auksion  •  Samarqand  •  1.2B    │  │
│  │ "Ko'prikning rekonstruksiya ishlari"                  │  │
│  │ Moslik: ██████░░░░ 61%    Deadline: 12 kun qoldi      │  │
│  │ [Tahlil qilish] [Saqlash ♥] [Ko'rish →]              │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ── So'nggi tahlillarim ──────────────────────────────── │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ ✅ COMPLETED  •  IT  •  10-iyun 2026                  │  │
│  │ "Dasturiy ta'minot yetkazib berish" — 92% moslik      │  │
│  │                                 [Ko'rish] [Qayta →]  │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ── Qolayotgan muhim deadline'lar ───────────────────────│  │
│  🔴 2 kun qoldi  •  Tibbiy uskunalar  •  "Shifoxona..."   │  │
│  🟡 5 kun qoldi  •  Mebel yetkazish   •  "Maktab uchi..." │  │
│                                         [Barchasi →]       │
└─────────────────────────────────────────────────────────────┘
```

---

## 5. Tenderlar Ro'yxati — `/tenders`

```
┌─────────────────────────────────────────────────────────────┐
│  Tenderlar                                 [+ Qo'lda kiritish]│
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 🔍 Tender yoki mahsulot nomini yozing...    [Izlash]│   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌───────────────────── FILTRLAR ─────────────────────┐    │
│  │ Platforma    Soha/Kategoriya  Narx diapazoni  Hudud│    │
│  │ [UzEx    ▼] [Barchasi      ▼] [0 – ∞      ] [≡ ▼] │    │
│  │                                                    │    │
│  │ Deadline         Status          Saralash          │    │
│  │ [∘ Istalgan]    [∘ Faol   ]     [Deadline  ▼]     │    │
│  │ [∘ 3 kun qoldi] [∘ Yopilgan]                      │    │
│  │ [∘ 1 hafta    ] [∘ Barchasi]   [Tozalash]  [Qo'lla]│    │
│  └────────────────────────────────────────────────────┘    │
│                                                             │
│  1,247 ta tender topildi  •  Saralash: Deadline bo'yicha   │
│                                   [≡ Ro'yxat] [⊞ Karta]   │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │          TENDER KARTA KOMPONENTI                     │  │
│  │                                                      │  │
│  │ 🟢 Faol          UzEx xarid      Toshkent viloyati   │  │
│  │                                                      │  │
│  │ Axborot tizimini modernizatsiya va texnik qo'llab-   │  │
│  │ quvvatlash xizmatlarini ko'rsatish (Lot №: 24110012) │  │
│  │                                                      │  │
│  │ 👤 Toshkent shahar hokimligi                         │  │
│  │ 💰 250,000,000 so'm              ⏰ 3 kun qoldi       │  │
│  │                                                      │  │
│  │ Sizning mosligingiz:                                 │  │
│  │ IT xizmatlar  ████████░░ 82%                         │  │
│  │                                                      │  │
│  │ [🔬 AI Tahlil] [♥ Saqlash] [📋 Hujjatlar] [↗ Ochish]│  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  [← 1  2  3  ... 62 →]   (20 ta sahifada)                  │
└─────────────────────────────────────────────────────────────┘
```

**Tarif cheklovlari ro'yxat sahifasida:**

| Funksiya | Free | Pro | Biznes |
|----------|------|-----|--------|
| Ko'rish | ✅ | ✅ | ✅ |
| Kengaytirilgan filtrlar | ✅ asosiy | ✅ to'liq | ✅ to'liq |
| Export (CSV/Excel) | ❌ | ✅ | ✅ |
| Tahlil sonlimi | 4/oy | ♾ | ♾ |
| Saqlash | ✅ 10 ta | ✅ cheksiz | ✅ cheksiz |

---

## 6. Tender Batafsil Sahifa — `/tenders/{id}`

```
┌─────────────────────────────────────────────────────────────┐
│  ← Orqaga  /  Tenderlar  /  Lot №24110012                  │
│                                                             │
│  ┌────────────────────────────────────┐ ┌────────────────┐ │
│  │  ASOSIY MA'LUMOTLAR                │ │  TII HARAKATI  │ │
│  │                                    │ │                │ │
│  │  Axborot tizimini modernizatsiya   │ │  Moslik: 82%   │ │
│  │  va texnik qo'llab-quvvatlash      │ │  ████████░░    │ │
│  │  xizmatlarini ko'rsatish           │ │                │ │
│  │                                    │ │  [🔬 AI Tahlil]│ │
│  │  📋 Lot raqami: 24110012           │ │  [🧮 Kalkulyat]│ │
│  │  👤 Buyurtmachi:                   │ │  [♥ Saqlash   ]│ │
│  │     Toshkent shahar hokimligi      │ │  [📤 Ulashish ]│ │
│  │  💰 Boshlang'ich narx: 250 mln so'm│ │                │ │
│  │  📅 E'lon qilingan: 01.06.2026     │ │  ⏰ Qoldi:     │ │
│  │  ⏰ Deadline:       14.06.2026     │ │  2 kun 14 soat │ │
│  │  📍 Hudud: Toshkent shahri         │ │  17 daqiqa     │ │
│  │  🏷️  Kategoriya: IT xizmatlar      │ │  (Taymer)      │ │
│  │  🌐 Platforma: UzEx xarid          │ │                │ │
│  │                                    │ │  [↗ UzEx da    │ │
│  └────────────────────────────────────┘ │   ochish]      │ │
│                                         └────────────────┘ │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  [📄 Texnik topshiriq] [📊 Shartlar] [📁 Hujjatlar]  │  │
│  │                                                      │  │
│  │  TEXNIK TOPSHIRIQ                                    │  │
│  │  ─────────────────────────────────────────           │  │
│  │  1. Loyihaning maqsadi va vazifalari...              │  │
│  │  2. Texnik talablar ro'yxati...                      │  │
│  │  3. Yetkazib berish shartlari...                     │  │
│  │  4. To'lov tartibi...                                │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  YUKLAB OLINADIGAN HUJJATLAR                         │  │
│  │  📄 Texnik topshiriq.pdf          2.3MB  [Yuklab ol] │  │
│  │  📄 Shartnoma loyihasi.docx       1.1MB  [Yuklab ol] │  │
│  │  📊 Smeta.xlsx                    856KB  [Yuklab ol] │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 7. AI Tahlil Sahifasi — `/analyses/{id}`

### 7.1. Tahlil Jarayoni (Progress)

```
┌─────────────────────────────────────────────────────────────┐
│  🔬 AI Tahlil amalga oshirilmoqda...                        │
│                                                             │
│  Lot №24110012 — Axborot tizimini modernizatsiya            │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  ✅ Hujjatlarni yuklab olish        3 ta hujjat     │   │
│  │  ✅ Matnni ajratish                 PDF, DOCX        │   │
│  │  ⏳ AI tahlil qilmoqda...                            │   │
│  │     ████████████░░░░░░░░░░░░  45%                    │   │
│  │  ○ Natijalarni formatlash                            │   │
│  │  ○ Moslik ballini hisoblash                          │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Bu jarayon 10-30 soniya davom etishi mumkin.               │
│  Sahifani yopmang.                                          │
│                                                             │
│  ℹ️ AI tahlil xulosalari huquqiy maslahat hisoblanmaydi.    │
└─────────────────────────────────────────────────────────────┘
```

### 7.2. Tahlil Natijasi

```
┌─────────────────────────────────────────────────────────────┐
│  ← Tenderga qaytish  /  Tahlil natijasi                    │
│                                                             │
│  📊 UMUMIY MOSLIK BALLI                                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         ╭──────────────────╮                         │  │
│  │         │       92%        │  Juda mos!              │  │
│  │         │  ████████████░░  │  Qatnashish tavsiya     │  │
│  │         │  Eligibility     │  etiladi                │  │
│  │         ╰──────────────────╯                         │  │
│  │                                                      │  │
│  │  Soha moslik: ████████░░ 80%    Narx moslik: ██████  │  │
│  │  Hudud moslik: ██████████ 100%  Tajriba: ████████    │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  [📋 Xulosa] [🚩 Xatarlar] [📄 Hujjatlar] [📐 Standartlar] │
│                            [✅ Talablar]   [💡 Tavsiyalar]  │
│                                                             │
│  ── 🚩 XATARLAR (RED FLAGS) ──────────────────────────────  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 🔴 BLOCKER  Yetkazib berish muddati qisqa            │  │
│  │ Manba: Texnik topshiriq.pdf, 3-bet, "Mahsulot..."    │  │
│  │ "10 kun ichida to'liq hajmda yetkazib berish"        │  │
│  │ → Logistika zanjiringizni avvaldan tayyorlang        │  │
│  │ Ishonchlilik: 94%                        [▲ Yashir]  │  │
│  ├──────────────────────────────────────────────────────┤  │
│  │ 🟡 WARNING  Bank kafolati talab qilingan             │  │
│  │ Manba: Shartnoma loyihasi.docx, 8-bet, "Kafolat..."  │  │
│  │ "Shartnoma summasining 10% bank kafolati..."         │  │
│  │ → Bank bilan oldindan muzokaralar olib boring         │  │
│  │ Ishonchlilik: 87%                        [▼ Ko'rsatish]│  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ── 📄 KERAKLI HUJJATLAR ─────────────────────────────────  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ ☐ Soliq qo'mitasidan ma'lumotnoma (oxirgi 3 oy)      │  │
│  │ ☐ ISO 9001 yoki ekvivalent sertifikat                │  │
│  │ ☐ Oxirgi 2 yillik moliyaviy hisobot                  │  │
│  │ ☑ Davlat ro'yxatidan o'tish guvohnomasi ✅            │  │
│  │ ☑ Kompaniya ustavi ✅                                 │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ── 💡 AI TAVSIYASI ──────────────────────────────────────  │
│  "Ushbu tender sizning soha profilingizga juda mos keladi.  │
│  Asosiy risklardan biri — yetkazib berish muddati qisqa.    │
│  Agar logistika imkoniyatlaringiz yetarli bo'lsa, qatnashing│  │
│  maqsadga muvofiq. Minimal narx taklifini kalkulyator orqali│  │
│  hisoblang."                                                │  │
│                                                             │
│  ⚠️ Bu xulosa AI tomonidan tayyorlangan va huquqiy maslahat  │
│  hisoblanmaydi. Qaror faqat kompaniya rahbariyatiga bog'liq.│  │
│                                                             │
│  [🧮 Kalkulyator] [📤 PDF sifatida yuklab olish PRO🔒]      │
└─────────────────────────────────────────────────────────────┘

### 7.3. Shaxsiy AI bilan Chat (Savol-Javob) — `/analyses/{id}/chat`

AI tahlil oynasida alohida "Chat" tab'i orqali tender bo'yicha Groq (Llama 3.3) bilan jonli muloqot qilish mumkin.

```
┌─────────────────────────────────────────────────────────────┐
│  [📋 Xulosa]  [💬 AI bilan Chat]  [📄 Hujjatlar]             │
│                                                             │
│  TENDER MENTOR AI (Groq Llama 3.3)                          │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  🤖 AI: Salom! Ushbu tender (Lot №24110012) bo'yicha        │
│  qanday savollaringiz bor? Hujjatlarning barchasi bilan     │
│  tanishib chiqdim.                                          │
│                                                             │
│  👤 Siz: "Texnik topshiriqda server parametrlari qanday     │
│  ko'rsatilgan?"                                             │
│                                                             │
│  🤖 AI: Texnik topshiriqning 4-betida quyidagicha keltiril- │
│  gan: "Kamida 32GB RAM va 1TB NVMe SSD". Lekin operatsion   │
│  tizim aniq yozilmagan. Buyurtmachiga so'rov yuborishni     │
│  tavsiya qilaman.                                           │
│  [📄 Manba: Texnik topshiriq.pdf, 4-bet]                    │
│                                                             │
│  👤 Siz: "Agar men 15 kunda yetkazib bersam bo'ladimi?"     │
│                                                             │
│  🤖 AI: Yo'q, shartnoma loyihasining 2.1-bandida aniq qilib │
│  "10 bank ish kuni ichida" deyilgan. 15 kun kechikish       │
│  jarimaga olib keladi (kuniga 0.5%).                        │
│                                                             │
│  ─────────────────────────────────────────────────────────  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ 💬 Savolingizni yozing...                       [▶]   │  │
│  └───────────────────────────────────────────────────────┘  │
│  Tezkor savollar:                                           │
│  [Jarimalar bormi?] [QQS qanday to'lanadi?]                 │
└─────────────────────────────────────────────────────────────┘
```
```

---

## 8. Kalkulyator — `/calculator`

Kompaniyaning shaxsiy obuna darajasiga mos (kompaniya xarajatlari, marja qoidalari o'zida saqlanadi).

```
┌─────────────────────────────────────────────────────────────┐
│  🧮 Aqlli Kalkulyator                                       │
│  (Lot №24110012 uchun, yoki mustaqil)                       │
│                                                             │
│  ┌─────────────────────────────┐ ┌────────────────────────┐ │
│  │  KIRITISH                   │ │  NATIJA                │ │
│  │                             │ │                        │ │
│  │  Mahsulot/xizmat tannarxi   │ │  Ishlab chiqarish      │ │
│  │  [_________________] so'm   │ │  tannarxi:             │ │
│  │                             │ │  125,000,000 so'm      │ │
│  │  Logistika xarajatlari      │ │                        │ │
│  │  [_________________] so'm   │ │  Majburiy xarajatlar:  │ │
│  │                             │ │  • QQS (12%): 15M      │ │
│  │  Ish haqi va boshqalar      │ │  • Komissiya: 188K     │ │
│  │  [_________________] so'm   │ │  • Zakalat (3%): 7.5M  │ │
│  │                             │ │                        │ │
│  │  QQS holati                 │ │  ─────────────────────  │ │
│  │  ○ QQS to'lovchiman         │ │  Break-even: 148M      │ │
│  │  ● QQS to'lovchi emasman    │ │  Stop-loss:  148M      │ │
│  │                             │ │                        │ │
│  │  Platforma                  │ │  Tavsiya narx:         │ │
│  │  [UzEx xarid          ▼]    │ │  175M – 200M so'm      │ │
│  │                             │ │                        │ │
│  │  Maqsad foyda marjasi       │ │  SOF FOYDA:            │ │
│  │  [____15___] %              │ │  🟢 27,000,000 so'm    │ │
│  │  [💾 Marjani profilga saqla]│ │  Marja: 15.4%          │ │
│  │                             │ │                        │ │
│  │  Zakalat: [__3__]%          │ │  Cash talab:           │ │
│  │  (Qaytariladigan)           │ │  7,500,000 so'm (oldin)│ │
│  │                             │ │                        │ │
│  │  [🔄 Hisoblash]             │ │  Formula v1.2          │ │
│  └─────────────────────────────┘ │  [ℹ️ Formula batafsil] │ │
│                                   └────────────────────────┘ │
│                                                             │
│  [📤 Excel sifatida saqlash  PRO🔒]  [🖨️ Chop etish PRO🔒]  │
└─────────────────────────────────────────────────────────────┘
```

---

## 9. Saqlangan va Kuzatish — `/saved`

```
┌─────────────────────────────────────────────────────────────┐
│  💾 Saqlangan va Kuzatish                                   │
│                                                             │
│  [💾 Saqlangan (12)] [👁 Kuzatish (5)] [🔍 Qidiruvlar (3)] │
│                                                             │
│  SAQLANGAN TENDERLAR                                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ ♥ Axborot tizimini modernizatsiya  •  UzEx  •  250M  │  │
│  │   Deadline: 3 kun qoldi                              │  │
│  │   [Ko'rish] [Tahlil] [♥ Olib tashlash]              │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  KUZATISH RO'YXATI                     [+ Kuzatishga qo'sh] │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 👁 Mebel yetkazib berish  •  UzEx  •  45M so'm       │  │
│  │   🔔 Deadline: 5 kun qolda xabar berish sozlangan    │  │
│  │   Status: Faol          [Sozlash 🔔] [Ko'rish]       │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  SAQLANGAN QIDIRUVLAR                                       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 🔍 "IT xizmatlar + Toshkent + 50M-500M"              │  │
│  │    Yangi natijalar: 3 ta                              │  │
│  │    [Yangilab ko'rish] [🔔 Bildirish sozlash] [×Ochir]│  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 9.5. Qo'lda Tender va Fayl Qo'shish (Upload) — Modal yoki `/tenders/new`

Tizimda yo'q bo'lgan, yoki xususiy korporativ tenderlarni qo'lda fayl yuklash orqali tahlil qilish interfeysi.

```
┌─────────────────────────────────────────────────────────────┐
│  📤 Yangi tender va fayllarni tahlil qilish                 │
│                                                             │
│  1. TENDER MA'LUMOTLARI                                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Tender/Loyiha nomi *                                │  │
│  │  [_______________________________________]           │  │
│  │                                                      │  │
│  │  Buyurtmachi            Boshlang'ich narx             │  │
│  │  [_______________]      [_______________] so'm       │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  2. HUJJATLARNI YUKLASH (PDF, DOCX)                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                                                      │  │
│  │       📁 Fayllarni shu yerga tashlang yoki           │  │
│  │                [Fayl tanlash]                        │  │
│  │                                                      │  │
│  │  Max: 50MB. Ruxsat etilgan formatlar: .pdf, .docx     │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  Yuklangan fayllar:                                         │
│  📄 Shartnoma_loyihasi.docx (1.2 MB)  [✅] [×]             │
│  📄 Texnik_topshiriq.pdf    (3.5 MB)  [✅] [×]             │
│                                                             │
│  [Bekor qilish]                     [Tahlilni boshlash 🚀]  │
└─────────────────────────────────────────────────────────────┘
```

---

## 10. Bildirishnomalar — `/notifications`

```
┌─────────────────────────────────────────────────────────────┐
│  🔔 Bildirishnomalar          [Barchasini o'qilgan deb belgi]│
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 🔵 YANGI  •  Az oldin                               │   │
│  │ Yangi mos tender: "IT xizmatlar..." — Moslik: 91%   │   │
│  │ [Ko'rish →]                                         │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 🔴  •  2 soat oldin                                 │   │
│  │ Deadline BUGUN: "Mebel yetkazish..." — 12 soat qoldi│   │
│  │ [Ko'rish →]                                         │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ ✅  •  Kecha                                         │   │
│  │ Tahlil yakunlandi: "Qurilish materiallari" 87%      │   │
│  │ [Natijani ko'rish →]                                │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ── Bildirishnoma Sozlamalari ─────────────────────────── │
│  [🤖 Telegram] [📧 Email] [📱 Push]                        │
│                                                             │
│  Yangi mos tender     [🔔 Telegram ✅] [📧 ○] [📱 ○]       │
│  Deadline eslatmasi   [🔔 Telegram ✅] [📧 ✅] [📱 ✅]     │
│  Tahlil yakunlandi    [🔔 Telegram ✅] [📧 ○] [📱 ✅]      │
│  To'lov/Obuna         [🔔 Telegram ✅] [📧 ✅] [📱 ○]      │
│                                                             │
│  Moslik chegarasi: [80  ] % dan yuqori tenderlar            │
└─────────────────────────────────────────────────────────────┘
```

---

## 11. Obuna va To'lov — `/billing`

```
┌─────────────────────────────────────────────────────────────┐
│  💳 Obuna va To'lov                                         │
│                                                             │
│  HOZIRGI TARIF                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  🆓 BEPUL TARIF                                      │  │
│  │                                                      │  │
│  │  AI Tahlil:  ████████████ 4/4 (Oy tugashiga 16 kun) │  │
│  │  Saqlangan:  ████░░░░░░░░ 10/10                     │  │
│  │                                                      │  │
│  │  [⚡ Pro ga o'tish]  [🚀 Biznes ga o'tish]          │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  TARIFLARNI SOLISHTIRISH                                    │
│                                                             │
│  [Oylik] [Yillik (-20%)]                                    │
│                                                             │
│  ┌────────────────┐ ┌────────────────┐ ┌────────────────┐  │
│  │  🆓 BEPUL     │ │  ⚡ PRO        │ │  🚀 BIZNES    │  │
│  │  0 so'm/oy    │ │  XXX so'm/oy   │ │  YYY so'm/oy  │  │
│  │               │ │                │ │                │  │
│  │  • 4 tahlil   │ │  • Cheksiz     │ │  • Cheksiz    │  │
│  │  • 10 saqlash │ │  • Cheksiz     │ │  • Cheksiz    │  │
│  │  • Kalkulyator│ │  • Kalkulyator │ │  • Kalkulyator│  │
│  │               │ │  • Telegram    │ │  • Telegram   │  │
│  │               │ │  • Export      │ │  • Export     │  │
│  │               │ │  • Tarix       │ │  • Tarix      │  │
│  │               │ │                │ │  • Jamoa (5)  │  │
│  │               │ │                │ │  • Raqobat    │  │
│  │               │ │                │ │  • API kirish │  │
│  │               │ │                │ │               │  │
│  │ Hozirgi ✅    │ │ [Sotib olish]  │ │ [Bog'lanish]  │  │
│  └────────────────┘ └────────────────┘ └────────────────┘  │
│                                                             │
│  TO'LOV TARIXI                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Sana        Tarif   Summa      Status               │  │
│  │  01.06.2026  Pro     X so'm     ✅ To'langan          │  │
│  │  01.05.2026  Pro     X so'm     ✅ To'langan          │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 11.1. To'lov Modal (CLICK)

```
┌──────────────────────────────────────────────────────────┐
│  💳 To'lovni amalga oshirish                              │
│                                                           │
│  Pro tarif — Oylik                                        │
│  Summa: XXX,000 so'm                                      │
│                                                           │
│  To'lov usulini tanlang:                                  │
│                                                           │
│  ┌────────────────┐ ┌────────────────┐ ┌──────────────┐  │
│  │  💳 CLICK     │ │  💳 Payme      │ │  🏦 Uzum     │  │
│  │               │ │                │ │              │  │
│  └────────────────┘ └────────────────┘ └──────────────┘  │
│                                                           │
│  [Bekor qilish]                   [To'lash →]            │
└──────────────────────────────────────────────────────────┘
```

---

## 12. Kompaniya Profili — `/settings/company`

```
┌─────────────────────────────────────────────────────────────┐
│  🏢 Kompaniya Profili                              [Saqlash] │
│                                                             │
│  [🏢 Asosiy] [👥 A'zolar] [📄 Hujjatlar] [⚙️ Sozlamalar]   │
│                                                             │
│  ASOSIY MA'LUMOTLAR                                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Kompaniya nomi *                                    │  │
│  │  [IT Solutions MCHJ                        ]         │  │
│  │                                                      │  │
│  │  STIR / Registry status                              │  │
│  │  [123456789] [Verified] [Reyestrni yangilash]        │  │
│  │                                                      │  │
│  │  Asosiy faoliyat sohasi *                            │  │
│  │  [IT va Dasturlash                          ▼]       │  │
│  │                                                      │  │
│  │  Xizmat ko'rsatiladigan viloyat/shahar *              │  │
│  │  [Toshkent shahri                           ▼]       │  │
│  │                                                      │  │
│  │  QQS holati                                          │  │
│  │  ○ Ha, QQS to'lovchiman  ● Yo'q, emasman             │  │
│  │                                                      │  │
│  │  Kompaniya tavsifi (ixtyoriy)                        │  │
│  │  [________________________________________] 0/500    │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  SERTIFIKATLAR VA LITSENZIYALAR                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  [× ISO 9001] [× GOST] [+ Qo'shish]                  │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  MOSLIK KALIT SO'ZLARI (Tender qidiruvda ishlatiladi)      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  [× dasturlash] [× IT xizmatlar] [× server]          │  │
│  │  [+ So'z qo'shish]                                   │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 13. Jamoa Bo'limi — `/team` (Business/Enterprise)

```
┌─────────────────────────────────────────────────────────────┐
│  👥 Jamoa boshqaruvi                           [+ Taklif et] │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  👤 Alisher Yusupov (Siz)       Owner    Faol        │  │
│  │  📧 alisher@company.uz                               │  │
│  ├──────────────────────────────────────────────────────┤  │
│  │  👤 Malika Rashidova             Manager  Faol       │  │
│  │  📧 malika@company.uz            [↓ Rol] [× Chiqar]  │  │
│  ├──────────────────────────────────────────────────────┤  │
│  │  👤 Jasur Mirzayev              Analyst  Faol        │  │
│  │  📧 jasur@company.uz             [↓ Rol] [× Chiqar]  │  │
│  ├──────────────────────────────────────────────────────┤  │
│  │  📧 bekzod@company.uz           Viewer   ⏳ Kutilmoqda│  │
│  │  (Taklif yuborilgan)                      [Qayta yub]│  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ROLLAR HUQUQLARI                                           │
│  ┌──────────────┬────────┬─────────┬─────────┬──────────┐  │
│  │ Funksiya     │ Owner  │ Manager │ Analyst │ Viewer   │  │
│  ├──────────────┼────────┼─────────┼─────────┼──────────┤  │
│  │ Ko'rish      │  ✅   │  ✅    │  ✅    │  ✅     │  │
│  │ Tahlil       │  ✅   │  ✅    │  ✅    │  ❌     │  │
│  │ Kalkulyator  │  ✅   │  ✅    │  ✅    │  ✅     │  │
│  │ Jamoa boshq. │  ✅   │  ✅    │  ❌    │  ❌     │  │
│  │ To'lov       │  ✅   │  ❌    │  ❌    │  ❌     │  │
│  └──────────────┴────────┴─────────┴─────────┴──────────┘  │
│                                                             │
│  JAMOA VAZIFALARI                                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  📌 Vazifa                  Kim?     Status  Muddati  │  │
│  │  Lot №241 hujjat yig'ish   Malika   🟡 Jaray  15-iyun│  │
│  │  Narx kalkulyatsiyasi       Jasur    ⬜ Boshlm  14-iyun│  │
│  │  [+ Yangi vazifa]                                    │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 14. Raqobatchilar Tahlili — `/competitors` (Business/Enterprise)

```
┌─────────────────────────────────────────────────────────────┐
│  🏆 TOP Raqobatchilar        Updated 12:30 • 47 source lot │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Kompaniya nomi     STIR         G'alaba %  Kuzatish │  │
│  │  ABC Systems MCHJ   123456789    34%        👁 [📊]   │  │
│  │  TechBuild LLC      987654321    28%        👁 [📊]   │  │
│  │  Yetarli data bo'lmasa: "insufficient data"           │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ABC SYSTEMS MCHJ — STATISTIKA                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Qatnashgan tenderlar: 47 ta                         │  │
│  │  G'alaba qozongan: 16 ta (34%)                       │  │
│  │                                                      │  │
│  │  Asosiy kategoriyalar:                               │  │
│  │  IT xizmatlar ████████████ 60%                       │  │
│  │  Qurilish      ████░░░░░░░ 25%                       │  │
│  │  Boshqa        ██░░░░░░░░░ 15%                       │  │
│  │                                                      │  │
│  │  O'rtacha narx taklifi:  -8% bozor o'rtachasidan     │  │
│  │  Eng ko'p g'alaba region: Toshkent (65%)             │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

Dashboard lot/category/period filterlariga ega. Rank, g'alaba, ishtirok,
win-rate, o'rtacha demping, sample size va `calculated_at` ko'rsatiladi.
Qo'lda competitor qo'shish MVP oqimiga kirmaydi; statistikalar yakunlangan
ochiq tender natijalaridan avtomatik hisoblanadi.

---

## 15. Telegram Bot Sozlash — `/settings/telegram`

```
┌─────────────────────────────────────────────────────────────┐
│  🤖 Telegram Bot Sozlash                                    │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  HOLAT: ✅ Ulangan                                   │  │
│  │  Telegram: @username                                 │  │
│  │                          [❌ Uzish]                  │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  Agar ulanmagan bo'lsangiz:                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  1. @TenderHelperBot ni Telegram'da oching           │  │
│  │  2. /start buyrug'ini yuboring                       │  │
│  │  3. Quyidagi kodni botga yuboring:                   │  │
│  │                                                      │  │
│  │  ┌────────────────────────────┐                      │  │
│  │  │  TH-XXXXXXXX              │  [Yangilash]          │  │
│  │  └────────────────────────────┘                      │  │
│  │  Kod 10 daqiqa amal qiladi                           │  │
│  │                                                      │  │
│  │  [📲 @TenderHelperBot ni ochish]                     │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  BILDIRISHNOMA SOZLAMALARI                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Yangi mos tenderlar     ✅ Yoqiq   Moslik: [80]%+   │  │
│  │  Deadline eslatmasi      ✅ Yoqiq   [3 kun] [1 kun]  │  │
│  │  Tahlil yakunlandi       ✅ Yoqiq                    │  │
│  │  Tizim xabarlari         ○  O'chiq                   │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 16. Sozlamalar — `/settings`

```
┌─────────────────────────────────────────────────────────────┐
│  ⚙️ Sozlamalar                                              │
│                                                             │
│  [🏢 Kompaniya] [🔐 Xavfsizlik] [🌐 Interfeys] [🔔 Bildirish]│
│                                                             │
│  INTERFEYS SOZLAMALARI                                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Til                 [O'zbek (UZ)              ▼]    │  │
│  │  Mavzu (Theme)       ○ Yorug'  ● Qorong'i  ○ Tizim  │  │
│  │  Sana formati        [DD.MM.YYYY              ▼]     │  │
│  │  Valyuta             [UZS (so'm)              ▼]     │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  HISOB XAVFSIZLIGI                                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Email: user@company.uz              [O'zgartirish]   │  │
│  │  Parol:  ••••••••••••               [O'zgartirish]   │  │
│  │  Google: Ulangan ✅                  [Uzish]         │  │
│  │  Ikki bosqichli: O'chiq             [Yoqish]         │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  HISOBNI O'CHIRISH                                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  ⚠️ Bu amalni bekor qilib bo'lmaydi                   │  │
│  │  [Hisobni o'chirish]                                 │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 17. Landing Sahifa — `/` (Autentifikatsiyasiz)

```
┌─────────────────────────────────────────────────────────────┐
│  HEADER: [🔷 TenderHelper] [Imkoniyatlar] [Narxlar] [Blog]  │
│                              [Kirish] [Bepul boshlash →]    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  HERO                                                       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │   Tenderlarda g'alaba qozonish                       │  │
│  │   endi ancha oson                                    │  │
│  │                                                      │  │
│  │   AI yordamida tender hujjatlarini tahlil qiling,    │  │
│  │   moslik ballini bilib oling va xatarlardan          │  │
│  │   oldindan ogoh bo'ling.                             │  │
│  │                                                      │  │
│  │   [🚀 Bepul boshlash] [▶ Videoni ko'rish]            │  │
│  │                                                      │  │
│  │   ✅ Kredit karta kerak emas                         │  │
│  │   ✅ 2 daqiqada ro'yxatdan o'ting                   │  │
│  │                                                      │  │
│  │           ┌────────────────────────────────┐         │  │
│  │           │  Dashboard ko'rinishi mockup  │         │  │
│  │           │  (Animatsiyali, interaktiv)   │         │  │
│  │           └────────────────────────────────┘         │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  STATISTIKA BAND                                            │
│  ┌──────────┬──────────┬──────────┬────────────────────┐   │
│  │ 12,000+  │  4 ta    │  78%     │  500+ kompaniya    │   │
│  │  Tender  │  Portal  │  O'rt.   │  ishonadi          │   │
│  │ tahlil   │  ulangan │  moslik  │                    │   │
│  └──────────┴──────────┴──────────┴────────────────────┘   │
│                                                             │
│  IMKONIYATLAR (Features)                                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  🔍 Aqlli qidiruv   📊 AI tahlil   🧮 Kalkulyator    │  │
│  │  🤖 Telegram bot    👥 Jamoa       🏆 Raqobat        │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  NARXLAR (3 tarif)                                          │
│                                                             │
│  IZOHLAR (Testimonials)                                     │
│                                                             │
│  FAQ                                                        │
│                                                             │
│  FOOTER: Hujjatlar | Shartlar | Maxfiylik | API | Blog     │
└─────────────────────────────────────────────────────────────┘
```

---

## 18. Tarif Cheklov UX Patterni

Barcha cheklangan funksiyalar uchun bir xil `<SubscriptionGate>` patterni:

### 18.1. Inline Bloklash

```
┌──────────────────────────────────────────────────────────┐
│  📤 PDF Hisobotni yuklab olish                            │
│                                                           │
│  Bu funksiya ⚡ PRO tarifida mavjud                       │
│                                                           │
│  Pro tarifida siz olasiz:                                 │
│  ✅ Cheksiz AI tahlil        ✅ PDF/Excel export          │
│  ✅ Telegram bildirishlar    ✅ Tahlil tarixi             │
│                                                           │
│  [Hozircha emas]          [⚡ Pro ga o'tish →]           │
└──────────────────────────────────────────────────────────┘
```

### 18.2. Usage Limit Ogohlantirishlar

```
/* 75% band bo'lganda — Sariq banner */
┌──────────────────────────────────────────────────────────┐
│ ⚠️ Bu oy 3 ta tahlil ishlatdingiz (4 tadan). 1 ta qoldi. │
│                                          [Pro ga o'ting] │
└──────────────────────────────────────────────────────────┘

/* 100% band bo'lganda — Qizil banner */
┌──────────────────────────────────────────────────────────┐
│ 🔴 Oylik tahlil limitingiz tugadi. Keyingi yangilanish:  │
│    15 kun 6 soat qoldi              [⚡ Pro ga o'tish]    │
└──────────────────────────────────────────────────────────┘
```

---

## 19. Xato va Bo'sh Holat Dizayni

### 19.1. Bo'sh Holat (Empty State)

```
┌──────────────────────────────────────────────────────────┐
│                     🔍                                   │
│           Hali hech qanday tahlil yo'q                   │
│                                                          │
│     Birinchi tahlilni boshlash uchun tenderlar           │
│     sahifasiga o'ting va "AI Tahlil" tugmasini bosing.   │
│                                                          │
│            [🔍 Tenderlar sahifasiga o'tish]              │
└──────────────────────────────────────────────────────────┘
```

### 19.2. Xato Holati (Error State)

```
┌──────────────────────────────────────────────────────────┐
│                     ⚠️                                   │
│              Tahlil muvaffaqiyatsiz                      │
│                                                          │
│     AI xizmatida vaqtinchalik muammo yuz berdi.         │
│     Tahlil balli saqlanmadi va limit sarflanmadi.        │
│                                                          │
│        [🔄 Qayta urinib ko'rish] [← Orqaga]             │
└──────────────────────────────────────────────────────────┘
```

---

## 20. Mobilga Moslashtirilgan Ekranlar

### 20.1. Mobile Navigation

```
┌──────────────────────┐
│  [≡] TenderHelper [🔔]│
├──────────────────────┤
│                      │
│  [Asosiy kontent]    │
│                      │
│                      │
│                      │
│                      │
├──────────────────────┤
│ [🏠] [🔍] [📋] [👤] │
└──────────────────────┘
```

Bottom navigation: Dashboard, Tenderlar, Tahlillar, Profil.

### 20.2. Mobile Tender Karta

```
┌──────────────────────┐
│ 🟢 Faol • UzEx       │
│ Axborot tizimini     │
│ modernizatsiya...    │
│                      │
│ 💰 250 mln so'm      │
│ ⏰ 3 kun qoldi       │
│                      │
│ Moslik: ██████░░ 82% │
│                      │
│ [Tahlil] [Ko'rish →] │
└──────────────────────┘
```

---

## 21. Mikroanimatsiyalar va Interaktivlik

| Element | Animatsiya |
|---------|-----------|
| Modal ochilish | Scale + fade in (200ms cubic-bezier) |
| Sidebar | Slide in (300ms) |
| Toast | Slide + fade top-right (300ms), auto-dismiss 5s |
| Button hover | Subtle scale (1.02) + shadow |
| Card hover | Y-translate (-2px) + shadow elevation |
| AI tahlil progress | Smooth fill (CSS transition) |
| Tarif toggle (oylik/yillik) | Spring animation narxlarda |
| OTP input | Focus ring animatsiya |
| Skeleton | Shimmer effect (pulse) |
| Confetti (welcome) | Canvas confetti.js |
| Karta moslik ball | Odometer — raqam aylanishi |
| Deadline taymer | Sekundlik update |

---

## 22. Target Fayllar va Marshrut Tuzilmasi

Quyidagi daraxt mavjud repo snapshoti emas, tasdiqlangan target frontend
strukturasi. Amaldagi fayllar bosqichma-bosqich shu ownership chegaralariga
ko'chiriladi.

```
frontend/src/
├── pages/
│   ├── public/
│   │   ├── LandingPage.jsx
│   │   ├── LoginPage.jsx
│   │   ├── RegisterPage.jsx          ← Stepper wrapper
│   │   ├── RegisterStep1Account.jsx  ← Hisob
│   │   ├── RegisterStep2Verify.jsx   ← OTP
│   │   ├── RegisterStep3Company.jsx  ← Kompaniya
│   │   ├── RegisterStep4Plan.jsx     ← Tarif
│   │   ├── RegisterWelcome.jsx       ← Yakuniy
│   │   ├── ForgotPasswordPage.jsx
│   │   └── NotFoundPage.jsx
│   │
│   └── private/
│       ├── DashboardPage.jsx
│       ├── TendersPage.jsx
│       ├── TenderDetailPage.jsx
│       ├── AnalysisPage.jsx          ← Progress + Natija
│       ├── CalculatorPage.jsx
│       ├── SavedPage.jsx
│       ├── NotificationsPage.jsx
│       ├── BillingPage.jsx
│       ├── TeamPage.jsx              ← Business/Enterprise
│       ├── CompetitorsPage.jsx       ← Business/Enterprise
│       ├── DocumentsPage.jsx          ← Business/Enterprise
│       ├── DocumentEditorPage.jsx     ← Business/Enterprise + STIR
│       └── settings/
│           ├── SettingsPage.jsx
│           ├── CompanySettings.jsx
│           ├── SecuritySettings.jsx
│           ├── TelegramSettings.jsx
│           └── InterfaceSettings.jsx
│   │
│   └── superadmin/
│       ├── AdminOverviewPage.jsx
│       ├── AdminUsersPage.jsx
│       ├── AdminCompaniesPage.jsx
│       ├── AdminPlansPage.jsx
│       ├── AdminSubscriptionsPage.jsx
│       ├── AdminPaymentsPage.jsx
│       ├── AdminBusinessUsagePage.jsx
│       ├── AdminOperationsPage.jsx
│       ├── AdminTemplatesPage.jsx
│       ├── AdminSettingsPage.jsx
│       └── AdminAuditPage.jsx
│
├── components/
│   ├── layout/
│   │   ├── AppLayout.jsx
│   │   ├── Sidebar.jsx
│   │   ├── Header.jsx
│   │   ├── BottomNav.jsx            ← Mobile
│   │   └── AdminLayout.jsx          ← Privileged desktop layout
│   │
│   ├── ui/
│   │   ├── Button.jsx
│   │   ├── Card.jsx
│   │   ├── Badge.jsx
│   │   ├── Modal.jsx
│   │   ├── Toast.jsx
│   │   ├── Skeleton.jsx
│   │   ├── Progress.jsx
│   │   ├── Stepper.jsx
│   │   ├── SubscriptionGate.jsx     ← Tarif cheklov
│   │   ├── UsageLimitBanner.jsx     ← Limit ogohlantirish
│   │   └── LanguageSwitcher.jsx
│   │
│   ├── auth/
│   │   ├── GoogleLoginButton.jsx
│   │   ├── OTPVerification.jsx
│   │   └── PasswordStrength.jsx
│   │
│   ├── tender/
│   │   ├── TenderCard.jsx
│   │   ├── TenderFilters.jsx
│   │   ├── TenderSearch.jsx
│   │   └── MatchScoreBar.jsx
│   │
│   ├── analysis/
│   │   ├── AnalysisProgress.jsx
│   │   ├── AnalysisResult.jsx
│   │   ├── RedFlagCard.jsx
│   │   ├── DocumentChecklist.jsx
│   │   ├── CitationBlock.jsx        ← Manba ko'rsatish
│   │   └── AIDisclaimer.jsx
│   │
│   ├── billing/
│   │   ├── PricingTable.jsx
│   │   ├── PlanComparisonModal.jsx
│   │   └── PaymentModal.jsx
│   │
│   ├── documents/
│   │   ├── TemplatePicker.jsx
│   │   ├── DocumentEditor.jsx
│   │   ├── DocumentStatus.jsx
│   │   ├── RevisionHistory.jsx
│   │   └── ExportModal.jsx
│   │
│   ├── dashboard/
│       ├── StatsCard.jsx
│       ├── RecentAnalyses.jsx
│       └── DeadlineWidget.jsx
│   │
│   └── admin/
│       ├── AdminSidebar.jsx
│       ├── MetricCard.jsx
│       ├── HealthStatusGrid.jsx
│       ├── AdminDataTable.jsx
│       ├── AdminActionModal.jsx
│       ├── StepUpAuthModal.jsx
│       ├── EntitlementPreview.jsx
│       ├── PaymentTimeline.jsx
│       └── AuditTimeline.jsx
│
├── routes/
│   ├── AppRouter.jsx
│   ├── PublicRoute.jsx
│   ├── PrivateRoute.jsx
│   └── AdminRoute.jsx          ← Capability + MFA guard
│
├── store/
│   ├── authStore.js          ← Zustand
│   ├── uiStore.js            ← Theme, sidebar
│   └── tenderStore.js        ← Filters, search
│
├── api/
│   ├── client.js             ← Axios instance
│   ├── auth.js
│   ├── tenders.js
│   ├── analyses.js
│   ├── calculator.js
│   ├── billing.js
│   └── admin.js                ← Superadmin control-plane API
│
├── i18n/
│   ├── index.js
│   └── locales/
│       ├── uz/common.json
│       ├── ru/common.json
│       ├── en/common.json
│       ├── kaa/common.json
│       └── tg/common.json
│
└── utils/
    ├── formatters.js         ← Narx, sana formatlash
    ├── validators.js
    └── subscriptionHelpers.js
```

---

## 23. AI Document Workspace — `/documents`

Business/Enterprise va STIR tasdiqlangan company uchun hujjat yaratish,
inline tahrirlash, tasdiqlash va export oqimi.

### 23.1. Hujjatlar ro'yxati

- template, tender, status, author va updated time;
- `generating`, `draft`, `approved`, `exported`, `failed`, `archived` badge;
- template turi va til filteri;
- empty state rasmiy document funksiyasi uchun STIR gate sababini ko'rsatadi.

### 23.2. Generate flow

1. Tender tanlash.
2. Ariza, kafolat xati, tijorat taklifi yoki compliance template tanlash.
3. Company va tender context preview.
4. Yetishmayotgan majburiy fieldlarni to'ldirish.
5. Async generation boshlash.
6. Haqiqiy status polling; soxta progress yo'q.

### 23.3. Inline Editor — `/documents/{id}/edit`

```
┌──────────────────────────────────────────────────────────────────┐
│ Draft • Kafolat xati  Saved 8s ago  [Versions] [Approve] [Export]│
├───────────────────────┬──────────────────────────────────────────┤
│ Context               │ Rich Text Editor                         │
│ Company / STIR        │ Heading, paragraph, list, table          │
│ Tender / buyer        │                                          │
│ Verified facts        │ [Canonical document content]             │
│ Warnings              │                                          │
├───────────────────────┴──────────────────────────────────────────┤
│ AI disclaimer • Template v3 • Edit version 12                    │
└──────────────────────────────────────────────────────────────────┘
```

- autosave 2-5 soniya debounce;
- optimistic locking va `409 Conflict` resolution;
- XSS sanitization;
- canonical JSON, sanitized HTML preview;
- approval userning ongli actioni;
- PDF/DOCX export approvaldan keyin;
- generation yoki export xatosi real `FAILED` holatida ko'rsatiladi.

---

## 24. Superadmin Console — `/superadmin`

Superadmin oddiy foydalanuvchi sidebaridan ajratilgan alohida privileged
layoutda ishlaydi. U Business tarifining mavjud subscription, feature va
usage ma'lumotlarini boshqaradi; yangi billing oqimi yaratmaydi.

### 24.1. Kirish va global layout

- route guard: admin capability + MFA;
- kritik amaldan oldin step-up re-auth modal;
- yuqorida qizil `SUPERADMIN` environment badge;
- production/staging muhiti doim ko'rinadi;
- global search: user, email, telefon, company va STIR;
- default desktop-first, tablet read-only support; kritik write action
  mobil ekranda cheklanadi;
- har bir sahifada `updated_at` va data freshness.

Sidebar:

1. Overview.
2. Userlar.
3. Kompaniyalar.
4. Tariflar va Feature'lar.
5. Obunalar.
6. To'lovlar.
7. Business Usage.
8. AI Operatsiyasi.
9. Tender/Scraping.
10. Hujjat Shablonlari.
11. System Settings.
12. Audit Log.

### 24.2. Overview — `/superadmin`

```
┌────────────────────────────────────────────────────────────────────┐
│ SUPERADMIN • Production   [Global search]  Updated 12s ago  [Admin]│
├────────────────────────────────────────────────────────────────────┤
│ [MRR] [Active subscriptions] [DAU] [AI cost] [Failed payments]    │
│                                                                    │
│ Revenue & subscriptions        User growth / onboarding funnel     │
│ [time-series chart]            [chart + STIR completion]           │
│                                                                    │
│ Business feature adoption      System health                       │
│ [generator/editor/competitor]  [API][Queue][AI][Scraping][Payment] │
│                                                                    │
│ Alerts: failed webhook, stale scraper, high AI failure, queue lag  │
└────────────────────────────────────────────────────────────────────┘
```

Filterlar: `Today`, `7 kun`, `30 kun`, `90 kun`, custom range. Revenue
kartalari reconciled, operational kartalar near-real-time badge bilan
ajratiladi. Stale metrika yashirilmaydi, sariq `Data delayed` holatiga o'tadi.

### 24.3. User va kompaniyalar

`/superadmin/users` DataTable:

- ism, email/telefon, company, role, plan, status, last active;
- qidiruv va status/plan/STIR/date filter;
- detail drawer: auth/session, memberships, onboarding, usage va support
  timeline;
- amallar: block/unblock, session revoke;
- PII maskalangan, reveal/export uchun reason modal.

`/superadmin/companies`:

- company, STIR/registry status, owner, members, plan, usage va created date;
- detailda Business feature usage, generated documents va competitor
  analytics agregati;
- company entitlement preview va subscription tarixiga deep link.

Impersonation tugmasi ko'rsatilmaydi.

### 24.4. Tarif, feature va obunalar

`/superadmin/plans`:

- Free, Pro, Business, Enterprise kartalari;
- narx, billing period, fair-use, team seats va feature matrix;
- draft change -> impact preview -> publish oqimi;
- mavjud subscriberlarga ta'siri alohida ko'rsatiladi.

`/superadmin/subscriptions`:

- active/trial/expired/cancelled/paused filterlari;
- company, plan, period, next charge, usage va payment status;
- activate, upgrade, scheduled downgrade, pause, cancel, extend;
- har bir actionda reason, effective date, expiry va confirmation;
- Business entitlementlar: document generation, editor/export, competitor
  intelligence va team alohida ko'rinadi.

### 24.5. To'lov va revenue

`/superadmin/payments`:

- transaction status, provider ID, amount, company, plan va timestamp;
- prepare/complete webhook timeline;
- failed/replayed webhook va reconciliation mismatch queue;
- refund review alohida danger modalda;
- completed transaction uchun inline amount/status edit yo'q;
- CSV export capability va audit bilan.

### 24.6. Business Usage va operatsiyalar

`/superadmin/business-usage`:

- company/plan/date bo'yicha generator, export, competitor va team usage;
- limitga yaqin companylar;
- adoption funnel va unit cost.

`/superadmin/operations` tablari:

- AI: request, token, cost, latency, failure, provider/model;
- Scraping: source, last run, freshness, errors, retry;
- Queue: depth, active/failed task va dead-letter;
- Feature flags: kill switch va maintenance banner;
- Templates: version, language, active/published holati.

Pause, retry, publish va kill switch actionlari step-up modal va impact
summary talab qiladi.

### 24.7. Audit Log — `/superadmin/audit`

Ustunlar:

- vaqt;
- admin;
- capability;
- action;
- target;
- reason;
- oldingi/yangi qiymat;
- request ID va IP;
- success/failure.

Audit detail drawer o'qish uchun; edit/delete action yo'q. Filter va export
faqat tegishli capability bilan.

### 24.8. Holatlar va xavfsizlik UX

- danger action qizil, destructive bo'lmagan action secondary;
- bulk action avval preview va affected count ko'rsatadi;
- write conflict `409` bo'lsa yangi qiymat va refresh actioni ko'rsatiladi;
- step-up session muddati headerda ko'rinadi;
- permission yetmasa disabled tugma emas, action umuman ko'rsatilmaydi;
- read-only support roli billing yoki operations write actionini ko'rmaydi;
- barcha grafiklarda empty, loading, error va stale state mavjud.

---

## 25. Tarif Huquqlari Matritsasi (Kodda ishlatish uchun)

```javascript
// subscriptionHelpers.js
export const PLAN_FEATURES = {
  free: {
    analysis_per_month: 4,
    saved_tenders: 10,
    telegram_notifications: false,
    export_pdf: false,
    export_excel: false,
    analysis_history: false,
    team_members: 0,
    competitor_analysis: false,
    advanced_filters: false,
    api_access: false,
    document_generation: false,
    document_export: false,
    advanced_audit: false,
  },
  pro: {
    analysis_per_month: null,       // Cheksiz (fair-use: 100)
    saved_tenders: null,            // Cheksiz
    telegram_notifications: true,
    export_pdf: true,
    export_excel: true,
    analysis_history: true,
    team_members: 0,
    competitor_analysis: false,
    advanced_filters: true,
    api_access: false,
    document_generation: false,
    document_export: false,
    advanced_audit: false,
  },
  business: {
    analysis_per_month: null,       // Cheksiz (fair-use: 250)
    saved_tenders: null,            // Cheksiz
    telegram_notifications: true,
    export_pdf: true,
    export_excel: true,
    analysis_history: true,
    team_members: 5,                // Kengaytiriladigan
    competitor_analysis: true,
    advanced_filters: true,
    api_access: true,
    document_generation: true,
    document_export: true,
    advanced_audit: false,
  },
  enterprise: {
    analysis_per_month: null,       // Cheksiz (fair-use: 500)
    saved_tenders: null,
    telegram_notifications: true,
    export_pdf: true,
    export_excel: true,
    analysis_history: true,
    team_members: null,             // Contract bo'yicha
    competitor_analysis: true,
    advanced_filters: true,
    api_access: true,
    document_generation: true,
    document_export: true,
    advanced_audit: true,
  },
};

// Komponentda ishlatish:
// <SubscriptionGate feature="export_pdf" requiredPlan="pro">
//   <ExportButton />
// </SubscriptionGate>
```

Superadmin ushbu tarif matritsasiga kirmaydi. Uning ruxsatlari obuna orqali
emas, `Plan.md` va `IMPLEMENTATION_PLAN.md`dagi capability matrix, MFA va
step-up authentication qoidalari orqali beriladi.

---

*Hujjat: `DESIGN.md` — Loyiha dizayn spesifikatsiyasi*  
*Plan.md va bu hujjat o'rtasida ziddiyat bo'lsa — Plan.md ustuvor.*
