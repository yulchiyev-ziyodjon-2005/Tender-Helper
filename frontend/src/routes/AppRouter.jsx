/**
 * TenderHelper AI — App Router
 * ===============================
 * Markaziy routing konfiguratsiyasi.
 */

import { lazy, Suspense, useEffect } from 'react';
import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
  useLocation,
} from 'react-router-dom';
import useAuthStore from '../store/authStore';

// Route-level splitting keeps the public landing and privileged console isolated.
const LandingPage = lazy(() => import('../pages/LandingPage'));
const LoginPage = lazy(() => import('../pages/LoginPage'));
const RegisterPage = lazy(() => import('../pages/RegisterPage'));
const DashboardPage = lazy(() => import('../pages/DashboardPage'));
const OnboardingPage = lazy(() => import('../pages/OnboardingPage'));
const NotFoundPage = lazy(() => import('../pages/NotFoundPage'));
const GoogleCallbackPage = lazy(() => import('../pages/GoogleCallbackPage'));
const TenderAnalysisPage = lazy(() => import('../pages/TenderAnalysisPage'));
const SettingsPage = lazy(() => import('../pages/SettingsPage'));
const SuperadminPage = lazy(() => import('../pages/SuperadminPage'));
const PrivacyPage = lazy(() => import('../pages/PrivacyPage'));
const TermsPage = lazy(() => import('../pages/TermsPage'));
const TeamWorkspacePage = lazy(() => import('../pages/TeamWorkspacePage'));
const ChangePasswordPage = lazy(() => import('../pages/ChangePasswordPage'));
const ForgotPasswordPage = lazy(() => import('../pages/ForgotPasswordPage'));
const ResetPasswordPage = lazy(() => import('../pages/ResetPasswordPage'));

function RouteFallback() {
  return (
    <div className="grid min-h-screen place-items-center bg-slate-50 dark:bg-slate-950">
      <div className="text-center">
        <span className="mx-auto block h-8 w-8 animate-spin rounded-full border-2 border-slate-200 border-t-blue-600 dark:border-slate-800 dark:border-t-cyan-300" />
        <p className="mt-3 text-xs font-bold text-slate-500">Ish maydoni yuklanmoqda...</p>
      </div>
    </div>
  );
}

function ScrollToTop() {
  const { pathname } = useLocation();

  useEffect(() => {
    window.scrollTo({ top: 0, left: 0, behavior: 'auto' });
  }, [pathname]);

  return null;
}

/**
 * Himoyalangan yo'nalish — faqat autentifikatsiya qilingan foydalanuvchilar
 */
function PrivateRoute({ children, allowPasswordChange = false }) {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const requiresPasswordChange = useAuthStore((state) => state.requiresPasswordChange);
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  if (requiresPasswordChange && !allowPasswordChange) {
    return <Navigate to="/change-password" replace />;
  }
  return children;
}

/**
 * Ochiq yo'nalish — faqat autentifikatsiya qilinmaganlar
 */
function PublicRoute({ children }) {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const requiresPasswordChange = useAuthStore((state) => state.requiresPasswordChange);
  return !isAuthenticated
    ? children
    : <Navigate to={requiresPasswordChange ? '/change-password' : '/dashboard'} replace />;
}

export default function AppRouter() {
  return (
    <BrowserRouter>
      <ScrollToTop />
      <Suspense fallback={<RouteFallback />}>
        <Routes>
        {/* Landing Page - Har doim ochiq, lekin auth bo'lsa dashboardga yo'naltirish ixtiyoriy. Hozircha hamma uchun ochiq. */}
        <Route path="/" element={<LandingPage />} />

        {/* Public Routes */}
        <Route
          path="/login"
          element={
            <PublicRoute>
              <LoginPage />
            </PublicRoute>
          }
        />

        <Route
          path="/register"
          element={
            <PublicRoute>
              <RegisterPage />
            </PublicRoute>
          }
        />
        <Route
          path="/forgot-password"
          element={
            <PublicRoute>
              <ForgotPasswordPage />
            </PublicRoute>
          }
        />
        <Route
          path="/reset-password"
          element={
            <PublicRoute>
              <ResetPasswordPage />
            </PublicRoute>
          }
        />

        <Route path="/auth/google/callback" element={<GoogleCallbackPage />} />
        <Route path="/terms" element={<TermsPage />} />
        <Route path="/privacy" element={<PrivacyPage />} />
        <Route
          path="/change-password"
          element={
            <PrivateRoute allowPasswordChange>
              <ChangePasswordPage />
            </PrivateRoute>
          }
        />

        {/* Private Routes */}
        <Route
          path="/dashboard"
          element={
            <PrivateRoute>
              <DashboardPage />
            </PrivateRoute>
          }
        />

        <Route
          path="/analysis"
          element={
            <PrivateRoute>
              <TenderAnalysisPage />
            </PrivateRoute>
          }
        />

        <Route
          path="/settings"
          element={
            <PrivateRoute>
              <SettingsPage />
            </PrivateRoute>
          }
        />
        
        <Route
          path="/onboarding"
          element={
            <PrivateRoute>
              <OnboardingPage />
            </PrivateRoute>
          }
        />

        <Route
          path="/superadmin"
          element={
            <PrivateRoute>
              <SuperadminPage />
            </PrivateRoute>
          }
        />
        <Route
          path="/team"
          element={
            <PrivateRoute>
              <TeamWorkspacePage />
            </PrivateRoute>
          }
        />

        {/* 404 */}
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  );
}
