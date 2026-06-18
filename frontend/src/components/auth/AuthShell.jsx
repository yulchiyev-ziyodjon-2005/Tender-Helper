import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, CheckCircle2, Quote, ShieldCheck, Sparkles } from 'lucide-react';
import BrandMark from '../brand/BrandMark';
import ThemeToggle from '../ui/ThemeToggle';

export default function AuthShell({ children, eyebrow, title, description }) {
  const proof = [
    {
      quote: 'Citation-first tahlil tender komissiyasi talablarini jamoamiz uchun tushunarli vazifalarga aylantirdi.',
      author: 'Operations Manager',
      company: 'Technology Supplier · Tashkent',
    },
    {
      quote: 'STIR registry draft va permission-based team workspace ichki nazoratimizni bir joyga jamladi.',
      author: 'Commercial Director',
      company: 'Business Services · Uzbekistan',
    },
    {
      quote: 'Raqobatchilar statistikasi faqat yakunlangan natijalarga tayangani qaror sifatini sezilarli oshirdi.',
      author: 'Tender Lead',
      company: 'Industrial Procurement Team',
    },
  ];
  const [proofIndex, setProofIndex] = useState(0);

  useEffect(() => {
    const timer = window.setInterval(
      () => setProofIndex((current) => (current + 1) % proof.length),
      6000,
    );
    return () => window.clearInterval(timer);
  }, [proof.length]);

  return (
    <main className="min-h-screen bg-slate-50 text-slate-950 dark:bg-slate-950 dark:text-white">
      <div className="grid min-h-screen lg:grid-cols-[minmax(0,1.08fr)_minmax(480px,.92fr)]">
        <section className="relative hidden overflow-hidden bg-[#07111f] p-10 text-white lg:flex lg:flex-col xl:p-14">
          <div className="absolute inset-0 auth-grid opacity-40" />
          <div className="absolute -left-24 top-24 h-72 w-72 rounded-full bg-blue-600/30 blur-3xl" />
          <div className="absolute bottom-0 right-0 h-96 w-96 rounded-full bg-cyan-500/20 blur-3xl" />

          <div className="relative z-10"><BrandMark inverse /></div>
          <div className="relative z-10 my-auto max-w-xl py-16">
            <span className="inline-flex items-center gap-2 rounded-full border border-cyan-400/20 bg-cyan-400/10 px-3 py-1.5 text-xs font-bold uppercase tracking-[0.2em] text-cyan-300">
              <Sparkles className="h-3.5 w-3.5" /> Canonical Plan v1.3
            </span>
            <h1 className="mt-7 text-4xl font-black leading-tight tracking-[-0.04em] xl:text-6xl">
              Tender qarorlarini <span className="text-cyan-300">ishonchli data</span> bilan tezlashtiring.
            </h1>
            <p className="mt-6 max-w-lg text-base leading-7 text-slate-300 xl:text-lg">
              Qidiruv, AI tahlil, hujjat yaratish va raqobatchilar razvedkasi bitta xavfsiz ish maydonida.
            </p>

            <div className="mt-10 grid gap-3 sm:grid-cols-2">
              {[
                'Citation-first AI tahlil',
                'Registry orqali STIR tasdiqlash',
                'Role-based team workspace',
                'Append-only admin audit',
              ].map((item) => (
                <div key={item} className="flex items-center gap-2 text-sm text-slate-200">
                  <CheckCircle2 className="h-4 w-4 text-cyan-300" /> {item}
                </div>
              ))}
            </div>

            <div className="mt-10 rounded-2xl border border-white/10 bg-white/[0.045] p-5 backdrop-blur">
              <Quote className="h-5 w-5 text-cyan-300" />
              <p className="mt-4 min-h-20 text-sm leading-6 text-slate-200">{proof[proofIndex].quote}</p>
              <div className="mt-4 flex items-end justify-between gap-4">
                <div><p className="text-xs font-black">{proof[proofIndex].author}</p><p className="mt-1 text-[10px] text-slate-500">{proof[proofIndex].company}</p></div>
                <div className="flex gap-1.5">{proof.map((item, index) => <button key={item.author} type="button" onClick={() => setProofIndex(index)} className={`h-1.5 rounded-full transition-all ${index === proofIndex ? 'w-6 bg-cyan-300' : 'w-1.5 bg-white/20'}`} aria-label={`${index + 1}-social proof`} />)}</div>
              </div>
            </div>
          </div>

          <div className="relative z-10 flex items-center justify-between border-t border-white/10 pt-6 text-xs text-slate-400">
            <span>12,000+ tender tahlil qilingan</span>
            <span className="inline-flex items-center gap-2"><ShieldCheck className="h-4 w-4 text-emerald-400" /> Secure by design</span>
          </div>
        </section>

        <section className="flex min-h-screen flex-col">
          <header className="flex items-center justify-between px-5 py-5 sm:px-8">
            <div className="lg:hidden"><BrandMark /></div>
            <Link to="/" className="hidden items-center gap-2 text-sm font-semibold text-slate-500 transition hover:text-slate-950 lg:flex dark:hover:text-white">
              <ArrowLeft className="h-4 w-4" /> Bosh sahifa
            </Link>
            <ThemeToggle />
          </header>

          <div className="flex flex-1 items-center justify-center px-5 py-8 sm:px-8">
            <div className="w-full max-w-[560px]">
              <div className="mb-7">
                <p className="text-xs font-extrabold uppercase tracking-[0.22em] text-blue-600 dark:text-cyan-400">{eyebrow}</p>
                <h2 className="mt-3 text-3xl font-black tracking-[-0.035em] sm:text-4xl">{title}</h2>
                <p className="mt-3 max-w-lg text-sm leading-6 text-slate-500 dark:text-slate-400">{description}</p>
              </div>
              {children}
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}
