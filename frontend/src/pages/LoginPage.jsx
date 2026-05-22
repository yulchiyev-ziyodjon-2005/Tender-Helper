/**
 * TenderHelper AI — Login Page
 * ==============================
 * Telefon + OTP va Google OAuth kirish sahifasi.
 * i18n integratsiya, dark mode, zamonaviy animatsiyalar.
 */

import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Shield } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import OTPVerification from '../components/auth/OTPVerification';
import GoogleLoginButton from '../components/auth/GoogleLoginButton';
import LanguageSwitcher from '../components/ui/LanguageSwitcher';
import ThemeToggle from '../components/ui/ThemeToggle';

export default function LoginPage() {
  const { t } = useTranslation();
  const [phone, setPhone] = useState('');
  const [step, setStep] = useState('phone'); // 'phone' | 'otp'
  const [fullPhone, setFullPhone] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const formatPhoneInput = (value) => {
    const digits = value.replace(/\D/g, '').slice(0, 9);
    if (digits.length <= 2) return digits;
    if (digits.length <= 5) return `${digits.slice(0, 2)} ${digits.slice(2)}`;
    if (digits.length <= 7) return `${digits.slice(0, 2)} ${digits.slice(2, 5)} ${digits.slice(5)}`;
    return `${digits.slice(0, 2)} ${digits.slice(2, 5)} ${digits.slice(5, 7)} ${digits.slice(7)}`;
  };

  const handlePhoneChange = (e) => {
    const formatted = formatPhoneInput(e.target.value);
    setPhone(formatted);
    setError('');
  };

  const handleSendOTP = async (e) => {
    e.preventDefault();
    const digits = phone.replace(/\D/g, '');
    if (digits.length !== 9) {
      setError(t('errors.invalid_phone'));
      return;
    }

    const fullNumber = `+998${digits}`;
    setFullPhone(fullNumber);
    setIsLoading(true);
    setError('');

    try {
      const res = await fetch('/api/v1/auth/send-otp/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone_number: fullNumber }),
      });

      if (res.ok) {
        setStep('otp');
      } else if (res.status === 429) {
        setError(t('errors.server_error'));
      } else {
        const data = await res.json();
        setError(data.message || t('messages.error_occurred'));
      }
    } catch {
      setError(t('messages.network_error'));
    } finally {
      setIsLoading(false);
    }
  };

  const handleBackToPhone = () => {
    setStep('phone');
    setError('');
  };

  return (
    <div className="min-h-screen flex flex-col bg-surface-50 dark:bg-surface-950 transition-colors duration-300">
      {/* Top bar — theme + language */}
      <div className="flex justify-end items-center gap-2 p-4">
        <ThemeToggle />
        <LanguageSwitcher />
      </div>

      {/* Main content */}
      <div className="flex-1 flex items-center justify-center px-4 pb-8">
        <div className="w-full max-w-md">
          {/* Logo */}
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="text-center mb-8"
          >
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-primary-500 to-primary-700 shadow-lg shadow-primary-500/25 mb-4">
              <Shield className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-2xl font-bold text-surface-900 dark:text-white">
              TenderHelper AI
            </h1>
            <p className="text-surface-500 mt-1 text-sm">
              {t('auth.welcome_subtitle')}
            </p>
          </motion.div>

          {/* Card */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="bg-white dark:bg-surface-900 rounded-2xl shadow-card border border-surface-200 dark:border-surface-800 overflow-hidden"
          >
            <AnimatePresence mode="wait">
              {step === 'phone' ? (
                <motion.div
                  key="phone"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  transition={{ duration: 0.25 }}
                  className="p-8"
                >
                  <h2 className="text-lg font-semibold text-surface-900 dark:text-white mb-6">
                    {t('auth.login_title')}
                  </h2>

                  <form onSubmit={handleSendOTP}>
                    {/* Phone Number */}
                    <div className="mb-4">
                      <label className="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-1.5">
                        {t('auth.phone_label')}
                      </label>
                      <div className="flex gap-2">
                        <span className="flex items-center px-3 bg-surface-100 dark:bg-surface-800 rounded-lg text-sm text-surface-500 font-mono font-medium select-none">
                          +998
                        </span>
                        <input
                          type="tel"
                          value={phone}
                          onChange={handlePhoneChange}
                          placeholder={t('auth.phone_placeholder')}
                          className="flex-1 px-4 py-3 bg-surface-50 dark:bg-surface-800 border border-surface-200 dark:border-surface-700 rounded-lg text-surface-900 dark:text-white placeholder-surface-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all font-mono"
                          autoFocus
                        />
                      </div>
                    </div>

                    {/* Error */}
                    {error && (
                      <motion.p
                        initial={{ opacity: 0, y: -5 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="text-sm text-danger-500 mb-3"
                      >
                        {error}
                      </motion.p>
                    )}

                    {/* Submit */}
                    <button
                      type="submit"
                      disabled={isLoading || phone.replace(/\D/g, '').length < 9}
                      className="w-full py-3 px-4 bg-primary-600 hover:bg-primary-700 active:bg-primary-800 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-all duration-150 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 dark:focus:ring-offset-surface-900"
                    >
                      {isLoading ? (
                        <span className="inline-flex items-center gap-2">
                          <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                          </svg>
                          {t('actions.loading')}
                        </span>
                      ) : (
                        t('auth.send_otp')
                      )}
                    </button>
                  </form>

                  {/* Divider */}
                  <div className="relative my-6">
                    <div className="absolute inset-0 flex items-center">
                      <div className="w-full border-t border-surface-200 dark:border-surface-700"></div>
                    </div>
                    <div className="relative flex justify-center text-sm">
                      <span className="px-3 bg-white dark:bg-surface-900 text-surface-400">
                        {t('auth.or')}
                      </span>
                    </div>
                  </div>

                  {/* Google Login */}
                  <GoogleLoginButton />

                  {/* Terms */}
                  <p className="text-xs text-surface-400 text-center mt-6">
                    {t('auth.terms_notice')}
                  </p>
                </motion.div>
              ) : (
                <motion.div
                  key="otp"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                  transition={{ duration: 0.25 }}
                >
                  <OTPVerification
                    phoneNumber={fullPhone}
                    onBack={handleBackToPhone}
                  />
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
