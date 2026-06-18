import { useEffect, useMemo, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  AlertCircle,
  ArrowLeft,
  Building2,
  Check,
  Eye,
  EyeOff,
  LockKeyhole,
  Mail,
  Phone,
  RotateCcw,
  UserRound,
} from 'lucide-react';
import AuthShell from '../components/auth/AuthShell';
import {
  registerWithEmail,
  sendOtp as sendOtpApi,
  verifyRegistrationPhone,
} from '../api/auth';
import useAuthStore from '../store/authStore';
import { getApiError, sanitizePlainText } from '../utils/security';
import { isValidEmail, isValidPhone } from '../utils/validators';

const initialForm = {
  companyName: '',
  fullName: '',
  email: '',
  phone: '',
  password: '',
  confirmPassword: '',
  terms: false,
  aiDisclaimer: false,
};

function Field({ label, icon: Icon, error, action, ...props }) {
  return (
    <label className="block">
      <span className="mb-2 block text-sm font-bold text-slate-700 dark:text-slate-200">{label}</span>
      <span className={`flex items-center rounded-xl border bg-white transition focus-within:ring-2 focus-within:ring-blue-500/25 dark:bg-white/[0.035] ${error ? 'border-rose-500' : 'border-slate-200 focus-within:border-blue-500 dark:border-white/10'}`}>
        <Icon className="ml-4 h-4 w-4 shrink-0 text-slate-400" />
        <input {...props} className="min-w-0 flex-1 bg-transparent px-3 py-3.5 text-sm outline-none placeholder:text-slate-400" />
        {action}
      </span>
      {error && <span className="mt-1.5 block text-xs font-semibold text-rose-600">{error}</span>}
    </label>
  );
}

function passwordChecks(password) {
  return [
    { label: '8+ belgi', passed: password.length >= 8 },
    { label: 'Raqam', passed: /\d/.test(password) },
    { label: 'Katta harf', passed: /[A-Z]/.test(password) },
    { label: 'Maxsus belgi', passed: /[^A-Za-z0-9]/.test(password) },
  ];
}

