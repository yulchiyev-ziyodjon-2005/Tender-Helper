import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { exchangeGoogleOAuthCode } from '../api/auth';
import useAuthStore from '../store/authStore';

export default function GoogleCallbackPage() {
  const navigate = useNavigate();
  const login = useAuthStore((state) => state.login);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const code = params.get('code');

    if (!code) {
      navigate('/login?google_error=Google login kodi topilmadi', { replace: true });
      return;
    }

    let active = true;
    exchangeGoogleOAuthCode(code)
      .then((data) => {
        if (!active) return;
        login(data.tokens, data.user, {
          requiresPasswordChange: data.force_password_change,
        });
        navigate(
          data.force_password_change
            ? '/change-password'
            : data.is_new_user
              ? '/onboarding'
              : (data.next || '/dashboard'),
          { replace: true },
        );
      })
      .catch(() => {
        if (active) {
          navigate('/login?google_error=Google login kodi yaroqsiz yoki muddati tugagan', { replace: true });
        }
      });

    return () => {
      active = false;
    };
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
