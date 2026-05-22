# TenderHelper AI — UI/UX va Texnik Arxitektura Rejasi (v2.0)

**Versiya:** 2.0 | **Yangilangan:** 2026-05-22  
**O'zgarishlar:** Ko'p tillilik (i18n), Dark Mode, zamonaviy dizayn standartlari qo'shildi

---

## 🎨 1. UI/UX Dizayn Falsafasi

TenderHelper foydalanuvchilari davlat xaridlarida millionlab, ba'zan milliardlab so'm aylanmasi bilan ishlaydigan odamlardir. Shuning uchun interfeys **mutlaqo jiddiy va professional** bo'lishi shart.

### Vizual Til (Visual Language)
- **Minimalizm:** Ekranda faqat eng muhim axborot qoladi. Bo'sh joylardan (white space) havo berish uchun keng foydalanamiz
- **Ishonch (Trust):** Bank dasturlari kabi his-tuyg'u uyg'otishi kerak
- **Progressiv ochilish (Progressive Disclosure):** Murakkab ma'lumotlarni birdaniga ko'rsatmaymiz
- **Consistency (Izchillik):** Barcha sahifalar, komponentlar va holatlar yagona dizayn tizimiga bo'ysunadi
- **Mobile-First:** Barcha sahifalar avval telefon uchun, keyin desktop uchun optimallashtiriladi

### Zamonaviy Dizayn Uslublari
Platformaning har bir qismida quyidagi zamonaviy texnikalar ishlatiladi:

| Uslub | Qo'llanilish joyi |
|-------|-------------------|
| **Glassmorphism** | Navbar, modal overlay, sidebar — shaffof blur effekt |
| **Subtle Gradients** | Kartalar foni, tugmalar hover holati, progress bar |
| **Micro-animations** | Tugma bosilganda, karta hover, sahifa o'tishi (framer-motion) |
| **Skeleton Loaders** | Barcha loading holatlarida kontent shaklidagi kulrang skeletlar |
| **Smooth Transitions** | Sahifalar orasida 250ms fade, komponentlar slide-up |
| **Elevation System** | shadow-card → shadow-elevated → shadow-modal (3 daraja) |
| **Neumorphism (light)** | Faqat stat kartalar va kalkulyator input'lari uchun |

---

## 🌙 2. Dark Mode (Qorong'u Rejim)

Dark mode — faqat "qo'shimcha" emas, balki **birinchi darajali fuqaro (first-class citizen)**. Ko'pchilik foydalanuvchilar kechasi ishlaydi.

### Implementatsiya
- Tailwind CSS `dark:` class strategiyasi
- `localStorage` da foydalanuvchi tanlovi saqlanadi
- Tizim sozlamalariga avtomatik moslashish (`prefers-color-scheme: dark`)
- Toggle tugmasi: Navbar'da Quyosh/Oy ikonkasi

### Ranglar jufti

| Element | Light Mode | Dark Mode |
|---------|-----------|-----------|
| **Background** | `#F8FAFC` (surface-50) | `#020617` (surface-950) |
| **Card/Surface** | `#FFFFFF` | `#0F172A` (surface-900) |
| **Border** | `#E2E8F0` (surface-200) | `#1E293B` (surface-800) |
| **Text Primary** | `#0F172A` (surface-900) | `#F1F5F9` (surface-100) |
| **Text Secondary** | `#64748B` (surface-500) | `#94A3B8` (surface-400) |
| **Input BG** | `#F8FAFC` (surface-50) | `#1E293B` (surface-800) |
| **Navbar** | `white/80 blur` | `surface-900/80 blur` |

### Qoidalar
- ❌ Mutlaq qora (`#000000`) fon ishlatmaymiz — ko'zni charchatadi
- ✅ To'q ko'k-kulrang (`#020617`) ishlatamiz — yumshoqroq
- ❌ Yorug' rangda yozilgan matnni qorong'u fonda ishlatmaymiz — kontrast yetarli bo'lmaydi
- ✅ Ranglarni dark rejimda biroz yorqinlashtirish (primary-500 → primary-400)

