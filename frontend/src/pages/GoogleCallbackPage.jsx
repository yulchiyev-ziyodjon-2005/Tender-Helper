import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import useAuthStore from '../store/authStore';

export default function GoogleCallbackPage() {
  const navigate = useNavigate();
  const login = useAuthStore((state) => state.login);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const access = params.get('access');
    const refresh = params.get('refresh');
    const isNewUser = params.get('is_new_user') === '1';
    const next = params.get('next') || '/dashboard';

    if (!access || !refresh) {
      navigate('/login?google_error=Google login tokenlari topilmadi', { replace: true });
      return;
    }

    login({ access, refresh }, null);
    navigate(isNewUser ? '/onboarding' : next, { replace: true });
  }, [login, navigate]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-surface-50 dark:bg-surface-950 px-4">
      <div className="w-full max-w-sm rounded-xl border border-surface-200 dark:border-surface-800 bg-white dark:bg-surface-900 p-6 text-center shadow-card">
        <div className="mx-auto mb-4 h-12 w-12 rounded-full skeleton" />
        <h1 className="text-lg font-semibold text-surface-900 dark:text-white">
          Google orqali kirish yakunlanmoqda
        </h1>
        <p className="mt-2 text-sm text-surface-500">
          Tokenlar tekshirilmoqda, iltimos kuting.
        </p>
      </div>
    </div>
  );
}
