# ADR-018: Telegram Mini App Identity va Session Security

**Status:** Qabul qilingan reja  
**Sana:** 2026-06-15

## Kontekst

Telegram username o'zgaradi va qayta taqsimlanishi mumkin. Uni account
identity sifatida qabul qilish account takeover xavfini yaratadi. Telegram
Mini App `initData` ham server tekshiruvisiz ishonchli emas.

## Qaror

- Telegram numeric user ID verifikatsiyadan keyingi canonical identity.
- Username faqat display va linking hint.
- `initData` serverda Telegram HMAC algoritmi bilan tekshiriladi.
- `auth_date` freshness va replay fingerprint majburiy.
- Link/re-link bir martalik, hash qilingan, expiring challenge orqali.
- Numeric ID mismatch corporate password va step-up re-auth talab qiladi.
- TMA session alohida audience va qisqa TTLga ega.
- Membership yoki session revoke web va TMA accessni birga yopadi.
- Barcha link, relink, unlink, mismatch va revoke eventlari auditlanadi.

## Rad Etilgan Variantlar

- Faqat `@username` bo'yicha avtomatik link.
- Client-side `initDataUnsafe`ga ishonish.
- Bot token yoki HMAC secretini frontend bundle ichiga joylash.
- TMA permissionlarini faqat UI orqali yashirish.

## Oqibatlar

Qo'shimcha identity, challenge va session modellari hamda replay store kerak.
Evaziga username o'zgarishi accessni o'z-o'zidan ko'chirmaydi va backend
barcha ruxsatlar uchun yagona authority bo'lib qoladi.
