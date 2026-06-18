import {
  Activity,
  ArrowUpRight,
  Bot,
  CheckCircle2,
  Clock3,
  Database,
  FileSearch,
  LayoutDashboard,
  Search,
  ShieldAlert,
  Trophy,
} from 'lucide-react';

const lots = [
  { title: 'Server infratuzilmasi modernizatsiyasi', source: 'xarid.uzex.uz', score: 94, amount: '1.84 mlrd' },
  { title: 'Tibbiy diagnostika uskunalari', source: 'dxarid.uzex.uz', score: 87, amount: '720 mln' },
  { title: 'Bulutli backup va DR xizmati', source: 'etender.uz', score: 81, amount: '486 mln' },
];

export default function DashboardPreview() {
  return (
    <div className="dashboard-glow relative overflow-hidden rounded-[28px] border border-white/10 bg-[#0a1423] text-white">
      <div className="flex items-center justify-between border-b border-white/10 px-4 py-3 sm:px-6">
        <div className="flex items-center gap-2">
          <span className="h-2.5 w-2.5 rounded-full bg-rose-400/80" />
          <span className="h-2.5 w-2.5 rounded-full bg-amber-300/80" />
          <span className="h-2.5 w-2.5 rounded-full bg-emerald-400/80" />
        </div>
        <div className="hidden items-center gap-2 rounded-lg border border-white/10 bg-white/5 px-3 py-1.5 text-[10px] text-slate-400 sm:flex">
          <Search className="h-3 w-3" /> Tender yoki STIR bo‘yicha qidirish
        </div>
        <span className="flex items-center gap-1.5 text-[10px] font-bold text-emerald-300">
          <span className="pulse-soft h-2 w-2 rounded-full bg-emerald-400" /> LIVE
        </span>
      </div>

      <div className="grid min-h-[490px] grid-cols-[64px_1fr] sm:grid-cols-[170px_1fr]">
        <aside className="border-r border-white/10 p-3 sm:p-4">
          <div className="mb-6 flex items-center gap-2">
            <span className="grid h-8 w-8 place-items-center rounded-lg bg-blue-600">
              <svg viewBox="0 0 32 32" className="h-5 w-5" aria-hidden="true">
                <path d="M7 8h18M16 8v17M10 15h12" stroke="white" strokeWidth="2.4" strokeLinecap="round" />
              </svg>
            </span>
            <span className="hidden text-xs font-extrabold sm:block">TenderHelper</span>
          </div>
          {[
            [LayoutDashboard, 'Overview'],
            [FileSearch, 'Tenderlar'],
            [Bot, 'AI tahlil'],
            [Trophy, 'Raqobatchilar'],
            [Database, 'Hujjatlar'],
          ].map(([Icon, label], index) => (
            <div
              key={label}
              className={`mb-1 flex items-center gap-2 rounded-lg p-2 text-[11px] ${index === 0 ? 'bg-blue-600 text-white' : 'text-slate-500'}`}
            >
              <Icon className="h-4 w-4 shrink-0" />
              <span className="hidden sm:block">{label}</span>
            </div>
          ))}
        </aside>

        <div className="min-w-0 p-3 sm:p-5">
          <div className="mb-4 flex items-center justify-between">
            <div>
              <p className="text-[9px] uppercase tracking-[0.2em] text-slate-500">Operational workspace</p>
              <h3 className="mt-1 text-sm font-bold sm:text-base">Tender radar</h3>
            </div>
            <span className="rounded-full border border-cyan-400/20 bg-cyan-400/10 px-2 py-1 text-[9px] font-bold text-cyan-300">14 JUN 2026</span>
          </div>

          <div className="grid grid-cols-2 gap-2 xl:grid-cols-4">
            {[
              ['Active lots', '1,284', '+12.4%', Activity, 'text-cyan-300'],
              ['AI pipeline', '96.8%', '24 running', Bot, 'text-violet-300'],
              ['Won value', '4.2B', '+18.1%', Trophy, 'text-emerald-300'],
              ['Risk flags', '17', '-8 today', ShieldAlert, 'text-amber-300'],
            ].map(([label, value, meta, Icon, color]) => (
              <div key={label} className="rounded-xl border border-white/10 bg-white/[0.035] p-3">
                <div className="flex items-center justify-between">
                  <span className="text-[9px] text-slate-500">{label}</span>
                  <Icon className={`h-3.5 w-3.5 ${color}`} />
                </div>
                <p className="mt-2 text-base font-black tabular-nums sm:text-lg">{value}</p>
                <p className={`mt-1 text-[9px] ${color}`}>{meta}</p>
              </div>
            ))}
          </div>

          <div className="mt-3 grid gap-3 xl:grid-cols-[1.2fr_.8fr]">
            <div className="rounded-xl border border-white/10 bg-white/[0.035] p-3">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-[10px] font-bold">AI Analysis Pipeline</p>
                  <p className="mt-0.5 text-[9px] text-slate-500">Citation and compliance stages</p>
                </div>
                <ArrowUpRight className="h-4 w-4 text-slate-500" />
              </div>
              <div className="mt-4 flex h-20 items-end gap-1.5">
                {[38, 56, 44, 72, 62, 86, 68, 92, 79, 96, 82, 100].map((height, index) => (
                  <div key={`${height}-${index}`} className="flex-1 rounded-t bg-gradient-to-t from-blue-600 to-cyan-300/90" style={{ height: `${height}%` }} />
                ))}
              </div>
              <div className="mt-3 grid grid-cols-3 gap-2 border-t border-white/10 pt-3 text-[9px]">
                <span><b className="block text-white">128</b><span className="text-slate-500">Parsed</span></span>
                <span><b className="block text-white">32</b><span className="text-slate-500">Analyzing</span></span>
                <span><b className="block text-white">4</b><span className="text-slate-500">Needs review</span></span>
              </div>
            </div>

            <div className="rounded-xl border border-white/10 bg-white/[0.035] p-3">
              <p className="text-[10px] font-bold">Outcome intelligence</p>
              <div className="mt-4 flex items-center justify-center">
                <div className="relative grid h-24 w-24 place-items-center rounded-full bg-[conic-gradient(#34d399_0_68%,#fb7185_68%_91%,#334155_91%)]">
                  <div className="grid h-16 w-16 place-items-center rounded-full bg-[#101b2b] text-center">
                    <span className="text-lg font-black">68%</span>
                    <span className="-mt-3 text-[8px] text-slate-500">WIN RATE</span>
                  </div>
                </div>
              </div>
              <div className="mt-3 flex justify-center gap-3 text-[9px] text-slate-400">
                <span><i className="mr-1 inline-block h-2 w-2 rounded-full bg-emerald-400" />Won 42</span>
                <span><i className="mr-1 inline-block h-2 w-2 rounded-full bg-rose-400" />Lost 14</span>
              </div>
            </div>
          </div>

          <div className="mt-3 rounded-xl border border-white/10 bg-white/[0.035] p-3">
            <div className="mb-2 flex items-center justify-between">
              <p className="text-[10px] font-bold">High-match lots</p>
              <span className="text-[9px] text-cyan-300">Sorted by relevance</span>
            </div>
            <div className="space-y-1.5">
              {lots.map((lot) => (
                <div key={lot.title} className="grid grid-cols-[1fr_auto] items-center gap-3 rounded-lg border border-white/5 bg-black/10 px-2.5 py-2">
                  <div className="min-w-0">
                    <p className="truncate text-[9px] font-semibold sm:text-[10px]">{lot.title}</p>
                    <p className="mt-0.5 flex items-center gap-1 text-[8px] text-slate-500"><Clock3 className="h-2.5 w-2.5" /> {lot.source} · {lot.amount} so‘m</p>
                  </div>
                  <span className="flex items-center gap-1 rounded-md bg-emerald-400/10 px-2 py-1 text-[9px] font-bold text-emerald-300">
                    <CheckCircle2 className="h-3 w-3" /> {lot.score}%
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
