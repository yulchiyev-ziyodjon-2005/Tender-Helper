import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

const resources = {
  uz: {
    translation: {
      "app_title": "TenderHelper AI",
      "free_plan": "Bepul Tarif",
      "search_placeholder": "Masalan: 24110012 yoki https://xarid.uzex.uz/...",
      "analyze_btn": "Tahlil qilish",
      "active_tenders": "Faol tenderlar",
      "my_analyses": "Tahlillarim",
      "avg_match": "O'rtacha moslik",
      "filters": "Filtrlar",
      "platform": "Platforma",
      "all": "Barchasi",
      "start_price": "Boshlang'ich Narx",
      "from": "Dan",
      "to": "Gacha",
      "category": "Soha / Kategoriya",
      "apply_filter": "Filtrni qo'llash",
      "results_count": "{{count}} ta natija",
      "loading_tenders": "Tenderlar yuklanmoqda...",
      "no_tenders": "Hozircha tenderlar topilmadi",
      "days_left": "{{count}} kun qoldi",
      "expired": "Muddati o'tgan",
      "customer_not_specified": "Buyurtmachi nomi ko'rsatilmagan",
      "red_flags": "Yashirin xatarlar",
      "missing_docs": "Kerakli Hujjatlar",
      "standards": "Standartlar",
      "tech_reqs": "Texnik Talablar",
      "recommendation": "Tavsiya",
      "next_steps": "Keyingi qadamlar",
      "calculator": "Aqlli Kalkulyator",
      "net_profit": "Sof Foyda",
      "ai_analysis": "AI Xulosasi",
      "match": "Moslik",
      "customer": "Buyurtmachi",
      "ai_recommendation": "AI Tavsiyasi",
      "no_red_flags": "Ushbu tenderda yashirin xatarlar aniqlanmadi."
    }
  },
  ru: {
    translation: {
      "app_title": "TenderHelper AI",
      "free_plan": "Бесплатный план",
      "search_placeholder": "Например: 24110012 или https://xarid.uzex.uz/...",
      "analyze_btn": "Анализировать",
      "active_tenders": "Активные тендеры",
      "my_analyses": "Мои анализы",
      "avg_match": "Ср. совпадение",
      "filters": "Фильтры",
      "platform": "Платформа",
      "all": "Все",
      "start_price": "Начальная цена",
      "from": "От",
      "to": "До",
      "category": "Отрасль / Категория",
      "apply_filter": "Применить фильтр",
      "results_count": "Результатов: {{count}}",
      "loading_tenders": "Загрузка тендеров...",
      "no_tenders": "Тендеры пока не найдены",
      "days_left": "Осталось: {{count}} дн.",
      "expired": "Просрочено",
      "customer_not_specified": "Заказчик не указан",
      "red_flags": "Скрытые риски",
      "missing_docs": "Требуемые документы",
      "standards": "Стандарты",
      "tech_reqs": "Технические требования",
      "recommendation": "Рекомендация",
      "next_steps": "Следующие шаги",
      "calculator": "Умный калькулятор",
      "net_profit": "Чистая прибыль",
      "ai_analysis": "Резюме ИИ",
      "match": "Совпадение",
      "customer": "Заказчик",
      "ai_recommendation": "Рекомендация ИИ",
      "no_red_flags": "В этом тендере скрытых рисков не обнаружено."
    }
  }
};

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: 'uz',
    interpolation: {
      escapeValue: false 
    }
  });

export default i18n;
