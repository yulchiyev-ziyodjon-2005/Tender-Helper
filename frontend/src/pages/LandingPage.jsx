import { useState } from 'react';
import { Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ArrowRight,
  BellRing,
  Bot,
  Check,
  CheckCircle2,
  ChevronRight,
  Code2,
  Database,
  FilePenLine,
  Fingerprint,
  Globe2,
  Headphones,
  Mail,
  Menu,
  MessageCircle,
  Phone,
  Search,
  ShieldCheck,
  Sparkles,
  Trophy,
  X,
  Zap,
} from 'lucide-react';
import BrandMark from '../components/brand/BrandMark';
import DashboardPreview from '../components/marketing/DashboardPreview';
import ThemeToggle from '../components/ui/ThemeToggle';

const featureCards = [
  {
    icon: Search,
    eyebrow: 'Tenders · Search',
    title: 'Smart Matchmaking & Search',
    description: 'PostgreSQL ILIKE va trigram relevance orqali lotlarni kompaniya profili, hudud va tajriba bilan moslang.',
    className: 'lg:col-span-7',
    visual: (
      <div className="mt-8 rounded-2xl border border-slate-200 bg-white p-3 shadow-sm dark:border-white/10 dark:bg-white/[0.04]">
        <div className="flex items-center gap-2 rounded-xl border border-slate-200 px-3 py-2.5 dark:border-white/10">
          <Search className="h-4 w-4 text-blue-500" />
          <span className="text-xs text-slate-500">server infratuzilmasi</span>
          <span className="ml-auto rounded-md bg-blue-50 px-2 py-1 text-[10px] font-bold text-blue-600 dark:bg-blue-500/10 dark:text-blue-300">ILIKE + TRGM</span>
        </div>
        <div className="mt-3 grid gap-2 sm:grid-cols-3">
          {['94% match', 'Budget ↓', 'Page 1 / 18'].map((item) => (
            <span key={item} className="rounded-lg bg-slate-50 px-3 py-2 text-[10px] font-bold text-slate-600 dark:bg-white/5 dark:text-slate-300">{item}</span>
          ))}
        </div>
      </div>
    ),
  },
  {
    icon: Bot,
    eyebrow: 'Analysis · Citations',
    title: 'AI Tender Analysis & Citation Engine',
    description: 'Har bir risk xulosasini original hujjat sahifasi bilan bog‘lab, compliance checklistni tekshiradi.',
    className: 'lg:col-span-5',
    visual: (
      <div className="mt-8 space-y-2">
        {[
          ['Blocker', 'Bank kafolati muddati mos emas', 'bg-rose-500'],
          ['Warning', 'ISO sertifikat yangilanishi kerak', 'bg-amber-400'],
          ['Passed', 'Moliyaviy limit talabga mos', 'bg-emerald-400'],
        ].map(([status, text, color]) => (
          <div key={status} className="flex items-center gap-3 rounded-xl border border-slate-200 bg-white p-3 dark:border-white/10 dark:bg-white/[0.04]">
            <span className={`h-2.5 w-2.5 rounded-full ${color}`} />
            <span className="min-w-0 flex-1 truncate text-xs font-semibold">{text}</span>
            <span className="text-[10px] text-slate-400">p.12</span>
          </div>
        ))}
      </div>
    ),
  },
  {
    icon: FilePenLine,
    eyebrow: 'Documents · Workspace',
    title: 'AI Document Generator & Inline Editor',
    description: 'Tasdiqlangan kompaniya va tender ma’lumotlaridan compliance hujjatlarini dinamik yarating va bir joyda tahrirlang.',
    className: 'lg:col-span-5',
    visual: (
      <div className="mt-8 overflow-hidden rounded-2xl border border-slate-200 bg-white dark:border-white/10 dark:bg-white/[0.04]">
        <div className="flex items-center gap-1 border-b border-slate-200 p-2 dark:border-white/10">
          {['B', 'I', 'U'].map((item) => <span key={item} className="grid h-6 w-6 place-items-center rounded text-[10px] font-bold text-slate-500">{item}</span>)}
          <span className="ml-auto text-[9px] font-bold text-emerald-500">AUTOSAVED</span>
        </div>
        <div className="space-y-2 p-4">
          <div className="h-2 w-1/2 rounded bg-slate-300 dark:bg-slate-600" />
          <div className="h-1.5 w-full rounded bg-slate-100 dark:bg-white/10" />
          <div className="h-1.5 w-5/6 rounded bg-slate-100 dark:bg-white/10" />
          <span className="inline-flex rounded bg-cyan-100 px-1 text-[9px] text-cyan-800 dark:bg-cyan-400/20 dark:text-cyan-200">{'{{ company.director_name }}'}</span>
        </div>
      </div>
    ),
  },
  {
    icon: Trophy,
    eyebrow: 'Competitors · Intelligence',
    title: 'Competitor Intelligence Dashboard',
    description: 'Faqat yakunlangan tenderlardan rank, discount, sample size va win-rate ko‘rsatkichlarini hisoblang.',
    className: 'lg:col-span-7',
    visual: (
      <div className="mt-8 grid grid-cols-2 gap-2 sm:grid-cols-4">
        {[
          ['#3', 'Market rank'],
          ['-8.4%', 'Avg discount'],
          ['128', 'Sample size'],
          ['64%', 'Win rate'],
        ].map(([value, label]) => (
          <div key={label} className="rounded-xl border border-slate-200 bg-white p-3 dark:border-white/10 dark:bg-white/[0.04]">
            <p className="text-lg font-black tabular-nums">{value}</p>
            <p className="mt-1 text-[9px] uppercase tracking-wider text-slate-400">{label}</p>
          </div>
        ))}
      </div>
    ),
  },
];

