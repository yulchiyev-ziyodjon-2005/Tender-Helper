# TenderHelper AI - UI/UX va Texnik Arxitektura Rejasi

Ushbu hujjat loyihaning frontend qismini yaratish bo'yicha professional UI/UX dizayner va Senior Arxitektor sifatidagi tavsiyalarim va strategiyamni o'z ichiga oladi. Asosiy maqsad — tizimni mukammal, jiddiy, ishonchli (FinTech darajasida), shu bilan birga oddiy tadbirkor tushunadigan darajada sodda qilishdir.

## 🎨 1. UI/UX Dizayn Falsafasi

TenderHelper foydalanuvchilari davlat xaridlarida millionlab, ba'zan milliardlab so'm aylanmasi bilan ishlaydigan odamlardir. Shuning uchun interfeys **mutlaqo jiddiy va professional** bo'lishi shart. "Multfilm" yoki o'yin elementlaridan qochamiz.

### Vizual Til (Visual Language)
*   **Minimalizm:** Ekranda faqat eng muhim axborot qoladi. Bo'sh joylardan (white space) havo berish uchun keng foydalanamiz.
*   **Ishonch (Trust):** Bank dasturlari kabi his-tuyg'u uyg'otishi kerak.
*   **Progressiv ochilish (Progressive Disclosure):** Murakkab ma'lumotlarni birdaniga ko'rsatmaymiz. Masalan, tahlil xulosasi qisqa ko'rinadi, "Batafsil" tugmasi orqali kengayadi.

### Ranglar Palitrasi
Ranglar psixologiyasi biznes qarorlariga ta'sir qiladi:
*   **Asosiy (Primary):** To'q ko'k (Deep Blue - `#1E3A8A` yoki `#0F172A`). Ishonch, barqarorlik va korporativ ruh.
*   **Muvaffaqiyat/Tavsiya (Success):** Zumrad yashil (Emerald Green - `#10B981`). "Qatnashish xavfsiz" degan signal uchun.
*   **Ogohlantirish (Warning/Red Flags):** Yorqin sariq/zarg'aldoq (Amber - `#F59E0B`). "E'tibor bering, risk bor" degan ma'noda.
*   **Xavf/Stop-Loss (Danger):** Qizil (Rose/Red - `#EF4444`). Diskvalifikatsiya xavfi yoki zararga kirish nuqtasi uchun.
*   **Fon (Background):** Och kulrang (`#F8FAFC`) yorug' rejim uchun, to'q kulrang/qora (`#020617`) Dark Mode uchun.

### Tipografiya
*   **Asosiy shrift:** `Inter` yoki `Roboto`. Ular raqamlar va uzun matnlarni o'qish uchun eng zo'r (FinTech standarti).
*   Matn o'lchamlari va qalinligi (weight) orqali ierarxiyani aniq ko'rsatamiz.

## 🧠 2. UX (Foydalanuvchi Tajribasi) Tavsiyalari

1.  **Onboarding (Tanishuv bosqichi):**
    *   3 ta savolni bitta uzun formada emas, alohida ekranlarda (Stepper/Slider ko'rinishida) silliq animatsiya bilan so'raymiz.
2.  **Skaner Progressi (AI kutilish vaqti):**
    *   AI tahlili 10-30 soniya olishi mumkin. Bu vaqtda shunchaki "Loading" emas, balki jarayonni **shaffof** ko'rsatuvchi interaktiv progress-bar qilamiz:
        *   ✅ *Hujjatlar yuklanmoqda...*
        *   🔄 *Yuridik terminlar oddiy tilga o'girilmoqda...* (Aylanuvchi icon)
        *   ⏳ *Red Flag'lar tekshirilmoqda...*
    *   Bu kutilish vaqtini zerikarli emas, balki qiziqarli qiladi va foydalanuvchida tizimning "aqlli" ekanligiga ishonchni oshiradi.
3.  **Kalkulyator va Stop-Loss:**
    *   Xarajatlarni kiritishda raqamlar avtomat ravishda bo'shliqlar bilan ajratilishi kerak (masalan: `10 000 000` emas, `10 000 000`).
    *   Stop-Loss chizig'iga yetganda raqamlar qizarib, vizual ogohlantirish beradi.
4.  **Skeleton Loaders:**
    *   Ma'lumotlar backenddan kelguncha bo'sh ekran o'rniga, kelajakdagi kontent shaklidagi kulrang "skeletlar" (Skeleton loading) miltillab turadi. Bu UI'ni tezroq his qildiradi.

## 🛠️ 3. Texnik Tavsiyalar (Frontend Arxitekturasi)

Sifatli UI/UX'ni tez va xatosiz qurish uchun quyidagi stack'ni taklif qilaman:

1.  **Framework:** `React 18` + `Vite` (Tezkor ishlash va build qilish uchun).
2.  **Styling (Dizayn):** `Tailwind CSS`. Bu bizga siz xohlagan "premium" ko'rinishni nol noldan, o'zimiz xohlagan ranglar bilan tez qurishga imkon beradi.
3.  **UI Kutubxona:** `Shadcn UI` yoki `Radix UI`.
    *   *Nima uchun?* Biz tugmalar, modallar, dropdown'larni noldan yozib vaqt yo'qotmaymiz. Shadcn juda jiddiy, toza va minimalist dizaynga ega (xuddi Vercel yoki Stripe kabi).
4.  **Holatni boshqarish (State Management):** `Zustand` (Redux o'rniga). U yengilroq, kod yozish kamroq va MVP uchun ideal.
5.  **Ma'lumotlarni tortish (Data Fetching):** `React Query` (TanStack Query). Backend'dan ma'lumotlarni olish, keshga saqlash va xatoliklarni chiroyli boshqarish uchun.
6.  **PWA (Progressive Web App):** `vite-plugin-pwa` orqali ilovani telefonga o'rnatiladigan qilib sozlaymiz.

## 📝 User Review Required (Tasdiqlash)

> [!IMPORTANT]
> Dizayn va texnik tomondan qilingan ushbu tavsiyalar bo'yicha fikringizni bildiring:
> 1. **Dizayn Uslubi:** Shadcn UI + Tailwind CSS orqali qat'iy va minimalist (Stripe uslubidagi) dizayn qilishga rozimisiz?
> 2. **Ranglar:** Yuqorida taklif qilingan (Deep Blue, Emerald, Amber, Rose) palitrasini ma'qullaysizmi?
> 3. **Holatni boshqarish:** Redux Toolkit o'rniga zamonaviyroq va yengilroq `Zustand` kutubxonasini ishlatsak maylimi? (Bu kodlashni tezlashtiradi).
