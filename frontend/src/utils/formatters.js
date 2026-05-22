/**
 * TenderHelper AI — Formatters
 * ==============================
 * Raqamlar, sanalar va matnlarni formatlash uchun yordamchi funksiyalar.
 */

/**
 * Raqamni bo'shliqlar bilan formatlash: 10000000 → "10 000 000"
 */
export function formatNumber(num) {
  if (num === null || num === undefined) return '—';
  return Number(num).toLocaleString('uz-UZ').replace(/,/g, ' ');
}

/**
 * Pul miqdorini formatlash: 10000000 → "10 000 000 so'm"
 */
export function formatCurrency(amount, currency = 'UZS') {
  if (amount === null || amount === undefined) return '—';
  const formatted = formatNumber(Math.round(amount));
  return currency === 'UZS' ? `${formatted} so'm` : `$${formatted}`;
}

/**
 * Foizni formatlash: 0.85 → "85%"
 */
export function formatPercent(value) {
  if (value === null || value === undefined) return '—';
  return `${Math.round(value * 100)}%`;
}

/**
 * Sanani formatlash: "2026-06-15T10:30:00Z" → "15 iyun, 2026"
 */
export function formatDate(dateString) {
  if (!dateString) return '—';
  const date = new Date(dateString);
  const months = [
    'yanvar', 'fevral', 'mart', 'aprel', 'may', 'iyun',
    'iyul', 'avgust', 'sentabr', 'oktabr', 'noyabr', 'dekabr',
  ];
  return `${date.getDate()} ${months[date.getMonth()]}, ${date.getFullYear()}`;
}

/**
 * Qolgan kunlarni hisoblash: deadline sanasigacha necha kun qoldi
 */
export function daysUntil(dateString) {
  if (!dateString) return null;
  const now = new Date();
  const deadline = new Date(dateString);
  const diff = Math.ceil((deadline - now) / (1000 * 60 * 60 * 24));
  return diff;
}

/**
 * Qolgan kunlarni matn ko'rinishida: "3 kun qoldi" yoki "Muddati o'tdi"
 */
export function formatDeadline(dateString) {
  const days = daysUntil(dateString);
  if (days === null) return '—';
  if (days < 0) return 'Muddati o\'tdi';
  if (days === 0) return 'Bugun tugaydi';
  if (days === 1) return 'Ertaga tugaydi';
  return `${days} kun qoldi`;
}

/**
 * Telefon raqamini formatlash: "+998901234567" → "+998 90 123 45 67"
 */
export function formatPhone(phone) {
  if (!phone) return '—';
  const cleaned = phone.replace(/\D/g, '');
  if (cleaned.length === 12) {
    return `+${cleaned.slice(0, 3)} ${cleaned.slice(3, 5)} ${cleaned.slice(5, 8)} ${cleaned.slice(8, 10)} ${cleaned.slice(10)}`;
  }
  return phone;
}

/**
 * Matnni qisqartirish: "Bu juda uzun matn..." → "Bu juda uzun..."
 */
export function truncate(text, maxLength = 100) {
  if (!text) return '';
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength).trim() + '...';
}
