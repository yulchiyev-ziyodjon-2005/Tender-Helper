import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  AlertCircle,
  Bot,
  Building2,
  Check,
  ChevronRight,
  CircleGauge,
  Copy,
  FilePenLine,
  KeyRound,
  Laptop,
  LayoutDashboard,
  LoaderCircle,
  LockKeyhole,
  LogOut,
  Menu,
  Plus,
  RefreshCw,
  Search,
  ShieldCheck,
  ShieldOff,
  Sparkles,
  Trash2,
  Trophy,
  Users,
  X,
} from 'lucide-react';
import BrandMark from '../components/brand/BrandMark';
import ThemeToggle from '../components/ui/ThemeToggle';
import {
  fetchTeamMembers,
  fetchTeamWorkspace,
  inviteTeamMember,
  revokeTeamMemberSessions,
} from '../api/teams';
import useAuthStore from '../store/authStore';
import { getApiError, sanitizePlainText } from '../utils/security';

const permissionGroups = [
  {
    name: 'Search',
    icon: Search,
    permissions: [
      ['view_lots', 'View Lots'],
      ['export_lot_data', 'Export Lot Data'],
    ],
  },
  {
    name: 'AI Analysis',
    icon: Bot,
    permissions: [
      ['run_ai_analysis', 'Run Deep AI Risk Analysis'],
      ['use_analysis_quotas', 'Use Quotas'],
    ],
  },
  {
    name: 'Documents',
    icon: FilePenLine,
    permissions: [
      ['generate_ai_contracts', 'Generate AI Contracts'],
      ['edit_inline_workspace', 'Edit Inline Workspace'],
      ['export_pdf_docx', 'Export PDF / DOCX'],
    ],
  },
  {
    name: 'Competitors',
    icon: Trophy,
    permissions: [
      ['access_competitor_metrics', 'Access Competitor Metrics'],
    ],
  },
];

const roleDefaults = {
  admin: permissionGroups.flatMap((group) => group.permissions.map(([key]) => key)).concat('manage_team'),
  manager: [
    'view_lots',
    'export_lot_data',
    'run_ai_analysis',
    'use_analysis_quotas',
    'generate_ai_contracts',
    'edit_inline_workspace',
    'export_pdf_docx',
    'access_competitor_metrics',
  ],
  viewer: ['view_lots', 'access_competitor_metrics'],
};

const previewMembers = [
  {
    id: 'owner-preview',
    full_name: 'Workspace Owner',
    email: 'owner@company.uz',
    role: 'owner',
    permissions: roleDefaults.admin,
    login_status: 'active',
    is_active: true,
    sessions: [],
  },
];

function generateTemporaryPassword() {
  const alphabet = 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789!@#$%';
  const bytes = new Uint32Array(16);
  window.crypto.getRandomValues(bytes);
  return Array.from(bytes, (value) => alphabet[value % alphabet.length]).join('');
}

function Toggle({ checked, onChange, label }) {
  return (
    <button
      type="button"
      role="switch"
      aria-checked={checked}
      aria-label={label}
      onClick={onChange}
      className={`relative h-6 w-11 rounded-full transition ${checked ? 'bg-blue-600' : 'bg-slate-200 dark:bg-white/10'}`}
    >
      <span className={`absolute top-1 h-4 w-4 rounded-full bg-white shadow transition ${checked ? 'left-6' : 'left-1'}`} />
    </button>
  );
}

