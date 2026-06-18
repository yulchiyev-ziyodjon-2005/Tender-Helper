import { useMemo, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  AlertCircle,
  ArrowRight,
  Building2,
  CheckCircle2,
  FileLock2,
  LoaderCircle,
  MapPin,
  PencilLine,
  Search,
  ShieldAlert,
  UserRound,
} from 'lucide-react';
import BrandMark from '../components/brand/BrandMark';
import ThemeToggle from '../components/ui/ThemeToggle';
import {
  confirmRegistryDraft,
  lookupCompanyRegistry,
  skipStirOnboarding,
} from '../api/companies';
import { getApiError, sanitizePlainText } from '../utils/security';
import { isValidSTIR } from '../utils/validators';

const registryDefaults = {
  company_name: '',
  company_type: 'mchj',
  industry: 'boshqa',
  experience_level: 'beginner',
  director_name: '',
  legal_address: '',
  registration_date: null,
  has_vat: false,
};

function normalizeDraft(data, fallbackCompany) {
  const normalized = data?.normalized_data || {};
  return {
    company_name: sanitizePlainText(normalized.company_name || fallbackCompany || registryDefaults.company_name),
    company_type: normalized.company_type || registryDefaults.company_type,
    industry: sanitizePlainText(normalized.industry || registryDefaults.industry),
    experience_level: normalized.experience_level || registryDefaults.experience_level,
    director_name: sanitizePlainText(normalized.director_name || registryDefaults.director_name),
    legal_address: sanitizePlainText(normalized.legal_address || ''),
    registration_date: normalized.registration_date || registryDefaults.registration_date,
    has_vat: Boolean(normalized.has_vat),
  };
}

