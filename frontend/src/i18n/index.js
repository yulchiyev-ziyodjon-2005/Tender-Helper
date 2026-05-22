/**
 * TenderHelper AI — i18n Configuration
 * =======================================
 * 5 tilli qo'llab-quvvatlash: O'zbek, Rus, Ingliz, Qoraqalpoq, Tojik
 */

import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

// Tarjima fayllari
import uzCommon from './locales/uz/common.json';
import ruCommon from './locales/ru/common.json';
import enCommon from './locales/en/common.json';
import kaaCommon from './locales/kaa/common.json';
import tgCommon from './locales/tg/common.json';

// Mavjud tillar ro'yxati (UI'da ko'rsatish uchun)
export const LANGUAGES = [
  { code: 'uz', label: "O'zbek", flag: '🇺🇿', dir: 'ltr' },
  { code: 'ru', label: 'Русский', flag: '🇷🇺', dir: 'ltr' },
  { code: 'en', label: 'English', flag: '🇬🇧', dir: 'ltr' },
  { code: 'kaa', label: 'Қарақалпақ', flag: '🏳️', dir: 'ltr' },
  { code: 'tg', label: 'Тоҷикӣ', flag: '🇹🇯', dir: 'ltr' },
];

i18n
  .use(initReactI18next)
  .init({
    resources: {
      uz: { common: uzCommon },
      ru: { common: ruCommon },
      en: { common: enCommon },
      kaa: { common: kaaCommon },
      tg: { common: tgCommon },
    },

    // Default til — localStorage'dan yoki O'zbek
    lng: localStorage.getItem('language') || 'uz',

    // Agar tarjima topilmasa — O'zbek tilida ko'rsatish
    fallbackLng: 'uz',

    // Namespace konfiguratsiyasi
    ns: ['common'],
    defaultNS: 'common',

    interpolation: {
      escapeValue: false, // React allaqachon XSS himoya qiladi
    },

    // Debug (development'da yoqish mumkin)
    debug: false,
  });

/**
 * Tilni almashtirganda localStorage'ga saqlash
 */
export function changeLanguage(langCode) {
  i18n.changeLanguage(langCode);
  localStorage.setItem('language', langCode);

  // HTML lang atributini yangilash (SEO uchun)
  document.documentElement.lang = langCode;
}

export default i18n;
