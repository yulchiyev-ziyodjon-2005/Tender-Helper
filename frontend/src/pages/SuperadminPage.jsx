import { useEffect, useMemo, useState } from 'react';
import {
  Activity,
  AlertTriangle,
  BarChart3,
  Bell,
  Bot,
  Building2,
  CheckCircle2,
  ChevronDown,
  CircleDollarSign,
  Clock3,
  Database,
  FileClock,
  FileText,
  Gauge,
  LayoutDashboard,
  LockKeyhole,
  Menu,
  Search,
  Settings,
  ShieldCheck,
  Users,
  X,
} from 'lucide-react';
import BrandMark from '../components/brand/BrandMark';
import ThemeToggle from '../components/ui/ThemeToggle';
import { fetchAdminAudit, fetchAdminOverview } from '../api/controlplane';
import { getApiError } from '../utils/security';

const previewOverview = {
  environment: 'PREVIEW',
  updated_at: new Date().toISOString(),
  growth: { companies: 0, total_users: 0, active_accounts: 0, stir_completion_rate: 0, source_status: 'preview' },
  subscriptions: { by_plan: { free: 0, pro: 0, business: 0 }, by_status: {}, source_status: 'preview' },
  ai: { requests: 0, failures: 0, tokens: null, source_status: 'preview' },
  revenue: { mrr: null, source_status: 'unavailable' },
  operations: { failed_documents: 0, competitor_quality_issues: 0, queue: { source_status: 'unavailable' }, scraping: { source_status: 'unavailable' } },
};

const previewAudit = [
  { id: 'preview-1', created_at: '2026-06-14T09:42:00+05:00', actor: 'a***@tenderhelper.uz', capability: 'subscription_write', action: 'subscription.override', target_type: 'company', reason: 'Approved support escalation TH-1842', outcome: 'success', metadata: { mfa: true } },
  { id: 'preview-2', created_at: '2026-06-14T09:16:00+05:00', actor: 'm***@tenderhelper.uz', capability: 'plan_write', action: 'plan.modification', target_type: 'business_plan', reason: 'Scheduled quota policy update', outcome: 'success', metadata: { mfa: true } },
  { id: 'preview-3', created_at: '2026-06-14T08:51:00+05:00', actor: 's***@tenderhelper.uz', capability: 'pii_reveal', action: 'user.reveal', target_type: 'user', reason: 'Identity verification support case', outcome: 'failure', metadata: { mfa: false } },
];

const navItems = [
  [LayoutDashboard, 'Overview'],
  [Users, 'Foydalanuvchilar'],
  [Building2, 'Kompaniyalar'],
  [CircleDollarSign, 'Tariflar va obunalar'],
  [Gauge, 'Business usage'],
  [Bot, 'AI operatsiyasi'],
  [Database, 'Tender / Scraping'],
  [FileText, 'Hujjat shablonlari'],
  [Settings, 'System settings'],
  [FileClock, 'Audit log'],
];

function sourceBadge(status) {
  const styles = {
    live: 'bg-emerald-400/10 text-emerald-300 border-emerald-400/20',
    partial: 'bg-amber-400/10 text-amber-300 border-amber-400/20',
    unavailable: 'bg-rose-400/10 text-rose-300 border-rose-400/20',
    preview: 'bg-violet-400/10 text-violet-300 border-violet-400/20',
  };
  return styles[status] || styles.partial;
}

function MetricCard({ icon: Icon, label, value, meta, status = 'live', accent = 'text-cyan-300' }) {
  return (
    <article className="rounded-2xl border border-white/10 bg-white/[0.035] p-5">
      <div className="flex items-start justify-between">
        <span className={`grid h-10 w-10 place-items-center rounded-xl bg-white/5 ${accent}`}><Icon className="h-5 w-5" /></span>
        <span className={`rounded-full border px-2 py-1 text-[8px] font-black uppercase tracking-wider ${sourceBadge(status)}`}>{status}</span>
      </div>
      <p className="mt-5 text-[10px] font-bold uppercase tracking-[0.15em] text-slate-500">{label}</p>
      <p className="mt-2 text-2xl font-black tabular-nums">{value}</p>
      <p className="mt-1 text-[10px] text-slate-500">{meta}</p>
    </article>
  );
}