---

## 🌍 3. Ko'p Tillilik (Internationalization — i18n)

### Qo'llab-quvvatlanadigan tillar

| # | Til | Kod | Yozuv | Status |
|---|-----|-----|-------|--------|
| 1 | **O'zbek** (Lotin) | `uz` | Chapdan-o'ngga | 🟢 Asosiy |
| 2 | **Русский** | `ru` | Chapdan-o'ngga | 🟢 To'liq |
| 3 | **English** | `en` | Chapdan-o'ngga | 🟢 To'liq |
| 4 | **Қарақалпақ** | `kaa` | Chapdan-o'ngga | 🟡 MVP+ |
| 5 | **Тоҷикӣ** | `tg` | Chapdan-o'ngga | 🟡 MVP+ |

### Texnik arxitektura: `react-i18next`

```
frontend/
└── src/
    └── i18n/
        ├── index.js          # i18next konfiguratsiyasi
        ├── locales/
        │   ├── uz/
        │   │   ├── common.json     # Umumiy so'zlar (Kirish, Chiqish, Saqlash...)
        │   │   ├── auth.json       # Auth sahifa matni
        │   │   ├── dashboard.json  # Dashboard matni
        │   │   ├── analysis.json   # AI tahlil matni
        │   │   └── pricing.json    # Tarif matni
        │   ├── ru/
        │   │   ├── common.json
        │   │   ├── auth.json
        │   │   ├── dashboard.json
        │   │   ├── analysis.json
        │   │   └── pricing.json
        │   ├── en/
        │   │   └── ...
        │   ├── kaa/
        │   │   └── ...
        │   └── tg/
        │       └── ...
```

### i18n konfiguratsiya
```javascript
// i18n/index.js
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

i18n.use(initReactI18next).init({
  resources: { uz, ru, en, kaa, tg },
  lng: localStorage.getItem('language') || 'uz', // Default til
  fallbackLng: 'uz',
  ns: ['common', 'auth', 'dashboard', 'analysis', 'pricing'],
  defaultNS: 'common',
  interpolation: { escapeValue: false },
});
```

### Til tanlash UI
- Navbar'da **bayroqli dropdown** — hozirgi tilning bayrog'i ko'rinadi
- Tanlash: 🇺🇿 O'zbek | 🇷🇺 Русский | 🇬🇧 English | 🏳️ Қарақалпақ | 🇹🇯 Тоҷикӣ
- Tanlangan til `localStorage('language')` da saqlanadi
- Sahifa qayta yuklanmasdan til almashinadi (real-time)

### Tarjima qoidalari
- **UI elementlari:** 100% tarjima qilinadi (tugmalar, menyular, xato xabarlari)
- **AI tahlil natijasi:** Gemini promptda til parametri bo'ladi — natija o'sha tilda chiqadi
- **Tender ma'lumotlari:** Asl tilda ko'rsatiladi (tarjima qilinmaydi)
- **Raqamlar formati:** Barcha tillarda bir xil: `10 000 000 so'm`

### Tarjima misoli
```json
// uz/common.json
{
  "nav": {
    "dashboard": "Boshqaruv paneli",
    "tenders": "Tenderlar",
    "analysis": "AI Tahlil",
    "calculator": "Kalkulyator",
    "pricing": "Tariflar",
    "profile": "Profil",
    "logout": "Chiqish",
    "dark_mode": "Qorong'u rejim",
    "language": "Til"
  },
  "actions": {
    "save": "Saqlash",
    "cancel": "Bekor qilish",
    "delete": "O'chirish",
    "search": "Qidirish",
    "filter": "Filtr",
    "analyze": "Tahlil qilish",
    "back": "Orqaga",
    "next": "Keyingi",
    "loading": "Yuklanmoqda..."
  }
}

// ru/common.json
{
  "nav": {
    "dashboard": "Панель управления",
    "tenders": "Тендеры",
    "analysis": "AI Анализ",
    "calculator": "Калькулятор",
    "pricing": "Тарифы",
    "profile": "Профиль",
    "logout": "Выход",
    "dark_mode": "Тёмная тема",
    "language": "Язык"
  },
  "actions": {
    "save": "Сохранить",
    "cancel": "Отмена",
    "delete": "Удалить",
    "search": "Поиск",
    "filter": "Фильтр",
    "analyze": "Анализировать",
    "back": "Назад",
    "next": "Далее",
    "loading": "Загрузка..."
  }
}
```

