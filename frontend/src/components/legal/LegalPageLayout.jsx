import { Link } from 'react-router-dom';
import {
  ArrowLeft,
  ExternalLink,
  Mail,
  Scale,
  ShieldCheck,
} from 'lucide-react';
import BrandMark from '../brand/BrandMark';
import ThemeToggle from '../ui/ThemeToggle';

export default function LegalPageLayout({
  eyebrow,
  title,
  summary,
  lastUpdated,
  sections,
}) {
  return (
    <main className="min-h-screen bg-slate-50 text-slate-950 dark:bg-[#050b14] dark:text-white">
      <header className="sticky top-0 z-40 border-b border-slate-200/80 bg-white/90 px-5 py-4 backdrop-blur-xl dark:border-white/10 dark:bg-[#08111f]/90">
        <div className="mx-auto flex max-w-6xl items-center justify-between">
          <BrandMark />
          <div className="flex items-center gap-2">
            <Link to="/" className="hidden items-center gap-2 rounded-xl px-3 py-2 text-sm font-bold text-slate-500 transition hover:bg-slate-100 hover:text-blue-600 sm:inline-flex dark:hover:bg-white/5 dark:hover:text-cyan-300">
              <ArrowLeft className="h-4 w-4" /> Bosh sahifa
            </Link>
            <ThemeToggle />
          </div>
        </div>
      </header>

      <article className="mx-auto max-w-6xl px-5 py-12 sm:py-16 lg:py-20">
        <div className="grid gap-10 lg:grid-cols-[minmax(0,1fr)_280px] lg:items-start">
          <div>
            <div className="rounded-[28px] border border-slate-200 bg-white p-6 shadow-xl shadow-slate-900/5 sm:p-10 dark:border-white/10 dark:bg-white/[0.025]">
              <span className="inline-flex items-center gap-2 rounded-full border border-blue-200 bg-blue-50 px-3 py-1.5 text-xs font-black uppercase tracking-[0.18em] text-blue-700 dark:border-cyan-400/20 dark:bg-cyan-400/10 dark:text-cyan-300">
                <Scale className="h-3.5 w-3.5" /> {eyebrow}
              </span>
              <h1 className="mt-6 text-balance text-4xl font-black tracking-[-0.045em] sm:text-5xl lg:text-6xl">{title}</h1>
              <p className="mt-6 max-w-3xl text-base leading-8 text-slate-600 dark:text-slate-300">{summary}</p>
              <div className="mt-7 flex flex-wrap gap-3 text-xs font-bold text-slate-500">
                <span className="rounded-full bg-slate-100 px-3 py-1.5 dark:bg-white/5">Last Updated: {lastUpdated}</span>
                <a href="https://tenderhelperai.com" className="inline-flex items-center gap-1.5 rounded-full bg-slate-100 px-3 py-1.5 transition hover:text-blue-600 dark:bg-white/5 dark:hover:text-cyan-300">
                  tenderhelperai.com <ExternalLink className="h-3.5 w-3.5" />
                </a>
              </div>
            </div>

            <div className="mt-6 space-y-4">
              {sections.map(({ id, title: sectionTitle, content }) => (
                <section id={id} key={id} className="scroll-mt-28 rounded-2xl border border-slate-200 bg-white p-6 sm:p-8 dark:border-white/10 dark:bg-white/[0.025]">
                  <h2 className="flex items-start gap-3 text-xl font-black tracking-tight">
                    <ShieldCheck className="mt-0.5 h-5 w-5 shrink-0 text-emerald-500" />
                    {sectionTitle}
                  </h2>
                  <div className="mt-4 space-y-4 text-sm leading-7 text-slate-600 dark:text-slate-300">{content}</div>
                </section>
              ))}
            </div>
          </div>

          <aside className="lg:sticky lg:top-28">
            <div className="rounded-2xl border border-slate-200 bg-white p-5 dark:border-white/10 dark:bg-white/[0.025]">
              <p className="text-xs font-black uppercase tracking-[0.16em] text-slate-400">Mundarija</p>
              <nav className="mt-4 space-y-1" aria-label={`${title} mundarijasi`}>
                {sections.map(({ id, title: sectionTitle }) => (
                  <a key={id} href={`#${id}`} className="block rounded-lg px-3 py-2 text-sm font-semibold text-slate-500 transition hover:bg-blue-50 hover:text-blue-700 dark:hover:bg-cyan-400/10 dark:hover:text-cyan-300">
                    {sectionTitle}
                  </a>
                ))}
              </nav>
            </div>
            <div className="mt-4 rounded-2xl border border-blue-200 bg-blue-50 p-5 dark:border-cyan-400/20 dark:bg-cyan-400/10">
              <p className="text-sm font-black">Huquqiy yoki maxfiylik murojaati</p>
              <a href="mailto:info@tenderhelperai.com" className="mt-3 inline-flex items-center gap-2 text-sm font-bold text-blue-700 dark:text-cyan-300">
                <Mail className="h-4 w-4" /> info@tenderhelperai.com
              </a>
            </div>
          </aside>
        </div>
      </article>
    </main>
  );
}