function formatNumber(value) {
  return value === null || value === undefined
    ? 'Not instrumented'
    : new Intl.NumberFormat('uz-UZ').format(value);
}

function formatTime(value) {
  if (!value) return 'Unknown';
  return new Intl.DateTimeFormat('uz-UZ', {
    month: 'short',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(value));
}

export default function SuperadminPage() {
  const [overview, setOverview] = useState(previewOverview);
  const [audit, setAudit] = useState(previewAudit);
  const [isPreview, setIsPreview] = useState(true);
  const [error, setError] = useState('');
  const [accessDenied, setAccessDenied] = useState(false);
  const [loading, setLoading] = useState(true);
  const [mobileNav, setMobileNav] = useState(false);
  const [range, setRange] = useState('30d');

  useEffect(() => {
    let cancelled = false;

    async function loadRadar() {
      setLoading(true);
      const [overviewResult, auditResult] = await Promise.allSettled([
        fetchAdminOverview({ range }),
        fetchAdminAudit({ page_size: 8 }),
      ]);
      if (cancelled) return;

      if (overviewResult.status === 'fulfilled') {
        setOverview(overviewResult.value);
        setIsPreview(false);
        setAccessDenied(false);
      } else {
        const status = overviewResult.reason?.response?.status;
        if (status === 401 || status === 403) {
          setAccessDenied(true);
          setError(getApiError(overviewResult.reason, 'Admin capability va MFA step-up talab qilinadi.'));
        } else {
          setOverview(previewOverview);
          setIsPreview(true);
          setError(getApiError(overviewResult.reason, 'Live operation radar vaqtincha mavjud emas.'));
        }
      }

      if (auditResult.status === 'fulfilled') {
        const payload = auditResult.value;
        setAudit(payload.results || payload);
      } else {
        setAudit(previewAudit);
      }
      setLoading(false);
    }

    loadRadar();
    return () => { cancelled = true; };
  }, [range]);

  const planTotal = useMemo(
    () => Object.values(overview.subscriptions?.by_plan || {}).reduce((sum, value) => sum + Number(value || 0), 0),
    [overview.subscriptions],
  );
  const failures = overview.ai?.failures || 0;
  const requests = overview.ai?.requests || 0;
  const failureRate = requests ? `${((failures / requests) * 100).toFixed(1)}%` : '0%';

  if (accessDenied) {
    return (
      <main className="grid min-h-screen place-items-center bg-[#050b14] px-5 text-white">
        <div className="w-full max-w-lg rounded-[28px] border border-rose-400/20 bg-[#0a1423] p-7 text-center shadow-2xl">
          <BrandMark inverse />
          <span className="mx-auto mt-10 grid h-16 w-16 place-items-center rounded-2xl bg-rose-400/10 text-rose-300">
            <LockKeyhole className="h-7 w-7" />
          </span>
          <p className="mt-6 text-xs font-black uppercase tracking-[0.2em] text-rose-300">403 · Privileged surface</p>
          <h1 className="mt-3 text-3xl font-black tracking-[-0.04em]">Superadmin ruxsati talab qilinadi</h1>
          <p className="mt-4 text-sm leading-6 text-slate-400">{error} Bu sahifada mock yoki live operatsion ma’lumot ochilmaydi.</p>
          <a href="/dashboard" className="mt-7 inline-flex rounded-xl bg-white px-5 py-3 text-sm font-extrabold text-slate-950">Customer workspace’ga qaytish</a>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-[#050b14] text-white">
      {/* WP7: privileged console stays visually and structurally separate from the customer app. */}
      <div className="grid min-h-screen xl:grid-cols-[250px_1fr]">
        <aside className={`fixed inset-y-0 left-0 z-50 w-[280px] border-r border-white/10 bg-[#07111f] p-4 transition-transform xl:static xl:w-auto xl:translate-x-0 ${mobileNav ? 'translate-x-0' : '-translate-x-full'}`}>
          <div className="flex items-center justify-between px-2 py-2">
            <BrandMark inverse />
            <button type="button" onClick={() => setMobileNav(false)} className="grid h-9 w-9 place-items-center rounded-lg border border-white/10 xl:hidden" aria-label="Menyuni yopish"><X className="h-4 w-4" /></button>
          </div>
          <div className="mt-6 rounded-xl border border-rose-400/20 bg-rose-400/10 px-3 py-2">
            <p className="text-[9px] font-black uppercase tracking-[0.22em] text-rose-300">Superadmin · {overview.environment || 'Production'}</p>
            <p className="mt-1 text-[10px] text-rose-100/60">Privileged operational surface</p>
          </div>
          <nav className="mt-6 space-y-1">
            {navItems.map(([Icon, label], index) => (
              <button key={label} type="button" className={`flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-left text-xs font-bold transition ${index === 0 ? 'bg-blue-600 text-white' : 'text-slate-400 hover:bg-white/5 hover:text-white'}`}>
                <Icon className="h-4 w-4" />{label}
              </button>
            ))}
          </nav>
          <div className="mt-8 rounded-xl border border-white/10 bg-white/[0.03] p-3">
            <div className="flex items-center gap-2 text-[10px] font-bold text-emerald-300"><ShieldCheck className="h-4 w-4" /> MFA step-up active</div>
            <p className="mt-2 text-[9px] leading-4 text-slate-500">Critical write window: 08:42 remaining</p>
          </div>
        </aside>

        {mobileNav && <button type="button" className="fixed inset-0 z-40 bg-black/70 xl:hidden" onClick={() => setMobileNav(false)} aria-label="Menyuni yopish" />}

        <div className="min-w-0">
          <header className="sticky top-0 z-30 border-b border-white/10 bg-[#050b14]/90 px-4 py-3 backdrop-blur-xl sm:px-6">
            <div className="flex items-center gap-3">
              <button type="button" onClick={() => setMobileNav(true)} className="grid h-10 w-10 place-items-center rounded-xl border border-white/10 xl:hidden" aria-label="Navigatsiyani ochish"><Menu className="h-5 w-5" /></button>
              <div className="hidden min-w-0 flex-1 items-center gap-2 rounded-xl border border-white/10 bg-white/[0.035] px-3 sm:flex">
                <Search className="h-4 w-4 text-slate-500" />
                <input placeholder="User, email, telefon, company yoki STIR..." className="w-full bg-transparent py-2.5 text-xs outline-none placeholder:text-slate-600" />
                <span className="rounded border border-white/10 px-1.5 py-0.5 text-[9px] text-slate-500">⌘K</span>
              </div>
              <span className="hidden items-center gap-2 text-[10px] text-slate-500 md:flex"><Clock3 className="h-3.5 w-3.5" /> Updated {formatTime(overview.updated_at)}</span>
              <ThemeToggle />
              <button type="button" className="relative grid h-10 w-10 place-items-center rounded-xl border border-white/10 text-slate-400"><Bell className="h-4 w-4" /><span className="absolute right-2 top-2 h-1.5 w-1.5 rounded-full bg-rose-400" /></button>
              <button type="button" className="flex items-center gap-2 rounded-xl border border-white/10 px-2 py-1.5 text-left"><span className="grid h-7 w-7 place-items-center rounded-lg bg-gradient-to-br from-blue-500 to-cyan-400 text-[10px] font-black">SA</span><span className="hidden text-[10px] font-bold lg:block">Super Admin</span><ChevronDown className="h-3 w-3 text-slate-500" /></button>
            </div>
          </header>

          <div className="mx-auto max-w-[1600px] px-4 py-7 sm:px-6 lg:px-8">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
              <div>
                <div className="flex items-center gap-2">
                  <h1 className="text-2xl font-black tracking-[-0.035em] sm:text-3xl">Operation Radar</h1>
                  {isPreview && <span className="rounded-full border border-violet-400/20 bg-violet-400/10 px-2 py-1 text-[8px] font-black uppercase tracking-wider text-violet-300">Preview dataset</span>}
                </div>
                <p className="mt-2 text-xs text-slate-500">Growth, revenue coverage, AI diagnostics and privileged audit events.</p>
              </div>
              <select value={range} onChange={(event) => setRange(event.target.value)} className="rounded-xl border border-white/10 bg-white/[0.035] px-4 py-2.5 text-xs font-bold outline-none">
                <option value="today" className="bg-slate-900">Today</option>
                <option value="7d" className="bg-slate-900">7 kun</option>
                <option value="30d" className="bg-slate-900">30 kun</option>
                <option value="90d" className="bg-slate-900">90 kun</option>
              </select>
            </div>

            {error && (
              <div className="mt-5 flex items-start gap-3 rounded-xl border border-amber-400/20 bg-amber-400/10 p-4 text-xs text-amber-100">
                <LockKeyhole className="h-4 w-4 shrink-0 text-amber-300" />
                <span>{error} Quyidagi qiymatlar faqat interfeys preview’si; live qiymat sifatida talqin qilinmaydi.</span>
              </div>
            )}

            <section className="mt-6 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
              <MetricCard icon={Building2} label="Total companies" value={formatNumber(overview.growth?.companies)} meta={`STIR completion ${overview.growth?.stir_completion_rate ?? 0}% · Updated 5 min ago`} status={overview.growth?.source_status} />
              <MetricCard icon={Users} label="Active accounts" value={formatNumber(overview.growth?.active_accounts)} meta={`${formatNumber(overview.growth?.total_users)} total users`} status={overview.growth?.source_status} accent="text-violet-300" />
              <MetricCard icon={CircleDollarSign} label="Paid MRR analytics" value={overview.revenue?.mrr === null ? 'Unavailable' : `${formatNumber(overview.revenue?.mrr)} UZS`} meta="Requires reconciled payment ledger" status={overview.revenue?.source_status} accent="text-emerald-300" />
              <MetricCard icon={Bot} label="AI requests" value={formatNumber(requests)} meta={`${failureRate} failure rate · Updated 1 min ago`} status={overview.ai?.source_status} accent="text-amber-300" />
            </section>

            <section className="mt-5 grid gap-5 2xl:grid-cols-[1.05fr_.95fr]">
              <article className="rounded-2xl border border-white/10 bg-white/[0.025] p-5">
                <div className="flex items-center justify-between"><div><h2 className="text-sm font-black">Subscription distribution</h2><p className="mt-1 text-[10px] text-slate-500">Effective subscriptions by canonical plan</p></div><BarChart3 className="h-5 w-5 text-cyan-300" /></div>
                <div className="mt-7 space-y-5">
                  {[
                    ['Free', overview.subscriptions?.by_plan?.free || 0, 'bg-slate-500'],
                    ['Pro', overview.subscriptions?.by_plan?.pro || 0, 'bg-blue-500'],
                    ['Business', overview.subscriptions?.by_plan?.business || 0, 'bg-cyan-300'],
                    ['Enterprise', overview.subscriptions?.by_plan?.enterprise || 0, 'bg-violet-400'],
                  ].map(([label, value, color]) => {
                    const width = planTotal ? Math.max(4, (value / planTotal) * 100) : 4;
                    return (
                      <div key={label}>
                        <div className="mb-2 flex justify-between text-xs"><span className="font-bold">{label}</span><span className="tabular-nums text-slate-400">{value} · {planTotal ? Math.round((value / planTotal) * 100) : 0}%</span></div>
                        <div className="h-2 rounded-full bg-white/5"><div className={`h-full rounded-full ${color}`} style={{ width: `${width}%` }} /></div>
                      </div>
                    );
                  })}
                </div>
                <div className="mt-7 grid grid-cols-3 gap-2 border-t border-white/10 pt-5">
                  {Object.entries(overview.subscriptions?.by_status || {}).slice(0, 3).map(([label, value]) => <div key={label}><p className="text-lg font-black tabular-nums">{value}</p><p className="text-[9px] uppercase text-slate-500">{label}</p></div>)}
                  {!Object.keys(overview.subscriptions?.by_status || {}).length && <p className="col-span-3 text-xs text-slate-500">Live subscription status data mavjud emas.</p>}
                </div>
              </article>

              <article className="rounded-2xl border border-white/10 bg-white/[0.025] p-5">
                <div className="flex items-center justify-between"><div><h2 className="text-sm font-black">Live ingestion & AI diagnostics</h2><p className="mt-1 text-[10px] text-slate-500">Provider, token and operational coverage</p></div><Activity className="h-5 w-5 text-emerald-300" /></div>
                <div className="mt-6 grid grid-cols-2 gap-3">
                  {[
                    ['Total requests', formatNumber(requests), overview.ai?.source_status],
                    ['Total tokens', formatNumber(overview.ai?.tokens), overview.ai?.tokens === null ? 'unavailable' : 'live'],
                    ['Failed analyses', formatNumber(failures), overview.ai?.source_status],
                    ['Provider failure', 'Not instrumented', 'unavailable'],
                  ].map(([label, value, status]) => (
                    <div key={label} className="rounded-xl border border-white/10 bg-black/10 p-4"><p className="text-[9px] uppercase tracking-wider text-slate-500">{label}</p><p className="mt-2 text-base font-black">{value}</p><span className={`mt-3 inline-flex rounded-full border px-2 py-0.5 text-[8px] font-black uppercase ${sourceBadge(status)}`}>{status}</span></div>
                  ))}
                </div>
                <div className="mt-4 flex items-start gap-3 rounded-xl border border-amber-400/20 bg-amber-400/10 p-3 text-[10px] leading-4 text-amber-100/80"><AlertTriangle className="h-4 w-4 shrink-0 text-amber-300" />Token usage, AI cost, latency va provider breakdown backend telemetry’sida hali instrument qilinmagan. Radar bu bo‘shliqni yashirmaydi.</div>
                <div className="mt-4 overflow-hidden rounded-xl border border-white/10">
                  {[
                    ['Google Gemini', formatNumber(overview.ai?.requests), failureRate, overview.ai?.source_status || 'partial'],
                    ['Company Registry', 'Not instrumented', 'Not instrumented', 'unavailable'],
                    ['Document AI', 'Not instrumented', `${overview.operations?.failed_documents || 0} failed`, 'partial'],
                  ].map(([provider, requestCount, failuresValue, providerStatus]) => (
                    <div key={provider} className="grid grid-cols-[1fr_auto_auto] items-center gap-4 border-b border-white/5 px-4 py-3 text-[10px] last:border-b-0">
                      <span className="font-bold">{provider}</span>
                      <span className="text-slate-400">{requestCount} requests</span>
                      <span className={`rounded-full border px-2 py-0.5 font-black uppercase ${sourceBadge(providerStatus)}`}>{failuresValue}</span>
                    </div>
                  ))}
                </div>
              </article>
            </section>

            <section className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
              {[
                ['API', 'Operational', 'live', Activity],
                ['Queue', 'Unavailable', overview.operations?.queue?.source_status || 'unavailable', Database],
                ['Scraping', 'Unavailable', overview.operations?.scraping?.source_status || 'unavailable', Gauge],
                ['Documents', `${overview.operations?.failed_documents || 0} failed`, (overview.operations?.failed_documents || 0) ? 'partial' : 'live', FileText],
              ].map(([label, value, status, Icon]) => (
                <div key={label} className="flex items-center gap-3 rounded-xl border border-white/10 bg-white/[0.025] p-4"><span className={`grid h-9 w-9 place-items-center rounded-lg ${sourceBadge(status)} border`}><Icon className="h-4 w-4" /></span><div><p className="text-[10px] font-bold text-slate-500">{label}</p><p className="mt-1 text-xs font-black">{value}</p></div></div>
              ))}
            </section>

            {/* WP7 audit is append-only: the interface deliberately exposes no edit/delete actions. */}
            <section className="mt-5 overflow-hidden rounded-2xl border border-white/10 bg-white/[0.025]">
              <div className="flex items-center justify-between border-b border-white/10 p-5"><div><h2 className="text-sm font-black">Privileged audit log</h2><p className="mt-1 text-[10px] text-slate-500">Append-only events · identity masked by default</p></div><span className="inline-flex items-center gap-2 rounded-full border border-emerald-400/20 bg-emerald-400/10 px-3 py-1.5 text-[9px] font-black text-emerald-300"><ShieldCheck className="h-3.5 w-3.5" /> IMMUTABLE</span></div>
              <div className="overflow-x-auto">
                <table className="w-full min-w-[1000px] text-left">
                  <thead className="border-b border-white/10 bg-white/[0.02] text-[9px] uppercase tracking-[0.14em] text-slate-500">
                    <tr><th className="px-5 py-3 font-bold">Timestamp</th><th className="px-5 py-3 font-bold">Capability role</th><th className="px-5 py-3 font-bold">Performed action</th><th className="px-5 py-3 font-bold">Mandated reason</th><th className="px-5 py-3 font-bold">Identity</th><th className="px-5 py-3 font-bold">MFA step-up</th><th className="px-5 py-3 font-bold">Outcome</th></tr>
                  </thead>
                  <tbody className="divide-y divide-white/5">
                    {audit.map((event) => {
                      const mfa = event.metadata?.mfa ?? event.action === 'admin.step_up';
                      return (
                        <tr key={event.id} className="text-[10px] transition hover:bg-white/[0.025]">
                          <td className="whitespace-nowrap px-5 py-4 font-mono text-slate-400">{formatTime(event.created_at)}</td>
                          <td className="px-5 py-4"><span className="rounded bg-blue-400/10 px-2 py-1 font-bold text-blue-300">{event.capability}</span></td>
                          <td className="px-5 py-4 font-bold">{event.action}</td>
                          <td className="max-w-[260px] truncate px-5 py-4 text-slate-400">{event.reason || 'Reason required'}</td>
                          <td className="px-5 py-4 font-mono text-slate-400">{event.actor || 'masked'}</td>
                          <td className="px-5 py-4">{mfa ? <span className="inline-flex items-center gap-1 text-emerald-300"><CheckCircle2 className="h-3.5 w-3.5" /> Success</span> : <span className="inline-flex items-center gap-1 text-rose-300"><AlertTriangle className="h-3.5 w-3.5" /> Missing</span>}</td>
                          <td className="px-5 py-4"><span className={`rounded-full px-2 py-1 font-black uppercase ${event.outcome === 'success' ? 'bg-emerald-400/10 text-emerald-300' : 'bg-rose-400/10 text-rose-300'}`}>{event.outcome}</span></td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
              <div className="flex items-center justify-between border-t border-white/10 px-5 py-4 text-[10px] text-slate-500"><span>{loading ? 'Live data tekshirilmoqda...' : `${audit.length} event ko‘rsatildi`}</span><span>Export requires `audit_export` + MFA</span></div>
            </section>
          </div>
        </div>
      </div>
    </main>
  );
}
