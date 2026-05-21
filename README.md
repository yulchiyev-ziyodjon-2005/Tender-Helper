# 🏛️ TenderHelper AI

**O'zbekiston kichik va o'rta biznesi uchun AI Tender Mentor platformasi**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Django](https://img.shields.io/badge/Django-5.0+-green.svg)](https://djangoproject.com)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://react.dev)
[![License](https://img.shields.io/badge/License-Private-red.svg)]()

---

## 📋 Loyiha Haqida

TenderHelper AI — davlat xaridlari va korporativ tenderlarda qatnashish jarayonini soddalashtiruvchi, sun'iy intellektga asoslangan mentor platformasi.

### Muammo
Kichik tadbirkorlar tender hujjatlarining murakkab yuridik tilini tushunmaydi, kerakli hujjatlarni bilmaydi, narx strategiyasida xato qiladi va yashirin shartlardan zarar ko'radi.

### Yechim
- 🔍 **AI Tender Tahlili** — tender matnini oddiy tilga o'giradi
- 📋 **Hujjatlar Checklist** — korxona turiga mos hujjatlar ro'yxati
- ⚠️ **Risk Aniqlash** — yashirin shartlar va Red Flag signallar
- 💰 **Smart Kalkulyator** — QQS, operator haqi, Stop-Loss narx hisoblash
- 👥 **Jamoaviy Ishlash** — Enterprise uchun team mode

---

## 🛠️ Tech Stack

| Qatlam | Texnologiya |
|--------|-------------|
| **Frontend** | React 18 + Vite + Tailwind CSS |
| **Backend** | Django 5.0 + Django REST Framework |
| **Database** | SQLite (MVP) → PostgreSQL (Production) |
| **AI** | Google Gemini API |
| **Auth** | JWT + Phone OTP + Google OAuth |
| **Mobile** | PWA (Progressive Web App) |

---

## 🚀 O'rnatish

### Talablar
- Python 3.11+
- Node.js 18+
- Git

### 1. Repozitoriyani klonlash
```bash
git clone <repo-url>
cd TenderHelper
```

### 2. Backend sozlash
```bash
# Virtual environment yaratish
cd backend
python -m venv venv

# Aktivlashtirish (Windows)
venv\Scripts\activate

# Aktivlashtirish (macOS/Linux)
source venv/bin/activate

# Dependencies o'rnatish
pip install -r requirements.txt

# .env faylni sozlash
cp ../.env.example ../.env
# .env faylni o'z API kalitlaringiz bilan to'ldiring

# Migratsiyalar
python manage.py migrate

# Superuser yaratish
python manage.py createsuperuser

# Server ishga tushirish
python manage.py runserver
```

### 3. Frontend sozlash
```bash
cd frontend

# Dependencies o'rnatish
npm install

# Dev server ishga tushirish
npm run dev
```

### 4. Brauzerda ochish
- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000/api/v1/
- **Admin Panel:** http://localhost:8000/admin/

---

## 📁 Loyiha Tuzilmasi

```
TenderHelper/
├── backend/          # Django 5.0 + DRF
│   ├── core/         # Project settings
│   ├── users/        # Auth (Phone OTP + Google)
│   ├── companies/    # Company profiles
│   ├── tenders/      # Tender lots & search
│   ├── analysis/     # AI analysis & calculator
│   ├── subscriptions/# Plans & payments
│   ├── teams/        # Team collaboration
│   └── competitors/  # Competitor intelligence
├── frontend/         # React 18 + Vite
│   └── src/
│       ├── api/      # API client
│       ├── store/    # Zustand stores
│       ├── components/
│       ├── pages/
│       └── routes/
├── docs/             # Documentation
├── TZ.md             # Texnik topshiriq
└── IMPLEMENTATION_PLAN.md
```

---

## 💰 Tarif Rejalari

| | Free | Pro | Enterprise |
|---|------|-----|------------|
| **Narx** | $0 | $15/oy | $50/oy |
| **AI Tahlil** | 4 ta/oy | Cheksiz | Cheksiz |
| **Kalkulyator** | ✅ | ✅ | ✅ |
| **Raqobatchi Razvedkasi** | ❌ | ❌ | ✅ |
| **Jamoaviy Ishlash** | ❌ | ❌ | ✅ |

---

## 📄 Litsenziya

Bu loyiha xususiy (private) litsenziya ostida. Barcha huquqlar himoyalangan.

---

## 👥 Jamoa

TenderHelper AI — O'zbekiston GovTech/LegalTech/FinTech startapi.