export default function RegisterPage() {
  const navigate = useNavigate();
  const login = useAuthStore((state) => state.login);
  const [form, setForm] = useState(initialForm);
  const [step, setStep] = useState('account');
  const [otp, setOtp] = useState('');
  const [resendAfter, setResendAfter] = useState(0);
  const [showPassword, setShowPassword] = useState(false);
  const [errors, setErrors] = useState({});
  const [alert, setAlert] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const checks = useMemo(() => passwordChecks(form.password), [form.password]);
  const strength = checks.filter((item) => item.passed).length;
  const normalizedPhone = `+${form.phone.replace(/\D/g, '')}`;

  useEffect(() => {
    if (resendAfter <= 0) return undefined;
    const timer = window.setInterval(
      () => setResendAfter((current) => Math.max(0, current - 1)),
      1000,
    );
    return () => window.clearInterval(timer);
  }, [resendAfter]);

  function updateField(event) {
    const { name, value, checked, type } = event.target;
    setForm((current) => ({
      ...current,
      [name]: type === 'checkbox'
        ? checked
        : name === 'password' || name === 'confirmPassword'
          ? value.slice(0, 128)
          : sanitizePlainText(value, 500),
    }));
    setErrors((current) => ({ ...current, [name]: '' }));
    setAlert('');
  }

  function validateAccount() {
    const next = {};
    if (form.companyName.trim().length < 2) next.companyName = 'Kompaniya nomini kiriting.';
    if (form.fullName.trim().length < 2) next.fullName = 'To‘liq ismni kiriting.';
    if (!isValidEmail(form.email)) next.email = 'To‘g‘ri ish emailini kiriting.';
    if (!isValidPhone(form.phone)) next.phone = 'Format: +998 XX XXX XX XX';
    if (strength < 3) next.password = 'Kuchliroq parol tanlang.';
    if (form.confirmPassword !== form.password) next.confirmPassword = 'Parollar bir xil emas.';
    if (!form.terms) next.terms = 'Foydalanish shartlariga rozilik majburiy.';
    if (!form.aiDisclaimer) next.aiDisclaimer = 'AI disclaimer tasdig‘i majburiy.';
    return next;
  }

  async function sendOtp() {
    await sendOtpApi(normalizedPhone);
    setResendAfter(60);
  }

  async function handleAccountSubmit(event) {
    event.preventDefault();
    const nextErrors = validateAccount();
    setErrors(nextErrors);
    if (Object.keys(nextErrors).length) return;

    setIsLoading(true);
    setAlert('');
    try {
      await sendOtp();
      setStep('verify');
      setOtp('');
    } catch (error) {
      setAlert(getApiError(error, 'Tasdiqlash kodi yuborilmadi. Qayta urinib ko‘ring.'));
    } finally {
      setIsLoading(false);
    }
  }

  async function handleVerificationSubmit(event) {
    event.preventDefault();
    if (!/^\d{6}$/.test(otp)) {
      setErrors((current) => ({ ...current, otp: '6 xonali kodni kiriting.' }));
      return;
    }

    setIsLoading(true);
    setAlert('');
    try {
      const verification = await verifyRegistrationPhone({
        phone_number: normalizedPhone,
        otp,
      });
      const data = await registerWithEmail({
        company_name: form.companyName.trim(),
        full_name: form.fullName.trim(),
        email: form.email.trim().toLowerCase(),
        phone_number: normalizedPhone,
        phone_verification_token: verification.verification_token,
        password: form.password,
        company_type: 'mchj',
        industry: 'boshqa',
        experience_level: 'beginner',
        business_type: 'supplier',
      });
      login(data.tokens, data.user, { remember: false });
      navigate('/onboarding', {
        replace: true,
        state: { company: data.company },
      });
    } catch (error) {
      const data = error.response?.data;
      const mapped = {};
      if (data?.email) mapped.email = sanitizePlainText(data.email[0]);
      if (data?.phone_number) mapped.phone = sanitizePlainText(data.phone_number[0]);
      if (data?.password) mapped.password = sanitizePlainText(data.password[0]);
      if (data?.phone_verification_token) mapped.otp = sanitizePlainText(data.phone_verification_token[0]);
      setErrors((current) => ({ ...current, ...mapped }));
      setAlert(getApiError(error, 'Hisob yaratilmadi. Ma’lumotlarni tekshirib qayta urinib ko‘ring.'));
    } finally {
      setIsLoading(false);
    }
  }

  async function resendOtp() {
    if (resendAfter > 0 || isLoading) return;
    setIsLoading(true);
    setAlert('');
    try {
      await sendOtp();
      setOtp('');
      setErrors((current) => ({ ...current, otp: '' }));
    } catch (error) {
      setAlert(getApiError(error, 'Kod qayta yuborilmadi.'));
    } finally {
      setIsLoading(false);
    }
  }

  const currentStep = step === 'account' ? 0 : 1;

  return (
    <AuthShell
      eyebrow={step === 'account' ? '1 / 4 · Hisob' : '2 / 4 · Telefon tasdig‘i'}
      title="Korporativ hisob yarating"
      description={step === 'account'
        ? 'Asosiy ma’lumotlarni kiriting. Telefon raqami SMS kod orqali tasdiqlanadi.'
        : `${normalizedPhone} raqamiga yuborilgan 6 xonali kodni kiriting.`}
    >
      <div className="mb-6 flex gap-2">
        {['Hisob', 'Telefon', 'STIR', 'Ish maydoni'].map((item, index) => (
          <div key={item} className="flex-1">
            <div className={`h-1 rounded-full ${index <= currentStep ? 'bg-blue-600' : 'bg-slate-200 dark:bg-white/10'}`} />
            <span className={`mt-2 block text-[10px] font-bold uppercase tracking-wider ${index <= currentStep ? 'text-blue-600 dark:text-cyan-300' : 'text-slate-400'}`}>{item}</span>
          </div>
        ))}
      </div>

      {step === 'account' ? (
        <form onSubmit={handleAccountSubmit} noValidate className="rounded-[26px] border border-slate-200 bg-white p-5 shadow-xl shadow-slate-900/5 sm:p-7 dark:border-white/10 dark:bg-white/[0.025]">
          {alert && <div role="alert" className="mb-5 flex gap-3 rounded-xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-800 dark:border-rose-500/30 dark:bg-rose-500/10 dark:text-rose-200"><AlertCircle className="h-5 w-5 shrink-0" />{alert}</div>}
          <div className="grid gap-5 sm:grid-cols-2">
            <div className="sm:col-span-2"><Field label="Kompaniya nomi" icon={Building2} name="companyName" value={form.companyName} onChange={updateField} placeholder="Example MChJ" autoComplete="organization" required error={errors.companyName} /></div>
            <Field label="To‘liq ism" icon={UserRound} name="fullName" value={form.fullName} onChange={updateField} placeholder="Ism Familiya" autoComplete="name" required error={errors.fullName} />
            <Field label="Ish emaili" icon={Mail} type="email" name="email" value={form.email} onChange={updateField} placeholder="name@company.uz" autoComplete="email" required error={errors.email} />
            <Field label="Telefon raqam" icon={Phone} type="tel" name="phone" value={form.phone} onChange={updateField} placeholder="+998 90 123 45 67" autoComplete="tel" required error={errors.phone} />
            <Field
              label="Parol"
              icon={LockKeyhole}
              type={showPassword ? 'text' : 'password'}
              name="password"
              value={form.password}
              onChange={updateField}
              placeholder="Kuchli parol yarating"
              autoComplete="new-password"
              required
              error={errors.password}
              action={<button type="button" onClick={() => setShowPassword((value) => !value)} className="mr-2 grid h-9 w-9 place-items-center rounded-lg text-slate-400 hover:bg-slate-100 dark:hover:bg-white/10" aria-label={showPassword ? 'Parolni yashirish' : 'Parolni ko‘rsatish'}>{showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}</button>}
            />
            <Field label="Parolni tasdiqlang" icon={LockKeyhole} type={showPassword ? 'text' : 'password'} name="confirmPassword" value={form.confirmPassword} onChange={updateField} placeholder="Parolni qayta kiriting" autoComplete="new-password" required error={errors.confirmPassword} />
          </div>

          <div className="mt-4">
            <div className="grid grid-cols-4 gap-1.5">{[1, 2, 3, 4].map((level) => <span key={level} className={`h-1.5 rounded-full ${strength >= level ? (strength >= 4 ? 'bg-emerald-500' : strength >= 3 ? 'bg-blue-500' : 'bg-amber-400') : 'bg-slate-200 dark:bg-white/10'}`} />)}</div>
            <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1">
              {checks.map((check) => <span key={check.label} className={`flex items-center gap-1 text-[10px] font-semibold ${check.passed ? 'text-emerald-600 dark:text-emerald-400' : 'text-slate-400'}`}><Check className="h-3 w-3" />{check.label}</span>)}
            </div>
          </div>

          <div className="mt-6 space-y-3">
            <label className="flex cursor-pointer items-start gap-3 text-sm text-slate-600 dark:text-slate-300">
              <input type="checkbox" name="terms" checked={form.terms} onChange={updateField} className="mt-1 h-4 w-4 shrink-0 accent-blue-600" />
              <span><Link to="/terms" className="font-bold text-blue-600 dark:text-cyan-300">Foydalanish shartlari</Link> va <Link to="/privacy" className="font-bold text-blue-600 dark:text-cyan-300">Maxfiylik siyosati</Link>ga roziman.</span>
            </label>
            {errors.terms && <p className="text-xs font-semibold text-rose-600">{errors.terms}</p>}
            <label className="flex cursor-pointer items-start gap-3 text-sm text-slate-600 dark:text-slate-300">
              <input type="checkbox" name="aiDisclaimer" checked={form.aiDisclaimer} onChange={updateField} className="mt-1 h-4 w-4 shrink-0 accent-blue-600" />
              <span>AI tahlil natijalari professional yuridik maslahat o‘rnini bosmasligini tushunaman.</span>
            </label>
            {errors.aiDisclaimer && <p className="text-xs font-semibold text-rose-600">{errors.aiDisclaimer}</p>}
          </div>

          <button type="submit" disabled={isLoading || !form.terms || !form.aiDisclaimer} className="mt-7 flex w-full items-center justify-center rounded-xl bg-blue-600 px-4 py-3.5 text-sm font-extrabold text-white shadow-lg shadow-blue-600/15 transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50">{isLoading ? 'Kod yuborilmoqda...' : 'Telefonni tasdiqlash'}</button>
        </form>
      ) : (
        <form onSubmit={handleVerificationSubmit} noValidate className="rounded-[26px] border border-slate-200 bg-white p-5 shadow-xl shadow-slate-900/5 sm:p-7 dark:border-white/10 dark:bg-white/[0.025]">
          {alert && <div role="alert" className="mb-5 flex gap-3 rounded-xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-800 dark:border-rose-500/30 dark:bg-rose-500/10 dark:text-rose-200"><AlertCircle className="h-5 w-5 shrink-0" />{alert}</div>}
          <label className="block">
            <span className="mb-2 block text-sm font-bold text-slate-700 dark:text-slate-200">SMS tasdiqlash kodi</span>
            <input
              value={otp}
              onChange={(event) => {
                setOtp(event.target.value.replace(/\D/g, '').slice(0, 6));
                setErrors((current) => ({ ...current, otp: '' }));
                setAlert('');
              }}
              inputMode="numeric"
              autoComplete="one-time-code"
              autoFocus
              placeholder="000000"
              className={`w-full rounded-xl border bg-white px-4 py-4 text-center font-mono text-2xl font-black tracking-[0.45em] outline-none transition focus:ring-2 focus:ring-blue-500/25 dark:bg-white/[0.035] ${errors.otp ? 'border-rose-500' : 'border-slate-200 focus:border-blue-500 dark:border-white/10'}`}
            />
            {errors.otp && <span className="mt-1.5 block text-xs font-semibold text-rose-600">{errors.otp}</span>}
          </label>
          <p className="mt-3 text-center text-xs leading-5 text-slate-500">Kod 3 daqiqa amal qiladi. Raqam noto‘g‘ri bo‘lsa, oldingi bosqichga qayting.</p>
          <button type="submit" disabled={isLoading || otp.length !== 6} className="mt-6 flex w-full items-center justify-center rounded-xl bg-blue-600 px-4 py-3.5 text-sm font-extrabold text-white shadow-lg shadow-blue-600/15 transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50">{isLoading ? 'Tasdiqlanmoqda...' : 'Tasdiqlash va hisob yaratish'}</button>
          <div className="mt-4 grid gap-2 sm:grid-cols-2">
            <button type="button" onClick={() => { setStep('account'); setAlert(''); }} disabled={isLoading} className="inline-flex items-center justify-center gap-2 rounded-xl border border-slate-200 px-4 py-3 text-sm font-bold dark:border-white/10"><ArrowLeft className="h-4 w-4" /> Ma’lumotlarni tahrirlash</button>
            <button type="button" onClick={resendOtp} disabled={isLoading || resendAfter > 0} className="inline-flex items-center justify-center gap-2 rounded-xl border border-slate-200 px-4 py-3 text-sm font-bold disabled:opacity-50 dark:border-white/10"><RotateCcw className="h-4 w-4" /> {resendAfter > 0 ? `Qayta yuborish: ${resendAfter}s` : 'Kodni qayta yuborish'}</button>
          </div>
        </form>
      )}
      <p className="mt-6 text-center text-sm text-slate-500">Hisobingiz bormi? <Link to="/login" className="font-extrabold text-blue-600 dark:text-cyan-300">Kirish</Link></p>
    </AuthShell>
  );
}
