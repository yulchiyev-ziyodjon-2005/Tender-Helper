import { useState } from 'react';
import { Link } from 'react-router-dom';
import { AlertCircle, ArrowLeft, CheckCircle2, Mail } from 'lucide-react';
import AuthShell from '../components/auth/AuthShell';
import { requestPasswordReset } from '../api/auth';
import { getApiError } from '../utils/security';
import { isValidEmail } from '../utils/validators';

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSent, setIsSent] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    if (!isValidEmail(email)) {
      setError('To‘g‘ri email manzilini kiriting.');
      return;
    }

    setIsLoading(true);
    setError('');
    try {
      await requestPasswordReset(email.trim().toLowerCase());
      setIsSent(true);
    } catch (requestError) {
      setError(getApiError(requestError, 'So‘rov yuborilmadi. Qayta urinib ko‘ring.'));
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <AuthShell
      eyebrow="Hisob xavfsizligi"
      title="Parolni tiklash"
      description="Hisobingizga biriktirilgan emailga xavfsiz tiklash havolasini yuboramiz."
    >
      <div className="rounded-[26px] border border-slate-200 bg-white p-5 shadow-xl shadow-slate-900/5 sm:p-7 dark:border-white/10 dark:bg-white/[0.025]">
        {isSent ? (
          <div className="text-center">
            <CheckCircle2 className="mx-auto h-12 w-12 text-emerald-500" />
            <h2 className="mt-4 text-xl font-black">Emailni tekshiring</h2>
            <p className="mt-3 text-sm leading-6 text-slate-500">
              Agar bu email ro‘yxatdan o‘tgan bo‘lsa, parolni tiklash havolasi yuborildi.
            </p>
            <Link to="/login" className="mt-6 inline-flex items-center gap-2 rounded-xl bg-blue-600 px-5 py-3 text-sm font-extrabold text-white">
              <ArrowLeft className="h-4 w-4" /> Kirishga qaytish
            </Link>
          </div>
        ) : (
          <form onSubmit={handleSubmit} noValidate>
            {error && <div role="alert" className="mb-5 flex gap-3 rounded-xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-800 dark:border-rose-500/30 dark:bg-rose-500/10 dark:text-rose-200"><AlertCircle className="h-5 w-5 shrink-0" />{error}</div>}
            <label className="block">
              <span className="mb-2 block text-sm font-bold text-slate-700 dark:text-slate-200">Email</span>
              <span className="flex items-center rounded-xl border border-slate-200 bg-white focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-500/25 dark:border-white/10 dark:bg-white/[0.035]">
                <Mail className="ml-4 h-4 w-4 text-slate-400" />
                <input type="email" value={email} onChange={(event) => { setEmail(event.target.value); setError(''); }} autoComplete="email" autoFocus placeholder="name@company.uz" className="min-w-0 flex-1 bg-transparent px-3 py-3.5 text-sm outline-none" />
              </span>
            </label>
            <button type="submit" disabled={isLoading} className="mt-6 w-full rounded-xl bg-blue-600 px-4 py-3.5 text-sm font-extrabold text-white disabled:opacity-60">
              {isLoading ? 'Yuborilmoqda...' : 'Tiklash havolasini yuborish'}
            </button>
            <Link to="/login" className="mt-4 flex items-center justify-center gap-2 text-sm font-bold text-slate-500 hover:text-blue-600">
              <ArrowLeft className="h-4 w-4" /> Kirishga qaytish
            </Link>
          </form>
        )}
      </div>
    </AuthShell>
  );
}