export default function OnboardingPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const company = location.state?.company;
  const [stir, setStir] = useState('');
  const [draftId, setDraftId] = useState('');
  const [draft, setDraft] = useState(null);
  const [editing, setEditing] = useState(false);
  const [status, setStatus] = useState('idle');
  const [error, setError] = useState('');
  const [skipped, setSkipped] = useState(false);
  const canLookup = useMemo(() => isValidSTIR(stir), [stir]);

  async function lookupRegistry() {
    if (!canLookup) {
      setError('STIR aniq 9 ta raqamdan iborat bo‘lishi kerak.');
      return;
    }
    setStatus('loading');
    setError('');
    try {
      const data = await lookupCompanyRegistry(stir);
      setDraftId(data.id);
      if (data.status === 'ready') {
        setDraft(normalizeDraft(data, company?.company_name));
      } else {
        setDraft(null);
        setError(
          data.error_message
          || 'Registry ma’lumot topmadi. STIRni tekshiring yoki hozircha o‘tkazib yuboring.',
        );
      }
      setStatus(data.status || 'ready');
    } catch (requestError) {
      setStatus('error');
      setError(getApiError(requestError, 'Registry provayderiga ulanib bo‘lmadi. Keyinroq qayta urinib ko‘ring.'));
    }
  }

  async function confirmDraft() {
    if (!draftId || !draft) return;
    setStatus('confirming');
    setError('');
    try {
      await confirmRegistryDraft(draftId, draft);
      setStatus('confirmed');
    } catch (requestError) {
      setStatus('ready');
      setError(getApiError(requestError, 'Registry draft tasdiqlanmadi.'));
    }
  }

  async function skipStir() {
    setStatus('skipping');
    setError('');
    try {
      await skipStirOnboarding({
        company_name: company?.company_name || 'Kompaniya',
        company_type: company?.company_type || 'mchj',
        industry: company?.industry || 'boshqa',
        experience_level: company?.experience_level || 'beginner',
      });
      setSkipped(true);
      setStatus('skipped');
    } catch (requestError) {
      setStatus('idle');
      setError(getApiError(requestError, 'STIR bosqichini o‘tkazib yuborib bo‘lmadi.'));
    }
  }

  function updateDraft(event) {
    const { name, value, checked, type } = event.target;
    setDraft((current) => ({
      ...current,
      [name]: type === 'checkbox' ? checked : sanitizePlainText(value),
    }));
  }

  const isBusy = ['loading', 'confirming', 'skipping'].includes(status);
  const isComplete = status === 'confirmed' || skipped;

  return (
    <main className="min-h-screen bg-slate-50 text-slate-950 dark:bg-[#050b14] dark:text-white">
      <header className="border-b border-slate-200 bg-white/90 px-5 py-4 backdrop-blur dark:border-white/10 dark:bg-[#08111f]/90">
        <div className="mx-auto flex max-w-6xl items-center justify-between"><BrandMark /><ThemeToggle /></div>
      </header>
      <div className="mx-auto max-w-6xl px-5 py-10 sm:py-14">
        {/* WP1: registry lookup remains a draft until the user confirms it. */}
        <div className="mb-9 grid grid-cols-3 gap-2">
          {['Hisob', 'Telefon', 'STIR tasdiqlash', 'Ish maydoni'].map((item, index) => (
            <div key={item}><div className={`h-1 rounded-full ${index <= 2 ? 'bg-blue-600' : 'bg-slate-200 dark:bg-white/10'}`} /><span className={`mt-2 block text-[10px] font-bold uppercase tracking-wider ${index <= 2 ? 'text-blue-600 dark:text-cyan-300' : 'text-slate-400'}`}>{item}</span></div>
          ))}
        </div>

        <div className="grid gap-6 lg:grid-cols-[.85fr_1.15fr]">
          <section>
            <p className="text-xs font-extrabold uppercase tracking-[0.2em] text-blue-600 dark:text-cyan-300">3 / 4 · Company registry</p>
            <h1 className="text-balance mt-4 text-4xl font-black tracking-[-0.045em]">Kompaniyangizni tasdiqlang.</h1>
            <p className="mt-5 text-sm leading-7 text-slate-500">9 xonali STIR orqali rasmiy registry ma’lumotlarini topamiz. Natija avval draft sifatida ko‘rsatiladi va faqat siz tasdiqlagandan keyin profilga yoziladi.</p>

            <div className="mt-8 rounded-2xl border border-slate-200 bg-white p-5 dark:border-white/10 dark:bg-white/[0.025]">
              <label className="text-sm font-bold">STIR (TIN)</label>
              <div className={`mt-2 flex rounded-xl border bg-slate-50 focus-within:ring-2 focus-within:ring-blue-500/20 dark:bg-white/[0.035] ${error && !draft ? 'border-rose-500' : 'border-slate-200 focus-within:border-blue-500 dark:border-white/10'}`}>
                <input value={stir} onChange={(event) => { setStir(event.target.value.replace(/\D/g, '').slice(0, 9)); setError(''); }} inputMode="numeric" pattern="[0-9]{9}" maxLength={9} placeholder="123456789" className="min-w-0 flex-1 bg-transparent px-4 py-3.5 font-mono text-sm tracking-[0.18em] outline-none" aria-describedby="stir-help" />
                <button type="button" onClick={lookupRegistry} disabled={!canLookup || isBusy} className="m-1.5 inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 text-xs font-extrabold text-white disabled:opacity-50">{status === 'loading' ? <LoaderCircle className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />} Lookup</button>
              </div>
              <p id="stir-help" className="mt-2 text-xs text-slate-400">Faqat raqamlar. Registry request audit metadata bilan qayd etiladi.</p>
              <button type="button" onClick={skipStir} disabled={isBusy} className="mt-5 w-full rounded-xl border border-slate-200 px-4 py-3 text-sm font-extrabold text-slate-600 transition hover:border-slate-300 hover:bg-slate-50 disabled:opacity-50 dark:border-white/10 dark:text-slate-300 dark:hover:bg-white/5">Hozircha o‘tkazib yuborish</button>
            </div>

            <div className="mt-5 rounded-2xl border border-amber-200 bg-amber-50 p-5 dark:border-amber-400/20 dark:bg-amber-400/10">
              <div className="flex items-center gap-2 text-sm font-black text-amber-900 dark:text-amber-200"><ShieldAlert className="h-5 w-5" /> Feature gated</div>
              <p className="mt-2 text-xs leading-5 text-amber-800/80 dark:text-amber-100/70">STIR tasdiqlanmasa quyidagi imkoniyatlar yopiq qoladi:</p>
              <ul className="mt-3 space-y-2 text-xs font-semibold text-amber-900 dark:text-amber-100">
                <li className="flex gap-2"><FileLock2 className="h-4 w-4" /> Rasmiy AI Document Generator va export</li>
                <li className="flex gap-2"><FileLock2 className="h-4 w-4" /> Competitor Intelligence baseline</li>
              </ul>
            </div>
          </section>

          <section className="min-h-[550px] rounded-[28px] border border-slate-200 bg-white p-5 shadow-xl shadow-slate-900/5 sm:p-7 dark:border-white/10 dark:bg-white/[0.025]">
            {error && <div role="alert" className="mb-5 flex gap-3 rounded-xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-800 dark:border-rose-500/30 dark:bg-rose-500/10 dark:text-rose-200"><AlertCircle className="h-5 w-5 shrink-0" />{error}</div>}

            {!draft && !isComplete && (
              <div className="grid h-full min-h-[480px] place-items-center text-center">
                <div className="max-w-sm">
                  <span className="mx-auto grid h-16 w-16 place-items-center rounded-2xl bg-blue-50 text-blue-600 dark:bg-blue-500/10 dark:text-cyan-300"><Building2 className="h-7 w-7" /></span>
                  <h2 className="mt-5 text-xl font-black">Registry company draft</h2>
                  <p className="mt-3 text-sm leading-6 text-slate-500">STIR lookup’dan keyin normalized kompaniya nomi, rahbar, manzil va registry statusi shu yerda paydo bo‘ladi.</p>
                </div>
              </div>
            )}

            {draft && status === 'ready' && (
              <div>
                <div className="flex flex-wrap items-start justify-between gap-3 border-b border-slate-200 pb-5 dark:border-white/10">
                  <div><p className="text-[10px] font-extrabold uppercase tracking-[0.18em] text-slate-400">Registry draft · {stir}</p><h2 className="mt-2 text-2xl font-black">{draft.company_name}</h2></div>
                  <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-50 px-3 py-1.5 text-[10px] font-black text-emerald-700 dark:bg-emerald-400/10 dark:text-emerald-300"><CheckCircle2 className="h-3.5 w-3.5" /> REGISTRY READY</span>
                </div>

                <div className="mt-6 grid gap-4">
                  {[
                    ['company_name', 'Kompaniya nomi', Building2],
                    ['director_name', 'Direktor', UserRound],
                    ['legal_address', 'Yuridik manzil', MapPin],
                    ['industry', 'Faoliyat sohasi', Building2],
                  ].map(([name, label, Icon]) => (
                    <label key={name} className="block">
                      <span className="mb-2 flex items-center gap-2 text-xs font-bold text-slate-500"><Icon className="h-3.5 w-3.5" />{label}</span>
                      <input name={name} value={draft[name]} onChange={updateDraft} readOnly={!editing} className={`w-full rounded-xl border px-4 py-3 text-sm outline-none transition ${editing ? 'border-blue-500 bg-blue-50/50 focus:ring-2 focus:ring-blue-500/20 dark:bg-blue-500/5' : 'border-slate-200 bg-slate-50 dark:border-white/10 dark:bg-white/[0.035]'}`} />
                    </label>
                  ))}
                  <label className="flex items-center justify-between rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm dark:border-white/10 dark:bg-white/[0.035]"><span><b className="block">QQS statusi</b><small className="text-slate-400">Registry va kalkulyator uchun</small></span><input type="checkbox" name="has_vat" checked={draft.has_vat} onChange={updateDraft} disabled={!editing} className="h-5 w-5 accent-blue-600" /></label>
                </div>

                <div className="mt-7 grid gap-3 sm:grid-cols-2">
                  <button type="button" onClick={() => setEditing((value) => !value)} className="inline-flex items-center justify-center gap-2 rounded-xl border border-slate-200 px-4 py-3 text-sm font-extrabold dark:border-white/10"><PencilLine className="h-4 w-4" />{editing ? 'Tahrirni yakunlash' : 'Maydonlarni tahrirlash'}</button>
                  <button type="button" onClick={confirmDraft} disabled={status === 'confirming'} className="inline-flex items-center justify-center gap-2 rounded-xl bg-blue-600 px-4 py-3 text-sm font-extrabold text-white disabled:opacity-60">{status === 'confirming' ? <LoaderCircle className="h-4 w-4 animate-spin" /> : <CheckCircle2 className="h-4 w-4" />} Profilni tasdiqlash</button>
                </div>
              </div>
            )}

            {isComplete && (
              <div className="grid h-full min-h-[480px] place-items-center text-center">
                <div className="max-w-md">
                  <span className={`mx-auto grid h-16 w-16 place-items-center rounded-full ${skipped ? 'bg-amber-50 text-amber-600 dark:bg-amber-400/10' : 'bg-emerald-50 text-emerald-600 dark:bg-emerald-400/10'}`}><CheckCircle2 className="h-8 w-8" /></span>
                  <h2 className="mt-6 text-2xl font-black">{skipped ? 'STIR keyinroq tasdiqlanadi' : 'Kompaniya tasdiqlandi'}</h2>
                  <p className="mt-3 text-sm leading-6 text-slate-500">{skipped ? 'Asosiy qidiruv va 4 ta bepul tahlil ochiq. Gated imkoniyatlar STIR tasdiqlangandan keyin faollashadi.' : 'Registry ma’lumotlari profilingizga xavfsiz yozildi. Business funksiyalari entitlement asosida ishlaydi.'}</p>
                  <button type="button" onClick={() => navigate('/dashboard', { replace: true })} className="mt-7 inline-flex items-center gap-2 rounded-xl bg-blue-600 px-6 py-3.5 text-sm font-extrabold text-white">Ish maydoniga o‘tish <ArrowRight className="h-4 w-4" /></button>
                </div>
              </div>
            )}
          </section>
        </div>
      </div>
    </main>
  );
}
