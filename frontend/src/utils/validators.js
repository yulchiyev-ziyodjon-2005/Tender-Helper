/**
 * TenderHelper AI — Validators
 * ==============================
 * Input validatsiya funksiyalari.
 */

/**
 * O'zbekiston telefon raqami validatsiyasi: +998XXXXXXXXX
 */
export function isValidPhone(phone) {
  if (!phone) return false;
  const cleaned = phone.replace(/\D/g, '');
  return /^998\d{9}$/.test(cleaned);
}

/**
 * STIR (INN) validatsiyasi: 9 raqamli
 */
export function isValidSTIR(stir) {
  if (!stir) return false;
  return /^\d{9}$/.test(stir.trim());
}

/**
 * Email validatsiyasi
 */
export function isValidEmail(email) {
  if (!email) return false;
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

/**
 * Bo'sh emasligini tekshirish
 */
export function isNotEmpty(value) {
  if (value === null || value === undefined) return false;
  if (typeof value === 'string') return value.trim().length > 0;
  return true;
}

/**
 * Narx validatsiyasi: musbat raqam
 */
export function isValidPrice(price) {
  const num = Number(price);
  return !isNaN(num) && num >= 0;
}
