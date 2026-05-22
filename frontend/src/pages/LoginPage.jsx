import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { motion, AnimatePresence } from 'framer-motion';
import { Link } from 'react-router-dom';
import GoogleLoginButton from '../components/auth/GoogleLoginButton';
import LanguageSwitcher from '../components/ui/LanguageSwitcher';
import ThemeToggle from '../components/ui/ThemeToggle';

export default function LoginPage() {
  const { t } = useTranslation();
  const [isLogin, setIsLogin] = useState(true); // Toggle between Login and Register
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    full_name: '',
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    const endpoint = isLogin ? '/api/v1/auth/login/' : '/api/v1/auth/register/';
    
    try {
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });

      const data = await res.json();

      if (res.ok) {
        localStorage.setItem('access_token', data.tokens.access);
        localStorage.setItem('refresh_token', data.tokens.refresh);
        
        // Agar yangi user bo'lsa Onboardingga, yo'qsa Dashboardga
        window.location.href = data.is_new_user ? '/onboarding' : '/dashboard';
      } else {
        // Handle validation errors from serializer
        let errorMsg = data.message || t('messages.error_occurred');
        if (data.email) errorMsg = data.email[0];
        if (data.password) errorMsg = data.password[0];
        setError(errorMsg);
      }
    } catch {
      setError(t('messages.network_error'));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-surface-50 dark:bg-surface-950 transition-colors duration-300">
      {/* Top bar */}
      <div className="flex justify-between items-center p-4">
        <Link to="/" className="text-surface-500 hover:text-surface-900 dark:hover:text-white flex items-center gap-2 text-sm font-medium transition-colors">
          ← Asosiy sahifaga qaytish
        </Link>
        <div className="flex items-center gap-2">
          <ThemeToggle />
          <LanguageSwitcher />
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 flex items-center justify-center px-4 pb-8">
        <div className="w-full max-w-md">
          {/* Logo */}
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="text-center mb-8 flex flex-col items-center"
          >
            <div className="w-24 h-24 mb-4 rounded-2xl overflow-hidden shadow-lg shadow-surface-200 dark:shadow-surface-900/50 flex items-center justify-center bg-white dark:bg-[#0A101D]">
              <img 
                src="/assets/logo-dark.jpg" 
                alt="TenderHelper Logo" 
                className="w-full h-full object-contain"
              />
            </div>
            <h1 className="text-2xl font-bold text-surface-900 dark:text-white">
              TenderHelper AI
            </h1>
            <p className="text-surface-500 mt-1 text-sm">
              Tenderlarda yutish ehtimolini oshiring
            </p>
          </motion.div>

          {/* Card */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="bg-white dark:bg-surface-900 rounded-2xl shadow-card border border-surface-200 dark:border-surface-800 overflow-hidden"
          >
            <div className="p-8">
              {/* Tabs */}
              <div className="flex bg-surface-100 dark:bg-surface-800 rounded-lg p-1 mb-6">
                <button
                  onClick={() => { setIsLogin(true); setError(''); }}
                  className={`flex-1 py-2 text-sm font-medium rounded-md transition-all ${isLogin ? 'bg-white dark:bg-surface-700 text-surface-900 dark:text-white shadow-sm' : 'text-surface-500 hover:text-surface-700 dark:hover:text-surface-300'}`}
                >
                  Kirish
                </button>
                <button
                  onClick={() => { setIsLogin(false); setError(''); }}
                  className={`flex-1 py-2 text-sm font-medium rounded-md transition-all ${!isLogin ? 'bg-white dark:bg-surface-700 text-surface-900 dark:text-white shadow-sm' : 'text-surface-500 hover:text-surface-700 dark:hover:text-surface-300'}`}
                >
                  Ro'yxatdan o'tish
                </button>
              </div>

              <AnimatePresence mode="wait">
                <motion.form
                  key={isLogin ? 'login' : 'register'}
                  initial={{ opacity: 0, x: isLogin ? -10 : 10 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: isLogin ? 10 : -10 }}
                  transition={{ duration: 0.2 }}
                  onSubmit={handleSubmit}
                >
                  {!isLogin && (
                    <div className="mb-4">
                      <label className="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-1.5">
                        Ismingiz (Kompaniya)
                      </label>
                      <input
                        type="text"
                        name="full_name"
                        value={formData.full_name}
                        onChange={handleChange}
                        required
                        placeholder="Ismingizni kiriting"
                        className="w-full px-4 py-3 bg-surface-50 dark:bg-surface-800 border border-surface-200 dark:border-surface-700 rounded-lg text-surface-900 dark:text-white placeholder-surface-400 focus:outline-none focus:ring-2 focus:ring-primary-500 transition-all"
                      />
                    </div>
                  )}

                  <div className="mb-4">
                    <label className="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-1.5">
                      Email
                    </label>
                    <input
                      type="email"
                      name="email"
                      value={formData.email}
                      onChange={handleChange}
                      required
                      placeholder="name@company.uz"
                      className="w-full px-4 py-3 bg-surface-50 dark:bg-surface-800 border border-surface-200 dark:border-surface-700 rounded-lg text-surface-900 dark:text-white placeholder-surface-400 focus:outline-none focus:ring-2 focus:ring-primary-500 transition-all"
                    />
                  </div>

                  <div className="mb-6">
                    <label className="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-1.5">
                      Parol
                    </label>
                    <input
                      type="password"
                      name="password"
                      value={formData.password}
                      onChange={handleChange}
                      required
                      minLength={8}
                      placeholder="••••••••"
                      className="w-full px-4 py-3 bg-surface-50 dark:bg-surface-800 border border-surface-200 dark:border-surface-700 rounded-lg text-surface-900 dark:text-white placeholder-surface-400 focus:outline-none focus:ring-2 focus:ring-primary-500 transition-all"
                    />
                  </div>

                  {error && (
                    <p className="text-sm text-danger-500 mb-4 bg-danger-50 dark:bg-danger-500/10 p-3 rounded-lg border border-danger-100 dark:border-danger-500/20">
                      {error}
                    </p>
                  )}

                  <button
                    type="submit"
                    disabled={isLoading}
                    className="w-full py-3 px-4 bg-primary-600 hover:bg-primary-700 active:bg-primary-800 disabled:opacity-50 text-white font-medium rounded-lg transition-all focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 dark:focus:ring-offset-surface-900 flex justify-center items-center"
                  >
                    {isLoading ? (
                      <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                      </svg>
                    ) : (
                      isLogin ? "Tizimga kirish" : "Ro'yxatdan o'tish"
                    )}
                  </button>
                </motion.form>
              </AnimatePresence>

              <div className="relative my-6">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-surface-200 dark:border-surface-700"></div>
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="px-3 bg-white dark:bg-surface-900 text-surface-400">yoki</span>
                </div>
              </div>

              <GoogleLoginButton />

              <p className="text-xs text-surface-400 text-center mt-6">
                Davom etish orqali siz TenderHelper'ning Maxfiylik Siyosati va Foydalanish Shartlariga rozilik bildirasiz.
              </p>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
