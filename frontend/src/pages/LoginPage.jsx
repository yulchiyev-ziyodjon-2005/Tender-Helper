import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { AlertCircle, Eye, EyeOff, LockKeyhole, Mail, ShieldCheck } from 'lucide-react';
import AuthShell from '../components/auth/AuthShell';
import GoogleLoginButton from '../components/auth/GoogleLoginButton';
import { loginWithEmail } from '../api/auth';
import useAuthStore from '../store/authStore';
import { getApiError } from '../utils/security';
import { isValidEmail } from '../utils/validators';

function InputField({ label, icon: Icon, error, action, ...inputProps }) {
  return (
    <label className="block">
      <span className="mb-2 block text-sm font-bold text-slate-700 dark:text-slate-200">{label}</span>
      <span className={`flex items-center rounded-xl border bg-white transition focus-within:ring-2 focus-within:ring-blue-500/25 dark:bg-white/[0.035] ${error ? 'border-rose-500' : 'border-slate-200 focus-within:border-blue-500 dark:border-white/10'}`}>
        <Icon className="ml-4 h-4 w-4 shrink-0 text-slate-400" />
        <input {...inputProps} className="min-w-0 flex-1 bg-transparent px-3 py-3.5 text-sm outline-none placeholder:text-slate-400" />
        {action}
      </span>
      {error && <span className="mt-1.5 block text-xs font-semibold text-rose-600">{error}</span>}
    </label>
  );
}

export default function LoginPage() {
  const navigate = useNavigate();
  const login = useAuthStore((state) => state.login);
  const [form, setForm] = useState({ email: '', password: '', remember: false });
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [fieldErrors, setFieldErrors] = useState({});
  const [alert, setAlert] = useState(
    () => new URLSearchParams(window.location.search).get('google_error') || '',
  );

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    if (params.has('google_error')) {
      window.history.replaceState({}, '', '/login');
    }
  }, []);

  function updateField(event) {
    const { name, value, checked, type } = event.target;
    setForm((current) => ({ ...current, [name]: type === 'checkbox' ? checked : value }));
    setFieldErrors((current) => ({ ...current, [name]: '' }));
    setAlert('');
  }

  async function handleSubmit(event) {
    event.preventDefault();
    const errors = {};
    if (!isValidEmail(form.email)) errors.email = 'To‘g‘ri ish emailini kiriting.';
    if (form.password.length < 8) errors.password = 'Parol kamida 8 belgidan iborat bo‘lishi kerak.';
    setFieldErrors(errors);
    if (Object.keys(errors).length) return;

    setIsLoading(true);
    setAlert('');
    try {
      const data = await loginWithEmail({
        email: form.email.trim().toLowerCase(),
        password: form.password,
      });
      login(data.tokens, data.user, {
        remember: form.remember,
        requiresPasswordChange: data.force_password_change,
      });
      navigate(data.force_password_change ? '/change-password' : '/dashboard', { replace: true });
    } catch (error) {
      const status = error.response?.status;
      if (status === 403) {
        setAlert('403 Forbidden: Hisob bloklangan. Administrator bilan bog‘laning.');
      } else if (status === 400 || status === 401) {
        setAlert('401 Unauthorized: Email yoki parol noto‘g‘ri.');
      } else {
        setAlert(getApiError(error, 'Tizimga ulanib bo‘lmadi. Qayta urinib ko‘ring.'));
      }
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <AuthShell
      eyebrow="Secure workspace"
      title="Tizimga kirish"
      description="Tender ish maydoningizga xavfsiz kirish uchun korporativ emailingizdan foydalaning."
    >
      {/* WP1: canonical email/password authentication with explicit session persistence. */}
      <div className="rounded-[26px] border border-slate-200 bg-white p-5 shadow-xl shadow-slate-900/5 sm:p-7 dark:border-white/10 dark:bg-white/[0.025]">
        {alert && (
          <div role="alert" className="mb-5 flex gap-3 rounded-xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-800 dark:border-rose-500/30 dark:bg-rose-500/10 dark:text-rose-200">
            <AlertCircle className="mt-0.5 h-5 w-5 shrink-0" />
            <span>{alert}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} noValidate className="space-y-5">
          <InputField
            label="Work email"
            icon={Mail}
            type="email"
            name="email"
            value={form.email}
            onChange={updateField}
            placeholder="name@company.uz"
            autoComplete="email"
            required
            error={fieldErrors.email}
          />
          <InputField
            label="Parol"
            icon={LockKeyhole}
            type={showPassword ? 'text' : 'password'}
            name="password"
            value={form.password}
            onChange={updateField}
            placeholder="Kamida 8 belgi"
            autoComplete="current-password"
            required
            error={fieldErrors.password}
            action={(
              <button type="button" onClick={() => setShowPassword((value) => !value)} className="mr-2 grid h-9 w-9 place-items-center rounded-lg text-slate-400 transition hover:bg-slate-100 hover:text-slate-900 dark:hover:bg-white/10 dark:hover:text-white" aria-label={showPassword ? 'Parolni yashirish' : 'Parolni ko‘rsatish'}>
                {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
            )}
          />

          <div className="flex items-center justify-between gap-3 text-sm">
            <label className="flex cursor-pointer items-center gap-2 text-slate-600 dark:text-slate-300">
              <input type="checkbox" name="remember" checked={form.remember} onChange={updateField} className="h-4 w-4 rounded border-slate-300 accent-blue-600" />
              Meni eslab qol
            </label>
            <Link to="/forgot-password" className="font-bold text-blue-600 hover:text-blue-700 dark:text-cyan-300">Parolni unutdingizmi?</Link>
          </div>

          <button type="submit" disabled={isLoading} className="flex w-full items-center justify-center rounded-xl bg-blue-600 px-4 py-3.5 text-sm font-extrabold text-white shadow-lg shadow-blue-600/15 transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60">
            {isLoading ? 'Tekshirilmoqda...' : 'Xavfsiz kirish'}
          </button>
        </form>

        <div className="relative my-6"><div className="border-t border-slate-200 dark:border-white/10" /><span className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 bg-white px-3 text-[10px] font-bold uppercase tracking-wider text-slate-400 dark:bg-[#111925]">yoki</span></div>
        <GoogleLoginButton disabled={isLoading} />

        <div className="mt-6 flex gap-3 rounded-xl bg-slate-50 p-3.5 dark:bg-white/[0.035]">
          <ShieldCheck className="h-5 w-5 shrink-0 text-emerald-500" />
          <p className="text-xs leading-5 text-slate-500">Standart sessiya brauzer yopilganda tugaydi. “Meni eslab qol” faqat shaxsiy qurilmada ishlatilishi kerak.</p>
        </div>
      </div>
      <p className="mt-6 text-center text-sm text-slate-500">Hisobingiz yo‘qmi? <Link to="/register" className="font-extrabold text-blue-600 dark:text-cyan-300">Ro‘yxatdan o‘ting</Link></p>
    </AuthShell>
  );
}
