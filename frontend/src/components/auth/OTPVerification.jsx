import { useState, useRef, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { motion } from 'framer-motion';

export default function OTPVerification({ phoneNumber, onBack }) {
  const { t } = useTranslation();
  const [otp, setOtp] = useState(['', '', '', '', '', '']);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [timeLeft, setTimeLeft] = useState(180); // 3 daqiqa
  const inputsRef = useRef([]);

  // Timer logic
  useEffect(() => {
    if (timeLeft <= 0) return;
    const timer = setInterval(() => setTimeLeft((prev) => prev - 1), 1000);
    return () => clearInterval(timer);
  }, [timeLeft]);

  // Handle OTP input
  const handleChange = (e, index) => {
    const value = e.target.value.replace(/\D/g, ''); // Faqat raqam
    if (!value) return;

    const newOtp = [...otp];
    newOtp[index] = value[0];
    setOtp(newOtp);
    setError('');

    // Avtomatik keyingi inputga o'tish
    if (index < 5 && value[0]) {
      inputsRef.current[index + 1].focus();
    }

    // Oxirgi raqam kiritilsa avtomat tekshirish
    if (index === 5 && newOtp.every(v => v !== '')) {
      verifyOtp(newOtp.join(''));
    }
  };

  const handleKeyDown = (e, index) => {
    if (e.key === 'Backspace') {
      if (!otp[index] && index > 0) {
        inputsRef.current[index - 1].focus();
        const newOtp = [...otp];
        newOtp[index - 1] = '';
        setOtp(newOtp);
      } else {
        const newOtp = [...otp];
        newOtp[index] = '';
        setOtp(newOtp);
      }
    }
  };

  const handlePaste = (e) => {
    e.preventDefault();
    const pastedData = e.clipboardData.getData('text').replace(/\D/g, '').slice(0, 6);
    if (pastedData) {
      const newOtp = [...otp];
      for (let i = 0; i < pastedData.length; i++) {
        newOtp[i] = pastedData[i];
      }
      setOtp(newOtp);
      
      const nextIndex = Math.min(pastedData.length, 5);
      inputsRef.current[nextIndex].focus();

      if (pastedData.length === 6) {
        verifyOtp(pastedData);
      }
    }
  };

  const verifyOtp = async (code) => {
    setIsLoading(true);
    setError('');

    try {
      const res = await fetch('/api/v1/auth/verify-otp/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone_number: phoneNumber, otp: code }),
      });

      const data = await res.json();

      if (res.ok) {
        // Tokenlarni saqlash
        localStorage.setItem('access_token', data.tokens.access);
        localStorage.setItem('refresh_token', data.tokens.refresh);
        
        // TODO: Update global auth store state
        // TODO: Redirect user (to onboarding or dashboard)
        window.location.href = data.is_new_user ? '/onboarding' : '/dashboard';
      } else {
        setError(data.message || t('errors.invalid_otp'));
        setOtp(['', '', '', '', '', '']); // Xato bo'lsa tozalash
        inputsRef.current[0].focus();
      }
    } catch {
      setError(t('messages.network_error'));
    } finally {
      setIsLoading(false);
    }
  };

  const handleResend = async () => {
    if (timeLeft > 0) return;
    setIsLoading(true);
    setError('');

    try {
      const res = await fetch('/api/v1/auth/send-otp/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone_number: phoneNumber }),
      });

      if (res.ok) {
        setTimeLeft(180);
        setOtp(['', '', '', '', '', '']);
        inputsRef.current[0].focus();
      } else {
        const data = await res.json();
        setError(data.message);
      }
    } catch {
      setError(t('messages.network_error'));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="p-8">
      {/* Back button */}
      <button 
        onClick={onBack}
        className="text-surface-500 hover:text-surface-900 dark:hover:text-white transition-colors flex items-center gap-2 mb-6 text-sm"
      >
        ← {t('actions.back')}
      </button>

      <h2 className="text-xl font-semibold text-surface-900 dark:text-white mb-2">
        {t('auth.otp_title')}
      </h2>
      <p className="text-sm text-surface-500 mb-6">
        {t('auth.otp_subtitle', { phone: phoneNumber })}
      </p>

      {/* OTP Inputs */}
      <div className="flex gap-2 justify-between mb-6" onPaste={handlePaste}>
        {otp.map((digit, index) => (
          <input
            key={index}
            ref={(el) => (inputsRef.current[index] = el)}
            type="text"
            inputMode="numeric"
            maxLength={1}
            value={digit}
            onChange={(e) => handleChange(e, index)}
            onKeyDown={(e) => handleKeyDown(e, index)}
            disabled={isLoading}
            className={`w-12 h-14 text-center text-xl font-bold rounded-lg border bg-surface-50 dark:bg-surface-800 text-surface-900 dark:text-white transition-all
              ${error ? 'border-danger-500 focus:ring-danger-500' : 'border-surface-200 dark:border-surface-700 focus:border-primary-500 focus:ring-primary-500'}
              focus:outline-none focus:ring-2 disabled:opacity-50
            `}
          />
        ))}
      </div>

      {error && (
        <motion.p initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-sm text-danger-500 mb-4 text-center">
          {error}
        </motion.p>
      )}

      <div className="text-center">
        {timeLeft > 0 ? (
          <p className="text-sm text-surface-500">
            {t('auth.resend_in', { seconds: timeLeft })}
          </p>
        ) : (
          <button
            onClick={handleResend}
            disabled={isLoading}
            className="text-sm font-medium text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300 disabled:opacity-50"
          >
            {t('auth.resend_otp')}
          </button>
        )}
      </div>
    </div>
  );
}
