/**
 * TenderHelper AI — Constants
 * ============================
 * Loyiha bo'ylab ishlatiladigan barcha doimiy qiymatlar.
 */

// ──────────── API ────────────
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

// ──────────── Auth ────────────
// ──────────── Subscription Limits ────────────
export const TARIFF_LIMITS = {
  free: {
    label: 'Bepul',
    ai_analysis_monthly: 4,
    sms_allowed_monthly: 0,
    daily_sms_cap: 0,
  },
  pro: {
    label: 'Pro',
    ai_analysis_monthly: 100,
    sms_allowed_monthly: 100,
    daily_sms_cap: 5,
  },
  business: {
    label: 'Business',
    ai_analysis_monthly: 250,
    sms_allowed_monthly: 500,
    daily_sms_cap: 20,
  },
  enterprise: {
    label: 'Enterprise',
    ai_analysis_monthly: 500,
    sms_allowed_monthly: 500,
    daily_sms_cap: 20,
  },
};

export function resolveTariffLimits(planCode, entitlementPayload = null) {
  const fallback = TARIFF_LIMITS[planCode] || TARIFF_LIMITS.free;
  return {
    ...fallback,
    ...(entitlementPayload?.limits || {}),
  };
}

// ──────────── Pricing ────────────
export const PRICING = {
  free: { price_usd: 0, price_uzs: 0 },
  pro: { price_uzs: 350_000, annual_uzs: 3_360_000 },
  business: { price_uzs: 950_000, annual_uzs: 9_120_000 },
};

// ──────────── Company Types ────────────
export const COMPANY_TYPES = [
  { value: 'yatt', label: 'YaTT (Yakka tartibdagi tadbirkor)' },
  { value: 'mchj', label: 'MChJ (Mas\'uliyati cheklangan jamiyat)' },
  { value: 'aj', label: 'AJ (Aksiyadorlik jamiyati)' },
  { value: 'tt', label: 'TT (To\'liq sheriklik)' },
];

// ──────────── Industries ────────────
export const INDUSTRIES = [
  { value: 'qurilish', label: 'Qurilish', icon: '🏗️' },
  { value: 'it', label: 'IT va Texnologiya', icon: '💻' },
  { value: 'logistika', label: 'Logistika va Transport', icon: '🚛' },
  { value: 'tibbiyot', label: 'Tibbiyot', icon: '🏥' },
  { value: 'taminot', label: 'Ta\'minot va Savdo', icon: '📦' },
  { value: 'oziq_ovqat', label: 'Oziq-ovqat', icon: '🍞' },
  { value: 'xizmat', label: 'Xizmat ko\'rsatish', icon: '🛠️' },
  { value: 'boshqa', label: 'Boshqa', icon: '📋' },
];

// ──────────── Experience Levels ────────────
export const EXPERIENCE_LEVELS = [
  { value: 'beginner', label: 'Yangi boshlovchi', description: 'Tenderda hali qatnashmagan' },
  { value: 'intermediate', label: 'O\'rtacha', description: '1-5 ta tenderda qatnashgan' },
  { value: 'expert', label: 'Professional', description: '5+ tenderda qatnashgan' },
];

// ──────────── Tender Platforms ────────────
export const TENDER_PLATFORMS = [
  { value: 'xarid_uzex', label: 'xarid.uzex.uz' },
  { value: 'dxarid_uzex', label: 'dxarid.uzex.uz' },
  { value: 'exarid_uzex', label: 'exarid.uzex.uz' },
  { value: 'e_auksion', label: 'e-auksion.uz' },
  { value: 'manual', label: 'Qo\'lda kiritilgan' },
];

// ──────────── Analysis Statuses ────────────
export const ANALYSIS_STATUSES = {
  pending: { label: 'Kutilmoqda', color: 'text-surface-500' },
  processing_docs: { label: 'Hujjatlar yuklanmoqda', color: 'text-primary-500' },
  checking_compliance: { label: 'Talablar tahlil qilinmoqda', color: 'text-primary-600' },
  detecting_red_flags: { label: 'Red Flag tekshiruvi', color: 'text-warning-500' },
  completed: { label: 'Tayyor', color: 'text-success-500' },
  failed: { label: 'Xatolik', color: 'text-danger-500' },
};

// ──────────── Risk Levels ────────────
export const RISK_LEVELS = {
  blocker: { label: 'BLOKLAYDI', color: 'danger', icon: '🔴' },
  warning: { label: 'MUAMMO', color: 'warning', icon: '🟡' },
  info: { label: 'E\'TIBOR', color: 'success', icon: '🟢' },
};

// ──────────── Financial Constants ────────────
export const FINANCE = {
  VAT_RATE: 0.12,           // 12% QQS
  OPERATOR_FEE_RATE: 0.0015, // 0.15% UzEx
  ZAKALAT_RATE: 0.03,        // 3% zakalat
  DEFAULT_MARGIN: 0.15,      // 15% foyda marjasi
};

// ──────────── Regions ────────────
export const REGIONS = [
  'Toshkent shahri', 'Toshkent viloyati', 'Andijon', 'Buxoro',
  'Farg\'ona', 'Jizzax', 'Xorazm', 'Namangan', 'Navoiy',
  'Qashqadaryo', 'Samarqand', 'Sirdaryo', 'Surxondaryo',
  'Qoraqalpog\'iston Respublikasi',
];
