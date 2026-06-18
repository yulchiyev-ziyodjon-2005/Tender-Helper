import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
  fetchGoogleOAuthConfig,
  googleOAuthStartUrl,
} from '../../api/auth';

export default function GoogleLoginButton({ disabled = false }) {
  const { t } = useTranslation();
  const [config, setConfig] = useState({
    isLoading: true,
    enabled: false,
    message: '',
  });

  useEffect(() => {
    let cancelled = false;

    fetchGoogleOAuthConfig()
      .then((data) => {
        if (cancelled) return;
        setConfig({
          isLoading: false,
          enabled: Boolean(data.enabled),
          message: data.message || '',
        });
      })
      .catch(() => {
        if (cancelled) return;
        setConfig({
          isLoading: false,
          enabled: false,
          message: 'Google login holatini tekshirib bolmadi',
        });
      });

    return () => {
      cancelled = true;
    };
  }, []);

  const handleGoogleLogin = () => {
    if (!config.enabled) return;
    window.location.href = googleOAuthStartUrl('/dashboard');
  };

  const isDisabled = disabled || config.isLoading || !config.enabled;

  return (
    <div>
      <button
        type="button"
        onClick={handleGoogleLogin}
        disabled={isDisabled}
        className="w-full flex items-center justify-center gap-3 px-4 py-3 border border-surface-200 dark:border-surface-700 rounded-lg hover:bg-surface-50 dark:hover:bg-surface-800 transition-colors text-surface-700 dark:text-surface-200 font-medium bg-white dark:bg-surface-900 focus:outline-none focus:ring-2 focus:ring-surface-200 dark:focus:ring-surface-700 disabled:opacity-60 disabled:cursor-not-allowed"
      >
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
          <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
          <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.16v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
          <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.16C1.43 8.55 1 10.22 1 12s.43 3.45 1.16 4.93l2.85-2.22.83-.62z" fill="#FBBC05"/>
          <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.16 7.07l3.68 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
        </svg>
        {config.isLoading ? t('actions.loading') : t('auth.google_login')}
      </button>

      {!config.isLoading && !config.enabled && (
        <p className="mt-2 text-xs text-surface-500 dark:text-surface-400 text-center">
          {config.message || 'Google orqali kirish vaqtincha sozlanmoqda'}
        </p>
      )}
    </div>
  );
}
