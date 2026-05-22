/**
 * TenderHelper AI — Login Page
 * ==============================
 * Telefon + OTP va Google OAuth kirish sahifasi.
 * To'liq implementatsiya BOSQICH 2 da.
 */

import { Shield } from 'lucide-react';

export default function LoginPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-surface-50 dark:bg-surface-950 p-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8 fade-in">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-primary-600 mb-4">
            <Shield className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-2xl font-bold text-surface-900 dark:text-white">
            TenderHelper AI
          </h1>
          <p className="text-surface-500 mt-1">
            AI Tender Mentor — tenderda g'olib bo'ling
          </p>
        </div>

        {/* Login Card */}
        <div className="bg-white dark:bg-surface-900 rounded-2xl shadow-card p-8 slide-up">
          <h2 className="text-lg font-semibold text-surface-900 dark:text-white mb-6">
            Kirish
          </h2>

          {/* Phone Number */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-1">
              Telefon raqami
            </label>
            <div className="flex gap-2">
              <span className="flex items-center px-3 bg-surface-100 dark:bg-surface-800 rounded-lg text-sm text-surface-500 font-medium">
                +998
              </span>
              <input
                type="tel"
                placeholder="90 123 45 67"
                className="flex-1 px-4 py-3 bg-surface-50 dark:bg-surface-800 border border-surface-200 dark:border-surface-700 rounded-lg text-surface-900 dark:text-white placeholder-surface-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
                disabled
              />
            </div>
          </div>

          {/* Submit button */}
          <button
            disabled
            className="w-full py-3 px-4 bg-primary-600 hover:bg-primary-700 disabled:opacity-50 text-white font-medium rounded-lg transition-colors"
          >
            SMS kod olish
          </button>

          {/* Divider */}
          <div className="relative my-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-surface-200 dark:border-surface-700"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-3 bg-white dark:bg-surface-900 text-surface-400">
                yoki
              </span>
            </div>
          </div>

          {/* Google Login */}
          <button
            disabled
            className="w-full py-3 px-4 bg-white dark:bg-surface-800 border border-surface-200 dark:border-surface-700 hover:bg-surface-50 dark:hover:bg-surface-700 disabled:opacity-50 text-surface-700 dark:text-surface-300 font-medium rounded-lg transition-colors flex items-center justify-center gap-3"
          >
            <svg className="w-5 h-5" viewBox="0 0 24 24">
              <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z" fill="#4285F4"/>
              <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
              <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
              <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
            </svg>
            Google orqali kirish
          </button>

          {/* Info */}
          <p className="text-xs text-surface-400 text-center mt-6">
            Kirib, siz foydalanish shartlarini qabul qilasiz.
            <br />
            BOSQICH 2 da to'liq implementatsiya qilinadi.
          </p>
        </div>
      </div>
    </div>
  );
}