const pricing = [
  {
    name: 'Free Tier',
    monthly: 0,
    description: 'Tender qidiruvini boshlayotgan kichik jamoalar uchun.',
    features: ['Basic lot search', 'Oyiga 4 ta AI tahlil', 'Basic calculator', '1 foydalanuvchi'],
    cta: 'Bepul boshlash',
  },
  {
    name: 'Pro Tier',
    monthly: 350000,
    annual: 3360000,
    description: 'Tahlil va xabarnomalarni tizimlashtirayotgan kompaniyalar uchun.',
    features: ['Cheksiz lot qidiruvi', 'Advanced AI pipelines', 'Real-time notifications', 'Deep insight alerts'],
    cta: 'Pro rejani boshlash',
  },
  {
    name: 'Business Tier',
    monthly: 950000,
    annual: 9120000,
    description: 'STIR tasdig‘i bilan hujjat, intelligence va enterprise team boshqaruvini birlashtiradi.',
    features: ['STIR (TIN) verification required', 'AI Document Generator + Inline Workspace', 'Competitor Intelligence baseline', 'Enterprise-grade Team Collaboration'],
    cta: 'Business tanlash',
    popular: true,
  },
];

function formatPrice(value) {
  return new Intl.NumberFormat('uz-UZ').format(value);
}