---

## 🎨 4. Ranglar Palitrasi

Ranglar psixologiyasi biznes qarorlariga ta'sir qiladi:

| Rang | Hex | Ma'no | Ishlatilish joyi |
|------|-----|-------|------------------|
| **Deep Blue** | `#2563EB` (primary-600) | Ishonch, barqarorlik | Tugmalar, navlinks, asosiy accent |
| **Navy** | `#0F172A` (primary-950) | Korporativ ruh | Dark mode fon, logotip |
| **Emerald** | `#10B981` (success-500) | Xavfsiz, tavsiya | "Qatnashish mumkin" signali |
| **Amber** | `#F59E0B` (warning-500) | E'tibor, risk | Red flag warning darajasi |
| **Rose** | `#EF4444` (danger-500) | Xavf, to'xtatish | Stop-Loss, blocker red flags |
| **Slate** | `#64748B` (surface-500) | Neytral | Ikkilamchi matn, borderlar |

---

## ✍️ 5. Tipografiya

| Element | Shrift | Size | Weight |
|---------|--------|------|--------|
| **H1** | Inter | 30px / 1.875rem | Bold (700) |
| **H2** | Inter | 24px / 1.5rem | Semibold (600) |
| **H3** | Inter | 20px / 1.25rem | Semibold (600) |
| **Body** | Inter | 16px / 1rem | Regular (400) |
| **Small** | Inter | 14px / 0.875rem | Regular (400) |
| **Caption** | Inter | 12px / 0.75rem | Medium (500) |
| **Raqamlar** | Inter `tabular-nums` | — | — |
| **Kod** | JetBrains Mono | 14px | Regular |

---

## 🧠 6. UX (Foydalanuvchi Tajribasi) Tavsiyalari

### 6.1. Onboarding (Stepper)
- 3 ta qadamli silliq animatsiya (framer-motion)
- Har bir qadamda progress indicator (1/3, 2/3, 3/3)
- "Orqaga" tugmasi bilan erkin navigatsiya

### 6.2. AI Tahlil Kutish Ekrani
- 4 bosqichli shaffof progress bar:
  - ✅ Hujjatlar yuklanmoqda...
  - 🔄 Yuridik terminlar tahlil qilinmoqda...
  - ⏳ Red Flag tekshiruvi...
  - ⏳ Yakuniy xulosa tayyorlanmoqda...
- Pulse animatsiya, foiz ko'rsatgichi

### 6.3. Kalkulyator
- Raqamlar avtomat `10 000 000` formatida
- Stop-Loss chizig'iga yetganda qizil pulsating border
- Vizual bar chart: tannarx vs tavsiya narx vs boshlang'ich narx

