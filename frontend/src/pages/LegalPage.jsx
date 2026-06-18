import { Link, useLocation } from 'react-router-dom';
import { ArrowLeft, Mail, ShieldCheck } from 'lucide-react';
import BrandMark from '../components/brand/BrandMark';
import ThemeToggle from '../components/ui/ThemeToggle';

const content = {
  '/terms': {
    eyebrow: 'Legal · Terms of Service',
    title: 'Foydalanish shartlari',
    intro: 'Tender-Helper AI xizmatidan foydalanish, hisob xavfsizligi va platforma cheklovlari bo‘yicha asosiy qoidalar.',
    sections: [
      ['Hisob va vakolatlar', 'Tashkilot administratori xodim rollari, permission flaglari va seatlardan foydalanish uchun javobgar. Login ma’lumotlarini ulashish taqiqlanadi.'],
      ['AI natijalari', 'AI tahlil, citation, risk score va generated documentlar yordamchi material hisoblanadi. Ular yuridik, moliyaviy yoki davlat organining rasmiy xulosasi emas.'],
      ['STIR va registry', 'Registry lookup natijasi foydalanuvchi tasdiqlamaguncha draft hisoblanadi. Noto‘g‘ri yoki eskirgan ma’lumot uchun foydalanuvchi yakuniy tekshiruv o‘tkazishi kerak.'],
      ['Tarif va fair use', 'Free, Pro va Business funksiyalari entitlement va fair-use limitlari asosida taqdim etiladi. Business hujjat funksiyalari STIR tasdig‘ini talab qiladi.'],
      ['Taqiqlangan foydalanish', 'Xizmatdan ruxsatsiz scraping, zararli kod yuborish, boshqa tashkilot ma’lumotiga kirish yoki xavfsizlik nazoratini chetlab o‘tish uchun foydalanish mumkin emas.'],
      ['Xizmat mavjudligi', 'Provider, registry, payment yoki davlat portalidagi uzilishlar ayrim funksiyalarga ta’sir qilishi mumkin. Stale va unavailable holatlar interfeysda ochiq ko‘rsatiladi.'],
    ],
  },
  '/privacy': {
    eyebrow: 'Legal · Privacy Policy',
    title: 'Maxfiylik siyosati',
    intro: 'Identity, kompaniya, tender va operatsion audit ma’lumotlarini qayta ishlash bo‘yicha platforma tamoyillari.',
    sections: [
      ['Yig‘iladigan ma’lumotlar', 'Hisob identifikatorlari, kompaniya profili, STIR draftlari, foydalanish metrikalari, qurilma/IP session metadata va audit eventlari xizmatni taqdim etish uchun qayta ishlanadi.'],
      ['Qayta ishlash maqsadi', 'Ma’lumotlar autentifikatsiya, tender matchmaking, AI tahlil, hujjat yaratish, subscription enforcement, support va security monitoring uchun ishlatiladi.'],
      ['Role-based access', 'Korporativ ma’lumotlar company membership va explicit permissionlar bilan cheklanadi. Superadmin PII ko‘rinishi default maskalangan va reveal amali auditlanadi.'],
      ['Xavfsizlik', 'TLS, secure deployment sozlamalari, versioned JWT revoke, majburiy password change va MFA step-up kabi nazoratlar qo‘llanadi. Hech bir tizim mutlaq xavfsizlikni kafolatlamaydi.'],
      ['Saqlash muddati', 'Ma’lumotlar xizmat, audit va qonuniy majburiyatlar uchun zarur muddat saqlanadi. Retention muddati ma’lumot turi va amaldagi shartnomaga bog‘liq.'],
      ['Foydalanuvchi murojaati', 'Korporativ ma’lumot bo‘yicha access, correction yoki deletion so‘rovlari tashkilot administratori orqali rasmiy support kanaliga yuboriladi.'],
    ],
  },
};

export default function LegalPage() {
  const { pathname } = useLocation();
  const page = content[pathname] || content['/terms'];

  return (
    <main className="min-h-screen bg-slate-50 text-slate-950 dark:bg-[#050b14] dark:text-white">
      <header className="border-b border-slate-200 bg-white px-5 py-4 dark:border-white/10 dark:bg-[#08111f]">
        <div className="mx-auto flex max-w-4xl items-center justify-between"><BrandMark /><ThemeToggle /></div>
      </header>
      <article className="mx-auto max-w-4xl px-5 py-14 sm:py-20">
        <Link to="/" className="inline-flex items-center gap-2 text-sm font-bold text-slate-500 hover:text-blue-600"><ArrowLeft className="h-4 w-4" /> Bosh sahifa</Link>
        <p className="mt-10 text-xs font-black uppercase tracking-[0.2em] text-blue-600 dark:text-cyan-300">{page.eyebrow}</p>
        <h1 className="mt-4 text-4xl font-black tracking-[-0.045em] sm:text-5xl">{page.title}</h1>
        <p className="mt-5 max-w-2xl text-base leading-7 text-slate-500">{page.intro}</p>
        <div className="mt-10 space-y-4">
          {page.sections.map(([title, text]) => (
            <section key={title} className="rounded-2xl border border-slate-200 bg-white p-6 dark:border-white/10 dark:bg-white/[0.025]">
              <h2 className="flex items-center gap-2 text-base font-black"><ShieldCheck className="h-5 w-5 text-emerald-500" />{title}</h2>
              <p className="mt-3 text-sm leading-7 text-slate-500">{text}</p>
            </section>
          ))}
        </div>
        <div className="mt-8 flex flex-col gap-3 rounded-2xl border border-blue-200 bg-blue-50 p-5 text-sm sm:flex-row sm:items-center sm:justify-between dark:border-cyan-400/20 dark:bg-cyan-400/10">
          <span><b>Yuridik yoki privacy murojaati:</b> info@tenderhelperai.com</span>
          <a href="mailto:info@tenderhelperai.com" className="inline-flex items-center gap-2 font-black text-blue-700 dark:text-cyan-300"><Mail className="h-4 w-4" /> Email yuborish</a>
        </div>
        <p className="mt-6 text-xs leading-5 text-slate-400">Last updated: June 14, 2026. Ushbu mahsulot matni production rollout oldidan mahalliy yuridik ekspert tomonidan yakuniy tasdiqlanishi kerak.</p>
      </article>
    </main>
  );
}
