# TenderHelper Frontend

React 19, Vite 8, Tailwind CSS 4, React Router 7, TanStack Query va Zustand
asosidagi demo/MVP frontend.

## Hozirgi Holat

Mavjud route'lar:

- `/`
- `/login`
- `/auth/google/callback`
- `/dashboard`
- `/analysis`
- `/settings`
- `/onboarding`

`PrivateRoute` va `PublicRoute` hozir vaqtincha auth tekshiruvini chetlab
o'tadi. JWT tokenlar `localStorage`da saqlanadi va Google callback tokenlarni
URL query orqali frontendga beradi. Bu demo holat; productiondan oldin
`Plan.md` Bosqich 0 bo'yicha route guard va xavfsiz auth oqimi joriy qilinadi.

Target ekranlar va komponentlar [`../DESIGN.md`](../DESIGN.md)da,
bosqichlar esa [`../IMPLEMENTATION_PLAN.md`](../IMPLEMENTATION_PLAN.md)da
belgilangan.

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

Frontend environment:

```text
VITE_API_BASE_URL=http://localhost:8000/api/v1
```