function AddMemberModal({ onClose, onCreated, companyId }) {
  const [form, setForm] = useState({
    fullName: '',
    email: '',
    password: generateTemporaryPassword(),
    forceChange: true,
    role: 'manager',
    permissions: roleDefaults.manager,
  });
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState('');
  const [copied, setCopied] = useState(false);

  function setRole(role) {
    setForm((current) => ({ ...current, role, permissions: [...roleDefaults[role]] }));
  }

  function togglePermission(permission) {
    setForm((current) => ({
      ...current,
      permissions: current.permissions.includes(permission)
        ? current.permissions.filter((item) => item !== permission)
        : [...current.permissions, permission],
    }));
  }

  async function submit(event) {
    event.preventDefault();
    setIsSaving(true);
    setError('');
    try {
      const member = await inviteTeamMember({
        company_id: companyId,
        full_name: sanitizePlainText(form.fullName, 255),
        email: form.email.trim().toLowerCase(),
        temporary_password: form.password,
        force_password_change: form.forceChange,
        role: form.role,
        permissions: form.permissions,
      });
      onCreated(member);
    } catch (requestError) {
      setError(getApiError(requestError, 'Xodimni qo‘shib bo‘lmadi.'));
    } finally {
      setIsSaving(false);
    }
  }

  async function copyPassword() {
    await navigator.clipboard.writeText(form.password);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  }

  return (
    <div className="fixed inset-0 z-[70] grid place-items-center overflow-y-auto bg-slate-950/80 p-4 backdrop-blur-sm">
      <button type="button" className="absolute inset-0" onClick={onClose} aria-label="Modalni yopish" />
      <form onSubmit={submit} className="relative z-10 my-6 w-full max-w-4xl rounded-[28px] border border-slate-200 bg-white shadow-2xl dark:border-white/10 dark:bg-[#0a1423]">
        <div className="flex items-start justify-between border-b border-slate-200 p-5 sm:p-7 dark:border-white/10">
          <div><p className="text-[10px] font-black uppercase tracking-[0.2em] text-blue-600 dark:text-cyan-300">WP2 · Seat provisioning</p><h2 className="mt-2 text-2xl font-black">Jamoa a’zosini qo‘shish</h2><p className="mt-2 text-sm text-slate-500">Role defaultlarini tanlang va explicit permissionlarni sozlang.</p></div>
          <button type="button" onClick={onClose} className="grid h-10 w-10 place-items-center rounded-xl border border-slate-200 dark:border-white/10" aria-label="Yopish"><X className="h-5 w-5" /></button>
        </div>

        <div className="grid gap-7 p-5 sm:p-7 lg:grid-cols-[.78fr_1.22fr]">
          <div className="space-y-5">
            {error && <div role="alert" className="flex gap-2 rounded-xl border border-rose-200 bg-rose-50 p-3 text-xs text-rose-700 dark:border-rose-400/20 dark:bg-rose-400/10 dark:text-rose-200"><AlertCircle className="h-4 w-4 shrink-0" />{error}</div>}
            <label className="block"><span className="mb-2 block text-xs font-bold">To‘liq ism</span><input value={form.fullName} onChange={(event) => setForm((current) => ({ ...current, fullName: event.target.value }))} required minLength={2} autoComplete="off" placeholder="Aziza Karimova" className="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 dark:border-white/10 dark:bg-white/[0.035]" /></label>
            <label className="block"><span className="mb-2 block text-xs font-bold">Assigned work email</span><input type="email" value={form.email} onChange={(event) => setForm((current) => ({ ...current, email: event.target.value }))} required autoComplete="off" placeholder="aziza@company.uz" className="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 dark:border-white/10 dark:bg-white/[0.035]" /></label>
            <label className="block">
              <span className="mb-2 flex items-center justify-between text-xs font-bold"><span>Temporary password</span><button type="button" onClick={() => setForm((current) => ({ ...current, password: generateTemporaryPassword() }))} className="flex items-center gap-1 text-blue-600 dark:text-cyan-300"><RefreshCw className="h-3 w-3" /> Regenerate</button></span>
              <span className="flex rounded-xl border border-slate-200 bg-slate-50 dark:border-white/10 dark:bg-white/[0.035]"><input value={form.password} readOnly className="min-w-0 flex-1 bg-transparent px-4 py-3 font-mono text-xs outline-none" /><button type="button" onClick={copyPassword} className="m-1.5 inline-flex items-center gap-1 rounded-lg bg-slate-950 px-3 text-[10px] font-bold text-white dark:bg-white dark:text-slate-950"><Copy className="h-3 w-3" />{copied ? 'Copied' : 'Copy'}</button></span>
            </label>
            <div className="flex items-center justify-between rounded-xl border border-slate-200 p-4 dark:border-white/10"><div><p className="text-xs font-black">Force password change</p><p className="mt-1 text-[10px] text-slate-500">Birinchi login boshqa private API’larni bloklaydi.</p></div><Toggle checked={form.forceChange} onChange={() => setForm((current) => ({ ...current, forceChange: !current.forceChange }))} label="Birinchi kirishda parolni almashtirish" /></div>

            <div><p className="mb-3 text-xs font-bold">Structural role</p><div className="grid grid-cols-3 gap-2">{['admin', 'manager', 'viewer'].map((role) => <button type="button" key={role} onClick={() => setRole(role)} className={`rounded-xl border px-2 py-3 text-xs font-black capitalize transition ${form.role === role ? 'border-blue-500 bg-blue-50 text-blue-700 dark:bg-blue-500/10 dark:text-cyan-300' : 'border-slate-200 text-slate-500 dark:border-white/10'}`}>{role}</button>)}</div></div>
          </div>

          <div>
            <div className="mb-4"><h3 className="text-sm font-black">Fine-grained permission matrix</h3><p className="mt-1 text-xs text-slate-500">Backend har bir write/read operatsiyasida shu flaglarni tekshiradi.</p></div>
            <div className="space-y-3">
              {permissionGroups.map(({ name, icon: Icon, permissions }) => (
                <section key={name} className="rounded-2xl border border-slate-200 p-4 dark:border-white/10">
                  <h4 className="mb-3 flex items-center gap-2 text-xs font-black uppercase tracking-wider text-slate-500"><Icon className="h-4 w-4 text-blue-500" />{name}</h4>
                  <div className="space-y-3">{permissions.map(([key, label]) => <div key={key} className="flex items-center justify-between gap-4"><span className="text-sm font-semibold">{label}</span><Toggle checked={form.permissions.includes(key)} onChange={() => togglePermission(key)} label={label} /></div>)}</div>
                </section>
              ))}
            </div>
          </div>
        </div>

        <div className="flex flex-col-reverse gap-3 border-t border-slate-200 p-5 sm:flex-row sm:justify-end sm:p-7 dark:border-white/10">
          <button type="button" onClick={onClose} className="rounded-xl border border-slate-200 px-5 py-3 text-sm font-bold dark:border-white/10">Bekor qilish</button>
          <button type="submit" disabled={isSaving} className="inline-flex items-center justify-center gap-2 rounded-xl bg-blue-600 px-6 py-3 text-sm font-black text-white disabled:opacity-50">{isSaving ? <LoaderCircle className="h-4 w-4 animate-spin" /> : <Plus className="h-4 w-4" />} Xodimni yaratish</button>
        </div>
      </form>
    </div>
  );
}

