# TenderHelper Telegram Bot va Mini App Rejasi

**Versiya:** 1.0  
**Yangilangan:** 2026-06-18  
**Holat:** Backend data-contract modellari va invariant testlari mavjud;
bot runtime, linking endpointlari, HMAC `initData` verification va Mini App UI
hali implementatsiya qilinmagan.

## Maqsad

Telegram ekotizimi kompaniya xodimiga web workspace bilan bir xil company,
subscription va permission authority asosida tenderlarni ko'rish, AI tahlil
boshlash va bildirishnomalarni boshqarish imkonini beradi.

## Xavfsizlik Chegaralari

- Telegram username faqat display va discovery hint; identity authority emas.
- Verifikatsiyadan keyin Telegram numeric user ID canonical link hisoblanadi.
- Bot token faqat backend secret store/environmentda saqlanadi.
- Frontend yoki TMA hech qachon `initDataUnsafe`ga ishonmaydi.
- Har bir action backendda company membership, active status, subscription,
  STIR va explicit permission bo'yicha qayta tekshiriladi.

## Ma'lumot Modellari

| Model | Muhim maydonlar |
|---|---|
| `TelegramIdentity` | member, telegram_user_id, username, status, verified_at, relink_requested_at |
| `TelegramLinkChallenge` | member, token_hash, expires_at, attempts, consumed_at, requested_by |
| `TelegramMiniAppSession` | identity, init_data_hash, auth_date, last_active_at, device, revoked_at |
| `NotificationPreference` | member, event_type, enabled, threshold, quiet_hours |
| `NotificationDelivery` | member, event_key, channel, status, attempts, sent_at |

Integrity qoidalari:

- active Telegram numeric user ID faqat bitta active platform identityga tegishli;
- challenge raw tokeni database yoki logda saqlanmaydi;
- consumed/expired challenge qayta ishlatilmaydi;
- notification `event_key + member + channel` bo'yicha idempotent;
- identity unlink/revoke barcha TMA sessiyalarini yopadi.

## Link va Re-link Oqimi

1. Admin team member yaratishda ixtiyoriy `@username` hint kiritadi.
2. Backend bir martalik challenge yaratadi.
3. Xodim bot yoki TMA orqali challenge'ni tasdiqlaydi.
4. Backend Telegram tomonidan berilgan numeric IDni saqlaydi.
5. Username yangilansa numeric ID o'zgarmagan bo'lsa display qiymati yangilanadi.
6. Admin re-link boshlasa status `awaiting_new_session_verification` bo'ladi.
7. Boshqa numeric ID aniqlansa corporate password va step-up talab qilinadi.
8. Eski web/TMA sessiyalari revoke qilinadi va audit yoziladi.

## TMA Authentication

Backend raw Telegram WebApp `initData`ni qabul qiladi, Telegram HMAC
algoritmi bilan signature'ni, `auth_date` freshness'ni va replay
fingerprintni tekshiradi. Numeric ID active `TelegramIdentity` bilan
solishtirilgach, qisqa muddatli audience-scoped TMA session beriladi.

Mismatch holatida username orqali avtomatik link qilinmaydi. Corporate
password fallback faqat TLS orqali backend step-up endpointiga yuboriladi;
xato matni account mavjudligini oshkor qilmaydi.

## Permission Mapping

| TMA imkoniyati | Talab |
|---|---|
| Lotlarni ko'rish | `view_lots` |
| Deep AI analysis | `run_ai_analysis` va `use_analysis_quotas` |
| Hujjat yaratish | `generate_ai_contracts`, Business va STIR |
| Inline edit | TMA MVP'da read-only preview; webda `edit_inline_workspace` |
| Competitor metrics | `access_competitor_metrics`, Business va STIR |
| Team boshqaruvi | TMA MVP'da yo'q; webda `manage_team` |

## Notificationlar

- matching lot;
- deadline reminder;
- analysis completed/failed;
- document generation completed/failed;
- security va account-link eventlari.

Admin taqiqlagan yoki user permissioniga kirmaydigan toggle ko'rsatilmaydi.
Security notificationlari user tomonidan o'chirilmaydi.

## Session Lifecycle

- `Revoke Session / Terminate Access` web va TMA sessiyalarini birga bekor qiladi.
- Password change, membership deactivate, company revoke va Telegram unlink
  session versionini invalid qiladi.
- Device, last active, IP/proxy-aware metadata va revoke sababi auditlanadi.

## UI Scope

- landing bento kartasida Telegram Mini App ekotizimi;
- Team Hub member modalida Telegram username;
- member detailda identity status, numeric ID maskasi va re-link action;
- smartphone frame ichida safe initialization, permission-aware dashboard,
  notification toggles va mismatch fallback;
- statuslar: `not_linked`, `pending`, `verified`,
  `awaiting_new_session_verification`, `revoked`, `failed`.

## Delivery Ketma-ketligi

1. ADR va threat model.
2. Additive schema/migration.
3. Bot webhook va challenge service.
4. TMA auth endpoint va replay store.
5. Team API relink/unlink integration.
6. Notification preferences/delivery.
7. Permission-aware TMA frontend.
8. Security, integration va end-to-end test.
9. Staging bot/domain smoke test.
10. Production rollout va audit monitoring.

## Definition of Done

- forged, stale va replay `initData` testlari green;
- username takeover testi rad etiladi;
- permission va subscription gate web/TMAda bir xil;
- revoke barcha channel sessiyalariga darhol ta'sir qiladi;
- secret/log/PII audit o'tgan;
- notification retry duplicate yubormaydi;
- privacy/terms Telegram data processingni qamrab oladi.