export default function LandingPage() {
  const [menuOpen, setMenuOpen] = useState(false);
  const [annual, setAnnual] = useState(true);

  return (
    <div className="overflow-hidden bg-white text-slate-950 dark:bg-[#050b14] dark:text-white">
      {/* WP0/WP8: public navigation and adaptive presentation shell. */}
      <header className="fixed inset-x-0 top-0 z-50 px-3 pt-3 sm:px-5">
        <nav className="mx-auto flex max-w-[1440px] items-center justify-between rounded-2xl border border-slate-200/80 bg-white/85 px-4 py-3 shadow-lg shadow-slate-900/5 backdrop-blur-xl dark:border-white/10 dark:bg-[#08111f]/85">
          <BrandMark />
          <div className="hidden items-center gap-8 lg:flex">
            {[
              ['Imkoniyatlar', '#features'],
              ['Narxlar', '#pricing'],
              ['Raqobatchilar', '#competitor-intel'],
            ].map(([label, href]) => (
              <a key={href} href={href} className="text-sm font-semibold text-slate-600 transition hover:text-blue-600 dark:text-slate-300 dark:hover:text-cyan-300">{label}</a>
            ))}
          </div>
          <div className="hidden items-center gap-2 lg:flex">
            <ThemeToggle />
            <Link to="/login" className="rounded-xl px-4 py-2.5 text-sm font-bold text-slate-700 transition hover:bg-slate-100 dark:text-slate-200 dark:hover:bg-white/5">Kirish</Link>
            <Link to="/register" className="rounded-xl bg-slate-950 px-5 py-2.5 text-sm font-bold text-white shadow-lg transition hover:bg-blue-600 dark:bg-white dark:text-slate-950 dark:hover:bg-cyan-300">Ro‘yxatdan o‘tish</Link>
          </div>
          <button type="button" className="grid h-10 w-10 place-items-center rounded-xl border border-slate-200 lg:hidden dark:border-white/10" onClick={() => setMenuOpen((value) => !value)} aria-label="Mobil menyuni ochish" aria-expanded={menuOpen}>
            {menuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
        </nav>
        <AnimatePresence>
          {menuOpen && (
            <motion.div initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -8 }} className="mx-auto mt-2 max-w-[1440px] rounded-2xl border border-slate-200 bg-white p-4 shadow-xl lg:hidden dark:border-white/10 dark:bg-[#08111f]">
              {[
                ['Imkoniyatlar', '#features'],
                ['Narxlar', '#pricing'],
                ['Raqobatchilar', '#competitor-intel'],
              ].map(([label, href]) => <a key={href} href={href} onClick={() => setMenuOpen(false)} className="block rounded-xl px-4 py-3 text-sm font-bold hover:bg-slate-50 dark:hover:bg-white/5">{label}</a>)}
              <div className="mt-3 grid grid-cols-2 gap-2 border-t border-slate-200 pt-4 dark:border-white/10">
                <Link to="/login" className="rounded-xl border border-slate-200 px-4 py-3 text-center text-sm font-bold dark:border-white/10">Kirish</Link>
                <Link to="/register" className="rounded-xl bg-blue-600 px-4 py-3 text-center text-sm font-bold text-white">Ro‘yxatdan o‘tish</Link>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </header>

      <main>
        <section className="relative overflow-hidden px-5 pb-24 pt-36 sm:pt-44">
          <div className="marketing-grid absolute inset-0 opacity-60 [mask-image:linear-gradient(to_bottom,black,transparent_85%)]" />
          <div className="absolute left-1/2 top-24 h-[520px] w-[900px] -translate-x-1/2 rounded-full bg-blue-500/10 blur-3xl dark:bg-blue-500/15" />
          <div className="relative mx-auto max-w-[1440px]">
            <motion.div initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }} className="mx-auto max-w-5xl text-center">
              <span className="inline-flex items-center gap-2 rounded-full border border-blue-200 bg-blue-50 px-3 py-1.5 text-xs font-extrabold uppercase tracking-[0.16em] text-blue-700 dark:border-cyan-400/20 dark:bg-cyan-400/10 dark:text-cyan-300">
                <Sparkles className="h-3.5 w-3.5" /> Built for Uzbekistan · Ready for global markets
              </span>
              <h1 className="text-balance mt-7 text-5xl font-black leading-[1.02] tracking-[-0.055em] sm:text-6xl lg:text-[82px]">
                AI-powered tender automation & <span className="bg-gradient-to-r from-blue-600 via-indigo-500 to-cyan-500 bg-clip-text text-transparent">matchmaking.</span>
              </h1>
              <p className="text-balance mx-auto mt-7 max-w-3xl text-base leading-7 text-slate-600 sm:text-xl sm:leading-8 dark:text-slate-300">
                Lotlarni topishdan boshlab, citation-first tahlil, hujjat tayyorlash va raqobatchilar intelligence’gacha bo‘lgan jarayonni bitta operatsion platformada boshqaring.
              </p>
              <div className="mt-9 flex flex-col justify-center gap-3 sm:flex-row">
                <Link to="/register" className="inline-flex items-center justify-center gap-2 rounded-2xl bg-blue-600 px-7 py-4 text-sm font-extrabold text-white shadow-xl shadow-blue-600/20 transition hover:-translate-y-0.5 hover:bg-blue-700">Bepul boshlash <ArrowRight className="h-4 w-4" /></Link>
                <a href="#features" className="inline-flex items-center justify-center gap-2 rounded-2xl border border-slate-200 bg-white px-7 py-4 text-sm font-extrabold transition hover:-translate-y-0.5 hover:border-slate-300 dark:border-white/10 dark:bg-white/5">Platformani ko‘rish <ChevronRight className="h-4 w-4" /></a>
              </div>
              <div className="mt-6 flex flex-wrap justify-center gap-x-6 gap-y-2 text-xs font-semibold text-slate-500">
                <span className="flex items-center gap-1.5"><CheckCircle2 className="h-4 w-4 text-emerald-500" /> Kredit karta talab qilinmaydi</span>
                <span className="flex items-center gap-1.5"><ShieldCheck className="h-4 w-4 text-emerald-500" /> Role-based access</span>
                <span className="flex items-center gap-1.5"><Fingerprint className="h-4 w-4 text-emerald-500" /> Audit-ready</span>
              </div>
            </motion.div>

            <motion.div initial={{ opacity: 0, y: 34, scale: 0.98 }} animate={{ opacity: 1, y: 0, scale: 1 }} transition={{ delay: 0.25, duration: 0.75 }} className="mx-auto mt-16 max-w-6xl">
              <DashboardPreview />
            </motion.div>

            <div className="mx-auto mt-14 grid max-w-5xl grid-cols-2 divide-x divide-slate-200 border-y border-slate-200 py-6 md:grid-cols-4 dark:divide-white/10 dark:border-white/10">
              {[
                ['12,000+', 'Tender tahlili'],
                ['4', 'Asosiy portal'],
                ['78%', 'O‘rtacha match'],
                ['500+', 'Kompaniya'],
              ].map(([value, label]) => (
                <div key={label} className="px-4 py-3 text-center">
                  <p className="text-2xl font-black tabular-nums sm:text-3xl">{value}</p>
                  <p className="mt-1 text-[10px] font-bold uppercase tracking-[0.16em] text-slate-400">{label}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* WP2-WP6: canonical product boundaries expressed as bento modules. */}
        <section id="features" className="scroll-mt-24 bg-slate-50 px-5 py-24 dark:bg-[#08111d]">
          <div className="mx-auto max-w-[1280px]">
            <div className="max-w-3xl">
              <p className="text-xs font-extrabold uppercase tracking-[0.22em] text-blue-600 dark:text-cyan-400">One connected workspace</p>
              <h2 className="text-balance mt-4 text-4xl font-black tracking-[-0.045em] sm:text-5xl">Har bir tender qarori uchun ishonchli signal.</h2>
              <p className="mt-5 text-base leading-7 text-slate-600 dark:text-slate-400">Users, companies, tenders, analysis, documents, competitors va subscriptions chegaralari aniq saqlangan.</p>
            </div>
            <div className="mt-12 grid gap-4 lg:grid-cols-12">
              {featureCards.map(({ icon: Icon, eyebrow, title, description, className, visual }) => (
                <article id={title.includes('Competitor') ? 'competitor-intel' : undefined} key={title} className={`${className} group scroll-mt-24 overflow-hidden rounded-[28px] border border-slate-200 bg-white p-6 transition duration-300 hover:-translate-y-1 hover:shadow-xl hover:shadow-slate-900/5 sm:p-8 dark:border-white/10 dark:bg-white/[0.025]`}>
                  <div className="flex items-start justify-between">
                    <span className="grid h-11 w-11 place-items-center rounded-2xl bg-slate-950 text-white transition group-hover:bg-blue-600 dark:bg-white dark:text-slate-950"><Icon className="h-5 w-5" /></span>
                    <span className="text-[9px] font-extrabold uppercase tracking-[0.2em] text-slate-400">{eyebrow}</span>
                  </div>
                  <h3 className="mt-8 text-2xl font-black tracking-[-0.035em]">{title}</h3>
                  <p className="mt-3 max-w-xl text-sm leading-6 text-slate-500 dark:text-slate-400">{description}</p>
                  {visual}
                </article>
              ))}
            </div>
          </div>
        </section>

        <section className="px-5 py-24">
          <div className="mx-auto grid max-w-[1280px] gap-12 lg:grid-cols-[.8fr_1.2fr] lg:items-center">
            <div>
              <span className="inline-flex items-center gap-2 text-xs font-extrabold uppercase tracking-[0.2em] text-blue-600 dark:text-cyan-400"><Database className="h-4 w-4" /> Data confidence layer</span>
              <h2 className="mt-4 text-4xl font-black tracking-[-0.045em] sm:text-5xl">Black-box emas. Har bir signal izohlanadi.</h2>
              <p className="mt-5 text-base leading-7 text-slate-600 dark:text-slate-400">AI natijalari citation, freshness va data quality indikatorlari bilan beriladi. Hujjat va competitor funksiyalari tasdiqlanmagan profil uchun aniq gated holatda qoladi.</p>
              <div className="mt-8 space-y-4">
                {[
                  [Code2, 'Citation-first analysis', 'Original fayl va sahifaga qaytish imkoniyati.'],
                  [Globe2, 'Uzbekistan registry workflow', 'STIR draft tasdiqlanmasdan profilga yozilmaydi.'],
                  [BellRing, 'Operational visibility', 'Stale va unavailable metrikalar yashirilmaydi.'],
                ].map(([Icon, title, text]) => (
                  <div key={title} className="flex gap-4">
                    <span className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-blue-50 text-blue-600 dark:bg-blue-500/10 dark:text-cyan-300"><Icon className="h-5 w-5" /></span>
                    <div><h3 className="text-sm font-extrabold">{title}</h3><p className="mt-1 text-sm text-slate-500">{text}</p></div>
                  </div>
                ))}
              </div>
            </div>
            <div className="rounded-[32px] border border-slate-200 bg-slate-950 p-4 text-white shadow-2xl dark:border-white/10">
              <div className="rounded-2xl border border-white/10 bg-[#0b1626] p-5">
                <div className="flex items-center justify-between"><span className="text-xs font-bold">Tender TH-2026-1842 · Evidence map</span><span className="rounded-full bg-emerald-400/10 px-2 py-1 text-[9px] font-bold text-emerald-300">CONFIDENCE 92%</span></div>
                <div className="mt-6 grid gap-3 sm:grid-cols-2">
                  {[
                    ['Eligibility', '12 / 13 passed', '98%', 'bg-emerald-400'],
                    ['Financial risk', '2 warnings', '74%', 'bg-amber-400'],
                    ['Document coverage', '31 citations', '91%', 'bg-cyan-400'],
                    ['Competitor data', '128 samples', '86%', 'bg-violet-400'],
                  ].map(([label, meta, score, color]) => (
                    <div key={label} className="rounded-xl border border-white/10 bg-white/[0.035] p-4">
                      <div className="flex justify-between text-xs"><span className="font-bold">{label}</span><span className="text-slate-400">{score}</span></div>
                      <p className="mt-2 text-[10px] text-slate-500">{meta}</p>
                      <div className="mt-4 h-1.5 rounded-full bg-white/10"><div className={`h-full rounded-full ${color}`} style={{ width: score }} /></div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* WP5: subscription presentation mirrors Free, Pro and Business entitlements. */}
        <section id="pricing" className="scroll-mt-24 bg-slate-50 px-5 py-24 dark:bg-[#08111d]">
          <div className="mx-auto max-w-[1280px]">
            <div className="mx-auto max-w-3xl text-center">
              <p className="text-xs font-extrabold uppercase tracking-[0.22em] text-blue-600 dark:text-cyan-400">Simple pricing</p>
              <h2 className="mt-4 text-4xl font-black tracking-[-0.045em] sm:text-5xl">Jamoangiz o‘sishi bilan kengayadi.</h2>
              <div className="mt-7 inline-flex rounded-2xl border border-slate-200 bg-white p-1 dark:border-white/10 dark:bg-white/5">
                <button type="button" onClick={() => setAnnual(false)} className={`rounded-xl px-4 py-2 text-xs font-extrabold transition ${!annual ? 'bg-slate-950 text-white dark:bg-white dark:text-slate-950' : 'text-slate-500'}`}>Oylik</button>
                <button type="button" onClick={() => setAnnual(true)} className={`rounded-xl px-4 py-2 text-xs font-extrabold transition ${annual ? 'bg-slate-950 text-white dark:bg-white dark:text-slate-950' : 'text-slate-500'}`}>Yillik <span className="ml-1 text-emerald-500">-20%</span></button>
              </div>
            </div>
            <div className="mt-12 grid gap-5 lg:grid-cols-3">
              {pricing.map((plan) => {
                const displayedPrice = annual ? (plan.annual ?? 0) : plan.monthly;
                return (
                  <article key={plan.name} className={`relative rounded-[28px] border p-7 ${plan.popular ? 'border-blue-500 bg-slate-950 text-white shadow-2xl shadow-blue-600/15 dark:bg-blue-600/10' : 'border-slate-200 bg-white dark:border-white/10 dark:bg-white/[0.025]'}`}>
                    {plan.popular && <span className="absolute right-5 top-5 rounded-full bg-cyan-300 px-3 py-1 text-[9px] font-black uppercase tracking-wider text-slate-950">Most popular</span>}
                    <h3 className="text-lg font-black">{plan.name}</h3>
                    <p className={`mt-3 min-h-12 text-sm leading-6 ${plan.popular ? 'text-slate-300' : 'text-slate-500'}`}>{plan.description}</p>
                    <div className="mt-7 flex items-end gap-2">
                      <span className="text-4xl font-black tabular-nums">{displayedPrice ? formatPrice(displayedPrice) : '0'}</span>
                      <span className={`pb-1 text-xs ${plan.popular ? 'text-slate-400' : 'text-slate-500'}`}>so‘m / {annual ? 'yil' : 'oy'}</span>
                    </div>
                    <Link to="/register" className={`mt-7 flex items-center justify-center rounded-xl px-4 py-3.5 text-sm font-extrabold transition ${plan.popular ? 'bg-cyan-300 text-slate-950 hover:bg-white' : 'bg-slate-950 text-white hover:bg-blue-600 dark:bg-white dark:text-slate-950'}`}>{plan.cta}</Link>
                    <div className={`my-7 border-t ${plan.popular ? 'border-white/10' : 'border-slate-200 dark:border-white/10'}`} />
                    <ul className="space-y-3">
                      {plan.features.map((item) => <li key={item} className={`flex items-start gap-2.5 text-sm ${plan.popular ? 'text-slate-200' : 'text-slate-600 dark:text-slate-300'}`}><Check className="mt-0.5 h-4 w-4 shrink-0 text-emerald-400" />{item}</li>)}
                    </ul>
                  </article>
                );
              })}
            </div>
          </div>
        </section>

        <section id="contact" className="scroll-mt-24 px-5 py-24">
          <div className="mx-auto grid max-w-[1280px] gap-10 rounded-[32px] border border-slate-200 bg-white p-6 sm:p-10 lg:grid-cols-[.85fr_1.15fr] dark:border-white/10 dark:bg-white/[0.025]">
            <div>
              <p className="text-xs font-extrabold uppercase tracking-[0.22em] text-blue-600 dark:text-cyan-400">Corporate contact</p>
              <h2 className="mt-4 text-4xl font-black tracking-[-0.045em]">Tender operatsiyangiz haqida gaplashamiz.</h2>
              <p className="mt-5 text-sm leading-7 text-slate-500">Tarif, STIR onboarding, Business Team Hub yoki korporativ joriy etish bo‘yicha rasmiy kanallardan bog‘laning.</p>
              <span className="mt-7 inline-flex items-center gap-2 rounded-full bg-emerald-50 px-3 py-1.5 text-[10px] font-black text-emerald-700 dark:bg-emerald-400/10 dark:text-emerald-300"><Headphones className="h-4 w-4" /> Business support · Uzbekistan</span>
            </div>
            <div className="grid gap-3 sm:grid-cols-2">
              {[
                [Mail, 'Corporate email', 'info@tenderhelperai.com', 'mailto:info@tenderhelperai.com'],
                [Phone, 'Hotline', '+998 (94) 994-05-04', 'tel:+998949940504'],
                [MessageCircle, 'Telegram channel', 'TenderHelper AI Channel', 'https://t.me/+fg-PELSnruU0NjVi'],
                [ShieldCheck, 'Direct admin support', '@Zdn_Ychv', 'https://t.me/Zdn_Ychv'],
              ].map(([Icon, label, value, href]) => (
                <a key={label} href={href} target={href.startsWith('http') ? '_blank' : undefined} rel={href.startsWith('http') ? 'noreferrer' : undefined} className="group rounded-2xl border border-slate-200 p-5 transition hover:-translate-y-1 hover:border-blue-300 hover:shadow-lg dark:border-white/10 dark:hover:border-cyan-400/30">
                  <span className="grid h-10 w-10 place-items-center rounded-xl bg-blue-50 text-blue-600 transition group-hover:bg-blue-600 group-hover:text-white dark:bg-cyan-400/10 dark:text-cyan-300"><Icon className="h-5 w-5" /></span>
                  <p className="mt-5 text-[10px] font-black uppercase tracking-wider text-slate-400">{label}</p>
                  <p className="mt-1 break-all text-sm font-black">{value}</p>
                </a>
              ))}
            </div>
          </div>
        </section>

        <section className="px-5 py-24">
          <div className="relative mx-auto max-w-[1280px] overflow-hidden rounded-[36px] bg-slate-950 px-6 py-16 text-center text-white sm:px-12">
            <div className="marketing-grid absolute inset-0 opacity-30" />
            <div className="relative">
              <Zap className="mx-auto h-8 w-8 text-cyan-300" />
              <h2 className="text-balance mx-auto mt-6 max-w-3xl text-4xl font-black tracking-[-0.045em] sm:text-5xl">Tender operatsiyangizni AI bilan tizimlashtiring.</h2>
              <p className="mx-auto mt-5 max-w-2xl text-sm leading-7 text-slate-300">Birinchi 4 ta tahlil bepul. STIR’ni hozir yoki keyinroq tasdiqlashingiz mumkin.</p>
              <Link to="/register" className="mt-8 inline-flex items-center gap-2 rounded-2xl bg-cyan-300 px-7 py-4 text-sm font-black text-slate-950 transition hover:bg-white">Hisob yaratish <ArrowRight className="h-4 w-4" /></Link>
            </div>
          </div>
        </section>
      </main>

      <footer className="border-t border-slate-200 px-5 py-12 dark:border-white/10">
        <div className="mx-auto grid max-w-[1280px] gap-10 lg:grid-cols-[1.4fr_repeat(3,1fr)]">
          <div><BrandMark /><p className="mt-5 max-w-sm text-sm leading-6 text-slate-500">Tender automation, explainable AI analysis va B2B intelligence platformasi.</p><a href="mailto:info@tenderhelperai.com" className="mt-4 block text-sm font-bold text-blue-600 dark:text-cyan-300">info@tenderhelperai.com</a><a href="tel:+998949940504" className="mt-2 block text-sm font-bold">+998 (94) 994-05-04</a><span className="mt-5 inline-flex items-center gap-2 rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1.5 text-[10px] font-bold text-emerald-700 dark:border-emerald-400/20 dark:bg-emerald-400/10 dark:text-emerald-300"><i className="h-2 w-2 rounded-full bg-emerald-500" /> All systems operational</span></div>
          {[
            ['Mahsulot', [['Imkoniyatlar', '#features'], ['Narxlar', '#pricing'], ['Raqobatchilar', '#competitor-intel'], ['Hisob yaratish', '/register']]],
            ['Yordam', [['Bog‘lanish', '#contact'], ['Tizimga kirish', '/login'], ['Parolni tiklash', '/forgot-password'], ['Korporativ email', 'mailto:info@tenderhelperai.com']]],
            ['Huquqiy', [['Foydalanish shartlari', '/terms'], ['Maxfiylik', '/privacy'], ['AI disclaimer', '/terms'], ['Ma’lumotlarni qayta ishlash', '/privacy']]],
          ].map(([title, items]) => (
            <div key={title}>
              <h3 className="text-xs font-black uppercase tracking-[0.16em]">{title}</h3>
              <ul className="mt-4 space-y-3">
                {items.map(([label, href]) => (
                  <li key={label}>
                    {href.startsWith('#') || href.startsWith('mailto:') ? (
                      <a href={href} className="text-sm text-slate-500 transition hover:text-blue-600 dark:hover:text-cyan-300">{label}</a>
                    ) : (
                      <Link to={href} className="text-sm text-slate-500 transition hover:text-blue-600 dark:hover:text-cyan-300">{label}</Link>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
        <div className="mx-auto mt-10 flex max-w-[1280px] flex-col gap-3 border-t border-slate-200 pt-6 text-xs text-slate-400 sm:flex-row sm:justify-between dark:border-white/10"><span>© 2026 Tender-Helper AI. All rights reserved.</span><span>Uzbekistan · Global-ready infrastructure</span></div>
      </footer>
    </div>
  );
}
