import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { motion, AnimatePresence } from 'framer-motion';
import { Link } from 'react-router-dom';
import { ArrowLeft, Phone, ShieldCheck } from 'lucide-react';
import GoogleLoginButton from '../components/auth/GoogleLoginButton';
import OTPVerification from '../components/auth/OTPVerification';
import LanguageSwitcher from '../components/ui/LanguageSwitcher';
import ThemeToggle from '../components/ui/ThemeToggle';

export default function LoginPage() {
  const { t } = useTranslation();
  const [phoneNumber, setPhoneNumber] = useState('');
  const [otpSentTo, setOtpSentTo] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const normalizedPhone = `+998${phoneNumber.replace(/\D/g, '').slice(0, 9)}`;
  const canSubmit = phoneNumber.replace(/\D/g, '').length === 9;

  const handlePhoneChange = (event) => {
    setPhoneNumber(event.target.value.replace(/\D/g, '').slice(0, 9));
    setError('');
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!canSubmit) {
      setError(t('errors.invalid_phone'));
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const response = await fetch('/api/v1/auth/send-otp/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone_number: normalizedPhone }),
      });
      const data = await response.json();

      if (response.ok) {
        setOtpSentTo(data.phone_number || normalizedPhone);
      } else {
        setError(data.message || t('messages.error_occurred'));
      }
    } catch {
      setError(t('messages.network_error'));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-surface-50 dark:bg-surface-950 transition-colors duration-300">
      <div className="flex justify-between items-center p-4">
        <Link to="/" className="text-surface-500 hover:text-surface-900 dark:hover:text-white flex items-center gap-2 text-sm font-medium transition-colors">
          <ArrowLeft className="w-4 h-4" />
          Asosiy sahifaga qaytish
        </Link>
        <div className="flex items-center gap-2">
          <ThemeToggle />
          <LanguageSwitcher />
        </div>
      </div>

      <div className="flex-1 flex items-center justify-center px-4 pb-8">
        <div className="w-full max-w-md">
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="text-center mb-8 flex flex-col items-center"
          >
            <div className="w-24 h-24 mb-4 flex items-center justify-center">
              <img
                src="/logo/logo-cropped.png"
                alt="TenderHelper Logo"
                className="w-full h-full object-contain drop-shadow-md"
              />
            </div>
            <h1 className="text-2xl font-bold text-surface-900 dark:text-white">
              TenderHelper AI
            </h1>
            <p className="text-surface-500 mt-1 text-sm">
              Tenderlarda yutish ehtimolini oshiring
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="bg-white dark:bg-surface-900 rounded-2xl shadow-card border border-surface-200 dark:border-surface-800 overflow-hidden"
          >
            <AnimatePresence mode="wait">
              {otpSentTo ? (
                <motion.div
                  key="otp"
                  initial={{ opacity: 0, x: 16 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -16 }}
                  transition={{ duration: 0.2 }}
                >
                  <OTPVerification
                    phoneNumber={otpSentTo}
                    onBack={() => {
                      setOtpSentTo('');
                      setError('');
                    }}
                  />
                </motion.div>
              ) : (
                <motion.div
                  key="phone"
                  initial={{ opacity: 0, x: -16 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 16 }}
                  transition={{ duration: 0.2 }}
                  className="p-8"
                >
                  <div className="mb-6">
                    <div className="w-12 h-12 rounded-xl bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center mb-4">
                      <Phone className="w-6 h-6 text-primary-600 dark:text-primary-400" />
                    </div>
                    <h2 className="text-xl font-semibold text-surface-900 dark:text-white">
                      {t('auth.login_title')}
                    </h2>
                    <p className="text-sm text-surface-500 mt-1">
                      Telefon raqamingizga bir martalik SMS kod yuboramiz.
                    </p>
                  </div>

                  <form onSubmit={handleSubmit}>
                    <label className="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-1.5">
                      {t('auth.phone_label')}
                    </label>
                    <div className="flex rounded-lg border border-surface-200 dark:border-surface-700 bg-surface-50 dark:bg-surface-800 focus-within:ring-2 focus-within:ring-primary-500 transition-all">
                      <span className="px-4 py-3 text-surface-500 border-r border-surface-200 dark:border-surface-700 select-none">
                        +998
                      </span>
                      <input
                        type="tel"
                        inputMode="numeric"
                        value={phoneNumber}
                        onChange={handlePhoneChange}
                        placeholder={t('auth.phone_placeholder')}
                        className="min-w-0 flex-1 px-4 py-3 bg-transparent text-surface-900 dark:text-white placeholder-surface-400 focus:outline-none"
                      />
                    </div>

                    {error && (
                      <p className="text-sm text-danger-500 mt-4 bg-danger-50 dark:bg-danger-500/10 p-3 rounded-lg border border-danger-100 dark:border-danger-500/20">
                        {error}
                      </p>
                    )}

                    <button
                      type="submit"
                      disabled={!canSubmit || isLoading}
                      className="w-full mt-6 py-3 px-4 bg-primary-600 hover:bg-primary-700 active:bg-primary-800 disabled:opacity-50 text-white font-medium rounded-lg transition-all focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 dark:focus:ring-offset-surface-900 flex justify-center items-center"
                    >
                      {isLoading ? t('actions.loading') : t('auth.send_otp')}
                    </button>
                  </form>

                  <div className="relative my-6">
                    <div className="absolute inset-0 flex items-center">
                      <div className="w-full border-t border-surface-200 dark:border-surface-700" />
                    </div>
                    <div className="relative flex justify-center text-sm">
                      <span className="px-3 bg-white dark:bg-surface-900 text-surface-400">
                        {t('auth.or')}
                      </span>
                    </div>
                  </div>

                  <GoogleLoginButton />

                  <div className="mt-6 flex gap-3 rounded-lg bg-surface-50 dark:bg-surface-950 border border-surface-200 dark:border-surface-800 p-4">
                    <ShieldCheck className="w-5 h-5 text-success-500 flex-shrink-0 mt-0.5" />
                    <p className="text-xs text-surface-500">
                      Kirish orqali siz TenderHelper foydalanish shartlari va maxfiylik siyosatiga rozilik bildirasiz.
                    </p>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
