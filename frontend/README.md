# TenderHelper Frontend

React 19, Vite 8, Tailwind CSS 4, React Router 7, TanStack Query va Zustand
asosidagi responsive SaaS frontend.

**Yangilangan:** 2026-06-15

## Implementatsiya Qilingan Yuzalar

- `/` - landing, dashboard preview, feature bento, pricing toggle va contacts;
- `/login` - split-screen secure login;
- `/register` - company/full name/email/phone/password signup;
- `/onboarding` - 9 xonali STIR lookup, editable registry draft yoki skip;
- `/terms` va `/privacy` - legal surfaces;
- `/dashboard`, `/analysis`, `/settings` - private workspace;
- `/team` - Business + STIR Team Hub;
- `/change-password` - invited memberning majburiy password checkpointi;
- `/superadmin` - privileged operational preview;
- `/auth/google/callback` - one-time exchange code callback.

Landing pricing contracti:

| Tarif | Oylik | Yillik |
|---|---:|---:|
| Free | 0 UZS | 0 UZS |
| Pro | 350,000 UZS | 3,360,000 UZS |
| Business | 950,000 UZS | 9,120,000 UZS |

## Auth va Security Contract

- `PrivateRoute` va `PublicRoute` auth holatini tekshiradi.
- Standard login access tokenni `sessionStorage`da saqlaydi.
- Faqat explicit `Remember me` tanlansa token `localStorage`da saqlanadi.
- Force-password-change flag token bilan bir xil storage lifecycle'ga ega.
- Google OAuth URL'da JWT olib yurmaydi; one-time exchange code ishlatiladi.
- 401/403 holatlari uchun typed error UI mavjud.
- Uzoq muddatli target: refresh tokenni Secure, HttpOnly, SameSite cookie'ga
  ko'chirish.

## Team Hub

Sidebar memberning backenddan kelgan explicit permissionlari asosida bo'limni
yashiradi yoki ko'rsatadi. UI gate yakuniy authority emas; backend har
requestda permission, company membership, subscription va STIRni tekshiradi.

Permissionlar:

- `view_lots`, `export_lot_data`;
- `run_ai_analysis`, `use_analysis_quotas`;
- `generate_ai_contracts`, `edit_inline_workspace`, `export_pdf_docx`;
- `access_competitor_metrics`, `manage_team`.

Member qo'shishda cryptographic temporary password backend tomonidan bir marta
qaytariladi. Session console device, browser, IP va last-active metadata
ko'rsatadi; revoke barcha accessni yopadi.

## Telegram Mini App

Telegram username, re-link UI, TMA smartphone viewport va notification hub hali
implementatsiya qilinmagan. Target flow
[`../docs/TELEGRAM_TMA_PLAN.md`](../docs/TELEGRAM_TMA_PLAN.md)da. Username
identity authority emas; server tomonidan verifikatsiya qilingan Telegram
numeric user ID ishlatiladi.

## Ishga Tushirish

```powershell
npm install
npm run dev
```

## Tekshiruv

```powershell
npm run lint
npm run build
```

Backend API contract smoke:

```powershell
# Backend alohida terminalda http://127.0.0.1:8000 da ishlayotgan bo'lishi kerak.
$env:API_CONTRACT_API_BASE_URL='http://127.0.0.1:8000/api/v1'
npm run contract:api

# Real login/session/team/admin contractlari uchun:
$env:API_CONTRACT_EMAIL='user@example.uz'
$env:API_CONTRACT_PASSWORD='strong-password'
npm run contract:api
```

Frontend API wrapperlari `src/api/endpoints.js`dagi canonical plural backend
contractdan foydalanadi. Yangi UI yuzasi endpoint qo'shsa, avval shu registry
yangilanadi, keyin `contract:api` smoke scriptga tekshiruv qo'shiladi.

Frontend environment:

```text
VITE_API_BASE_URL=http://localhost:8000/api/v1
```