function PermissionMatrix({ member }) {
  return (
    <div className="grid gap-3 md:grid-cols-2">
      {permissionGroups.map(({ name, icon: Icon, permissions }) => (
        <div key={name} className="rounded-2xl border border-slate-200 p-4 dark:border-white/10">
          <p className="flex items-center gap-2 text-xs font-black uppercase tracking-wider text-slate-500"><Icon className="h-4 w-4 text-blue-500" />{name}</p>
          <div className="mt-3 space-y-2">{permissions.map(([key, label]) => <div key={key} className="flex items-center justify-between text-xs"><span>{label}</span>{member.permissions.includes(key) ? <Check className="h-4 w-4 text-emerald-500" /> : <X className="h-4 w-4 text-slate-300 dark:text-slate-700" />}</div>)}</div>
        </div>
      ))}
    </div>
  );
}

export default function TeamWorkspacePage() {
  const navigate = useNavigate();
  const logout = useAuthStore((state) => state.logout);
  const [workspace, setWorkspace] = useState(null);
  const [members, setMembers] = useState([]);
  const [selectedId, setSelectedId] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [mobileNav, setMobileNav] = useState(false);
  const [terminating, setTerminating] = useState(false);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const workspaceData = await fetchTeamWorkspace();
        if (cancelled) return;
        setWorkspace(workspaceData);
        if (workspaceData.membership.can_manage_team) {
          const memberData = await fetchTeamMembers({
            company_id: workspaceData.company.id,
          });
          if (cancelled) return;
          setMembers(memberData);
          setSelectedId(memberData[0]?.id || '');
        } else {
          setMembers(previewMembers.map((item) => ({ ...item, full_name: 'Current employee', role: workspaceData.membership.role, permissions: workspaceData.membership.permissions })));
          setSelectedId('owner-preview');
        }
      } catch (requestError) {
        if (!cancelled) setError(getApiError(requestError, 'Team workspace mavjud emas yoki Business entitlement talab qilinadi.'));
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => { cancelled = true; };
  }, []);

  const selected = members.find((member) => member.id === selectedId) || members[0];
  const permissions = workspace?.membership?.permissions || [];
  const has = (permission) => workspace?.membership?.role === 'owner' || permissions.includes(permission);
  const nav = [
    { label: 'Workspace overview', icon: LayoutDashboard, show: true, to: '/team' },
    { label: 'Tender search', icon: Search, show: has('view_lots'), to: '/dashboard' },
    { label: 'AI analysis', icon: Bot, show: has('run_ai_analysis'), to: '/analysis' },
    { label: 'Document generation', icon: FilePenLine, show: has('generate_ai_contracts'), to: '/team?module=documents' },
    { label: 'Competitor analytics', icon: Trophy, show: has('access_competitor_metrics'), to: '/team?module=competitors' },
    { label: 'Team & permissions', icon: Users, show: workspace?.membership?.can_manage_team, to: '/team' },
    { label: 'Superadmin control', icon: CircleGauge, show: workspace?.platform_admin, to: '/superadmin' },
  ].filter((item) => item.show);

  async function revokeAccess() {
    if (!selected || selected.role === 'owner') return;
    setTerminating(true);
    try {
      await revokeTeamMemberSessions(selected.id);
      setMembers((current) => current.map((member) => member.id === selected.id ? { ...member, is_active: false, login_status: 'terminated', sessions: member.sessions.map((session) => ({ ...session, revoked_at: new Date().toISOString() })) } : member));
    } catch (requestError) {
      setError(getApiError(requestError, 'Sessiyani bekor qilib bo‘lmadi.'));
    } finally {
      setTerminating(false);
    }
  }

  if (loading) return <div className="grid min-h-screen place-items-center bg-slate-50 dark:bg-[#050b14]"><LoaderCircle className="h-8 w-8 animate-spin text-blue-600" /></div>;

  if (error && !workspace) {
    return (
      <main className="grid min-h-screen place-items-center bg-slate-50 p-5 dark:bg-[#050b14]">
        <div className="max-w-lg rounded-[28px] border border-amber-200 bg-white p-8 text-center dark:border-amber-400/20 dark:bg-[#0a1423]"><LockKeyhole className="mx-auto h-10 w-10 text-amber-500" /><h1 className="mt-5 text-2xl font-black">Business Team Hub yopiq</h1><p className="mt-3 text-sm leading-6 text-slate-500">{error}</p><Link to="/#pricing" className="mt-6 inline-flex rounded-xl bg-blue-600 px-5 py-3 text-sm font-black text-white">Business tarifini ko‘rish</Link></div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-slate-50 text-slate-950 dark:bg-[#050b14] dark:text-white">
      <div className="grid min-h-screen xl:grid-cols-[250px_1fr]">
        <aside className={`fixed inset-y-0 left-0 z-50 w-[280px] border-r border-slate-200 bg-white p-4 transition-transform xl:static xl:w-auto xl:translate-x-0 dark:border-white/10 dark:bg-[#07111f] ${mobileNav ? 'translate-x-0' : '-translate-x-full'}`}>
          <div className="flex items-center justify-between px-2 py-2"><BrandMark /><button type="button" onClick={() => setMobileNav(false)} className="grid h-9 w-9 place-items-center rounded-lg border border-slate-200 xl:hidden dark:border-white/10"><X className="h-4 w-4" /></button></div>
          <div className="mt-6 rounded-xl border border-blue-200 bg-blue-50 p-3 dark:border-cyan-400/20 dark:bg-cyan-400/10"><p className="text-[9px] font-black uppercase tracking-[0.18em] text-blue-700 dark:text-cyan-300">Business workspace</p><p className="mt-1 truncate text-xs font-bold">{workspace.company.name}</p><p className="mt-1 text-[9px] uppercase text-slate-500">{workspace.membership.role} · {workspace.company.stir_verified ? 'STIR verified' : 'STIR required'}</p></div>
          <nav className="mt-6 space-y-1">{nav.map(({ label, icon: Icon, to }, index) => <Link key={label} to={to} className={`flex items-center gap-3 rounded-xl px-3 py-2.5 text-xs font-bold transition ${index === 0 ? 'bg-blue-600 text-white' : 'text-slate-500 hover:bg-slate-100 hover:text-slate-950 dark:hover:bg-white/5 dark:hover:text-white'}`}><Icon className="h-4 w-4" />{label}</Link>)}</nav>
          <button type="button" onClick={() => { logout(); navigate('/login'); }} className="mt-8 flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-xs font-bold text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-400/10"><LogOut className="h-4 w-4" />Chiqish</button>
        </aside>
        {mobileNav && <button type="button" className="fixed inset-0 z-40 bg-slate-950/70 xl:hidden" onClick={() => setMobileNav(false)} aria-label="Menyuni yopish" />}

        <div className="min-w-0">
          <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-slate-200 bg-white/90 px-4 backdrop-blur-xl sm:px-6 dark:border-white/10 dark:bg-[#050b14]/90"><div className="flex items-center gap-3"><button type="button" onClick={() => setMobileNav(true)} className="grid h-10 w-10 place-items-center rounded-xl border border-slate-200 xl:hidden dark:border-white/10"><Menu className="h-5 w-5" /></button><div><p className="text-xs font-black">Enterprise Team Hub</p><p className="text-[9px] text-slate-500">Permission-aware operational workspace</p></div></div><div className="flex items-center gap-2"><ThemeToggle />{workspace.membership.can_manage_team && <button type="button" onClick={() => setShowModal(true)} className="inline-flex items-center gap-2 rounded-xl bg-blue-600 px-4 py-2.5 text-xs font-black text-white"><Plus className="h-4 w-4" /><span className="hidden sm:inline">Add Team Member</span></button>}</div></header>

          <div className="mx-auto max-w-[1500px] p-4 sm:p-6 lg:p-8">
            {error && <div role="alert" className="mb-5 flex gap-2 rounded-xl border border-rose-200 bg-rose-50 p-3 text-xs text-rose-700 dark:border-rose-400/20 dark:bg-rose-400/10 dark:text-rose-200"><AlertCircle className="h-4 w-4" />{error}</div>}
            <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
              {[
                [Users, members.filter((member) => member.is_active).length, 'Active seats', 'text-blue-500'],
                [ShieldCheck, workspace.membership.role, 'Your structural role', 'text-emerald-500'],
                [KeyRound, permissions.length || roleDefaults.admin.length, 'Explicit permissions', 'text-violet-500'],
                [Building2, workspace.company.plan, 'Subscription plan', 'text-amber-500'],
              ].map(([Icon, value, label, color]) => <div key={label} className="rounded-2xl border border-slate-200 bg-white p-5 dark:border-white/10 dark:bg-white/[0.025]"><Icon className={`h-5 w-5 ${color}`} /><p className="mt-4 text-2xl font-black capitalize tabular-nums">{value}</p><p className="mt-1 text-[10px] font-bold uppercase tracking-wider text-slate-400">{label}</p></div>)}
            </div>

            <div className="mt-5 grid gap-5 2xl:grid-cols-[.75fr_1.25fr]">
              <section className="overflow-hidden rounded-2xl border border-slate-200 bg-white dark:border-white/10 dark:bg-white/[0.025]">
                <div className="border-b border-slate-200 p-5 dark:border-white/10"><h2 className="text-sm font-black">Team directory</h2><p className="mt-1 text-[10px] text-slate-500">Seat, role va login status</p></div>
                <div className="divide-y divide-slate-100 dark:divide-white/5">{members.map((member) => <button type="button" key={member.id} onClick={() => setSelectedId(member.id)} className={`flex w-full items-center gap-3 p-4 text-left transition ${selected?.id === member.id ? 'bg-blue-50 dark:bg-blue-500/10' : 'hover:bg-slate-50 dark:hover:bg-white/[0.025]'}`}><span className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-slate-100 text-xs font-black dark:bg-white/5">{member.full_name?.split(' ').map((part) => part[0]).join('').slice(0, 2) || 'TM'}</span><span className="min-w-0 flex-1"><span className="block truncate text-xs font-black">{member.full_name}</span><span className="mt-1 block truncate text-[10px] text-slate-500">{member.email}</span></span><span className="text-right"><span className="block text-[9px] font-black uppercase text-blue-500">{member.role}</span><span className={`mt-1 inline-flex items-center gap-1 text-[9px] ${member.login_status === 'active' ? 'text-emerald-500' : member.login_status === 'terminated' ? 'text-rose-500' : 'text-amber-500'}`}><i className="h-1.5 w-1.5 rounded-full bg-current" />{member.login_status}</span></span><ChevronRight className="h-4 w-4 text-slate-300" /></button>)}</div>
              </section>

              {selected && <section className="rounded-2xl border border-slate-200 bg-white p-5 sm:p-6 dark:border-white/10 dark:bg-white/[0.025]">
                <div className="flex flex-col gap-4 border-b border-slate-200 pb-5 sm:flex-row sm:items-start sm:justify-between dark:border-white/10"><div className="flex items-center gap-3"><span className="grid h-12 w-12 place-items-center rounded-2xl bg-gradient-to-br from-blue-600 to-cyan-400 text-sm font-black text-white">{selected.full_name?.slice(0, 2).toUpperCase()}</span><div><h2 className="text-lg font-black">{selected.full_name}</h2><p className="mt-1 text-xs text-slate-500">{selected.email} · <span className="capitalize">{selected.role}</span></p></div></div><span className={`inline-flex items-center gap-2 self-start rounded-full px-3 py-1.5 text-[9px] font-black uppercase ${selected.is_active ? 'bg-emerald-50 text-emerald-700 dark:bg-emerald-400/10 dark:text-emerald-300' : 'bg-rose-50 text-rose-700 dark:bg-rose-400/10 dark:text-rose-300'}`}>{selected.is_active ? <ShieldCheck className="h-3.5 w-3.5" /> : <ShieldOff className="h-3.5 w-3.5" />}{selected.is_active ? 'Access active' : 'Access terminated'}</span></div>

                <div className="mt-6"><div className="mb-4 flex items-center justify-between"><div><h3 className="text-sm font-black">Permission matrix</h3><p className="mt-1 text-[10px] text-slate-500">{selected.permissions.length} explicit access flag</p></div><Sparkles className="h-5 w-5 text-violet-500" /></div><PermissionMatrix member={selected} /></div>

                <div className="mt-6 border-t border-slate-200 pt-6 dark:border-white/10"><div className="flex items-center justify-between"><div><h3 className="text-sm font-black">Employee security console</h3><p className="mt-1 text-[10px] text-slate-500">Observed JWT sessions and device metadata</p></div><Laptop className="h-5 w-5 text-blue-500" /></div>
                  <div className="mt-4 space-y-3">
                    {selected.sessions?.length ? selected.sessions.map((session) => <div key={session.id} className="grid gap-3 rounded-xl border border-slate-200 p-4 text-xs sm:grid-cols-4 dark:border-white/10"><div><p className="text-[9px] uppercase text-slate-400">Login status</p><p className={`mt-1 font-black ${session.revoked_at ? 'text-rose-500' : 'text-emerald-500'}`}>{session.revoked_at ? 'Revoked' : 'Active'}</p></div><div><p className="text-[9px] uppercase text-slate-400">Device / browser</p><p className="mt-1 truncate font-bold" title={session.device}>{session.browser || session.device}</p></div><div><p className="text-[9px] uppercase text-slate-400">Last active IP</p><p className="mt-1 font-mono font-bold">{session.ip_address || 'Masked / unknown'}</p></div><div><p className="text-[9px] uppercase text-slate-400">Last active</p><p className="mt-1 font-bold">{new Intl.DateTimeFormat('uz-UZ', { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(session.last_active_at))}</p></div></div>) : <div className="rounded-xl border border-dashed border-slate-200 p-5 text-center text-xs text-slate-500 dark:border-white/10">Xodim hali JWT bilan private API’ga kirmagan.</div>}
                  </div>
                  {workspace.membership.can_manage_team && selected.role !== 'owner' && selected.is_active && <button type="button" onClick={revokeAccess} disabled={terminating} className="mt-4 inline-flex items-center gap-2 rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-xs font-black text-rose-700 transition hover:bg-rose-100 disabled:opacity-50 dark:border-rose-400/20 dark:bg-rose-400/10 dark:text-rose-300"><Trash2 className="h-4 w-4" />{terminating ? 'Terminating...' : 'Revoke Session / Terminate Access'}</button>}
                </div>
              </section>}
            </div>
          </div>
        </div>
      </div>
      {showModal && <AddMemberModal companyId={workspace.company.id} onClose={() => setShowModal(false)} onCreated={(member) => { setMembers((current) => [...current, member]); setSelectedId(member.id); setShowModal(false); }} />}
    </main>
  );
}
