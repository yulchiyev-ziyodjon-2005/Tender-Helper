import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AlertCircle, Eye, EyeOff, KeyRound, ShieldCheck } from 'lucide-react';
import AuthShell from '../components/auth/AuthShell';
import { changePassword } from '../api/auth';
import useAuthStore from '../store/authStore';
import { getApiError } from '../utils/security';

export default function ChangePasswordPage() {
  const navigate = useNavigate();
  const login = useAuthStore((state) => state.login);
  const [form, setForm] = useState({ current: '', next: '', confirm: '' });
  const [show, setShow] = useState(false);
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);

  async function submit(event) {
    event.preventDefault();
    if (form.next !== form.confirm) {
      setError('Yangi parollar bir xil emas.');
      return;
    }
    setSaving(true);
    try {
      const data = await changePassword({
        current_password: form.current,
        new_password: form.next,
      });
      login(data.tokens, data.user, { remember: false });
      navigate('/team', { replace: true });
    } catch (requestError) {
      setError(getApiError(requestError, 'Parolni almashtirib bo‘lmadi.'));
    } finally {
      setSaving(false);
    }
  }

  return (
    <AuthShell eyebrow="Security checkpoint" title="Vaqtinchalik parolni almashtiring" description="Administrator bergan parol bir martalik. Ish maydoniga kirishdan oldin faqat siz biladigan yangi parol yarating.">
      <form onSubmit={submit} className="rounded-[26px] border border-slate-200 bg-white p-6 shadow-xl dark:border-white/10 dark:bg-white/[0.025]">
        <div className="mb-5 flex gap-3 rounded-xl border border-blue-200 bg-blue-50 p-4 text-xs leading-5 text-blue-800 dark:border-cyan-400/20 dark:bg-cyan-400/10 dark:text-cyan-100"><ShieldCheck className="h-5 w-5 shrink-0" />Boshqa barcha private API va workspace route’lari yangi parol o‘rnatilguncha bloklangan.</div>
        {error && <div role="alert" className="mb-5 flex gap-2 rounded-xl border border-rose-200 bg-rose-50 p-3 text-xs text-rose-700 dark:border-rose-400/20 dark:bg-rose-400/10 dark:text-rose-200"><AlertCircle className="h-4 w-4" />{error}</div>}
        <div className="space-y-4">
          {[
            ['current', 'Joriy vaqtinchalik parol'],
            ['next', 'Yangi kuchli parol'],
            ['confirm', 'Yangi parolni tasdiqlang'],
          ].map(([name, label]) => <label key={name} className="block"><span className="mb-2 block text-xs font-bold">{label}</span><span className="flex items-center rounded-xl border border-slate-200 bg-slate-50 focus-within:border-blue-500 dark:border-white/10 dark:bg-white/[0.035]"><KeyRound className="ml-4 h-4 w-4 text-slate-400" /><input type={show ? 'text' : 'password'} value={form[name]} onChange={(event) => setForm((current) => ({ ...current, [name]: event.target.value.slice(0, 128) }))} required minLength={8} autoComplete={name === 'current' ? 'current-password' : 'new-password'} className="min-w-0 flex-1 bg-transparent px-3 py-3.5 text-sm outline-none" />{name === 'next' && <button type="button" onClick={() => setShow((value) => !value)} className="mr-2 grid h-9 w-9 place-items-center rounded-lg text-slate-400" aria-label="Parol ko‘rinishini almashtirish">{show ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}</button>}</span></label>)}
        </div>
        <button type="submit" disabled={saving} className="mt-6 w-full rounded-xl bg-blue-600 px-4 py-3.5 text-sm font-black text-white disabled:opacity-50">{saving ? 'Yangilanmoqda...' : 'Parolni yangilash va davom etish'}</button>
      </form>
    </AuthShell>
  );
}