### 6.4. Skeleton Loaders
- Barcha sahifalarda kontent shaklidagi skeletlar
- Shimmer animatsiya (chapdan o'ngga harakatlanuvchi gradient)

### 6.5. Empty States
- Chiroyli illustratsiya (lucide-react ikonkalar)
- Yorliq: "Hali tahlil qilmadingiz" + CTA tugma
- Hech qachon bo'sh oq ekran ko'rsatmaymiz

### 6.6. Error States
- Toast notifikatsiyalar (o'ng yuqori burchak, 4 soniya)
- Network error: retry tugmali xato kartasi
- 404: professional sahifa + bosh sahifaga qaytish

---

## 🛠️ 7. Texnik Stack (Frontend)

| Texnologiya | Versiya | Maqsad |
|-------------|---------|--------|
| React | 18 | UI framework |
| Vite | 8 | Build tool, HMR |
| Tailwind CSS | v4 | Styling + design system |
| Zustand | latest | State management |
| React Query | v5 | Data fetching + caching |
| React Router | v7 | Routing |
| react-i18next | latest | **Ko'p tillilik (i18n)** |
| Framer Motion | latest | Animatsiyalar |
| Lucide React | latest | Ikonkalar |
| Axios | latest | HTTP client |

---

## 📐 8. Responsive Breakpoints

| Breakpoint | O'lcham | Maqsad |
|-----------|---------|--------|
| `xs` | 0-374px | Kichik telefonlar |
| `sm` | 375-639px | Telefon (asosiy) |
| `md` | 640-767px | Katta telefon |
| `lg` | 768-1023px | Planshet |
| `xl` | 1024-1279px | Kichik laptop |
| `2xl` | 1280px+ | Desktop |

### Layout strategiyasi
- **Mobile (sm):** Single column, bottom tab navigation, full-width kartalar
- **Tablet (lg):** 2 column grid, sidebar yashiriladi (hamburger)
- **Desktop (xl+):** Sidebar + main content, 3 column grid stat kartalar

---

## 🧩 9. Komponent Dizayn Tizimi

Barcha komponentlar yagona stilga bo'ysunadi:

### Kartalar
```
┌─────────────────────────────┐
│  ┌──┐  Sarlavha              │  ← 20px padding
│  │🔵│  Ikkilamchi matn       │  ← Ikonka + matn
│  └──┘                        │
│  ─────────────────────────── │  ← Border (1px, surface-200)
│  Asosiy kontent              │
│                              │
│  [Tugma]           123 456   │  ← CTA + raqam
└─────────────────────────────┘
```
- `rounded-xl` (12px radius)
- `shadow-card` (yorug'da), dark: border bilan ajratish
- Hover: `shadow-elevated` + scale(1.01)

### Tugmalar
| Turi | Light | Dark |
|------|-------|------|
| **Primary** | `bg-primary-600 text-white` | Xuddi shunday |
| **Secondary** | `bg-surface-100 text-surface-700` | `bg-surface-800 text-surface-200` |
| **Danger** | `bg-danger-600 text-white` | Xuddi shunday |
| **Ghost** | `text-primary-600 hover:bg-primary-50` | `text-primary-400 hover:bg-primary-950` |

Barcha tugmalarda:
- `transition-colors duration-150`
- `focus:ring-2 focus:ring-primary-500 focus:ring-offset-2`
- Disabled holat: `opacity-50 cursor-not-allowed`

### Input/Form
- `rounded-lg` border
- Focus: `ring-2 ring-primary-500`
- Error: `ring-2 ring-danger-500` + qizil xato xabari
- Label har doim input ustida (floating label ishlatmaymiz — soddaroq)

---

## ✅ Tekshiruv Ro'yxati (Har bir sahifa uchun)

Har bir sahifa qurilganda quyidagilar tekshirilishi shart:

- [ ] Light mode — barcha elementlar ko'rinadi
- [ ] Dark mode — barcha elementlar ko'rinadi, kontrast yetarli
- [ ] Mobile (375px) — tartib buzilmagan
- [ ] Tablet (768px) — ikki ustunli layout
- [ ] Desktop (1280px+) — sidebar + content
- [ ] Loading holat — skeleton ko'rsatiladi
- [ ] Empty state — chiroyli bo'sh holat
- [ ] Error state — xato xabari ko'rsatiladi
- [ ] Til almashtirganda barcha matn yangilanadi
- [ ] Keyboard navigatsiya ishlaydi (Tab, Enter, Escape)
- [ ] Focus ring ko'rinadi
