import { useMemo, useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { AlertCircle, CheckCircle2, Eye, EyeOff, LockKeyhole } from 'lucide-react';
import AuthShell from '../components/auth/AuthShell';
import { resetPassword } from '../api/auth';
import { getApiError } from '../utils/security';

export default function ResetPasswordPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const uid = searchParams.get('uid') || '';
  const token = searchParams.get('token') || '';
  const hasToken = useMemo(() => Boolean(uid && token), [token, uid]);
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isComplete, setIsComplete] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    if (password.length < 8) {
      setError('Parol kamida 8 belgidan iborat bo‘lishi kerak.');
      return;
    }
    if (password !== confirmPassword) {
      setError('Parollar bir xil emas.');
      return;
    }

    setIsLoading(true);
    setError('');
    try {
      await resetPassword({
        uid,
        token,
        new_password: password,
      });
      setIsComplete(true);
      window.setTimeout(() => navigate('/login', { replace: true }), 1800);
    } catch (requestError) {
      setError(getApiError(requestError, 'Tiklash havolasi yaroqsiz yoki muddati tugagan.'));
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <AuthShell
      eyebrow="Hisob xavfsizligi"
      title="Yangi parol o‘rnating"
      description="Yangi parol boshqa xizmatlarda ishlatilmagan va kamida 8 belgidan iborat bo‘lsin."
    >
      <div className="rounded-[26px] border border-slate-200 bg-white p-5 shadow-xl shadow-slate-900/5 sm:p-7 dark:border-white/10 dark:bg-white/[0.025]">
        {isComplete ? (
          <div className="text-center">
            <CheckCircle2 className="mx-auto h-12 w-12 text-emerald-500" />
            <h2 className="mt-4 text-xl font-black">Parol yangilandi</h2>
            <p className="mt-2 text-sm text-slate-500">Kirish sahifasiga yo‘naltirilmoqda.</p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} noValidate>
            {(!hasToken || error) && <div role="alert" className="mb-5 flex gap-3 rounded-xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-800 dark:border-rose-500/30 dark:bg-rose-500/10 dark:text-rose-200"><AlertCircle className="h-5 w-5 shrink-0" />{error || 'Tiklash havolasi to‘liq emas.'}</div>}
            <label className="block">
              <span className="mb-2 block text-sm font-bold">Yangi parol</span>
              <span className="flex items-center rounded-xl border border-slate-200 focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-500/25 dark:border-white/10">
                <LockKeyhole className="ml-4 h-4 w-4 text-slate-400" />
                <input type={showPassword ? 'text' : 'password'} value={password} onChange={(event) => { setPassword(event.target.value.slice(0, 128)); setError(''); }} autoComplete="new-password" className="min-w-0 flex-1 bg-transparent px-3 py-3.5 text-sm outline-none" />
                <button type="button" onClick={() => setShowPassword((current) => !current)} className="mr-2 grid h-9 w-9 place-items-center rounded-lg text-slate-400" aria-label={showPassword ? 'Parolni yashirish' : 'Parolni ko‘rsatish'}>{showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}</button>
              </span>
            </label>
            <label className="mt-5 block">
              <span className="mb-2 block text-sm font-bold">Parolni tasdiqlang</span>
              <span className="flex items-center rounded-xl border border-slate-200 focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-500/25 dark:border-white/10">
                <LockKeyhole className="ml-4 h-4 w-4 text-slate-400" />
                <input type={showPassword ? 'text' : 'password'} value={confirmPassword} onChange={(event) => { setConfirmPassword(event.target.value.slice(0, 128)); setError(''); }} autoComplete="new-password" className="min-w-0 flex-1 bg-transparent px-3 py-3.5 text-sm outline-none" />
              </span>
            </label>
            <button type="submit" disabled={isLoading || !hasToken} className="mt-6 w-full rounded-xl bg-blue-600 px-4 py-3.5 text-sm font-extrabold text-white disabled:opacity-60">
              {isLoading ? 'Yangilanmoqda...' : 'Parolni yangilash'}
            </button>
            {!hasToken && <Link to="/forgot-password" className="mt-4 block text-center text-sm font-bold text-blue-600">Yangi havola so‘rash</Link>}
          </form>
        )}
      </div>
    </AuthShell>
  );
}
