/**
 * TenderHelper AI — App Router
 * ===============================
 * Markaziy routing konfiguratsiyasi.
 */

import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import useAuthStore from '../store/authStore';

// Pages (placeholder - to'liq sahifalar 2-bosqichdan boshlab yaratiladi)
import LandingPage from '../pages/LandingPage';
import LoginPage from '../pages/LoginPage';
import DashboardPage from '../pages/DashboardPage';
import OnboardingPage from '../pages/OnboardingPage';
import NotFoundPage from '../pages/NotFoundPage';
import GoogleCallbackPage from '../pages/GoogleCallbackPage';
import TenderAnalysisPage from '../pages/TenderAnalysisPage';

/**
 * Himoyalangan yo'nalish — faqat autentifikatsiya qilingan foydalanuvchilar
 */
function PrivateRoute({ children }) {
  return children; // Temporarily allow access without auth
  // const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  // return isAuthenticated ? children : <Navigate to="/login" replace />;
}

/**
 * Ochiq yo'nalish — faqat autentifikatsiya qilinmaganlar
 */
function PublicRoute({ children }) {
  return children; // Temporarily allow access without auth
  // const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  // return !isAuthenticated ? children : <Navigate to="/dashboard" replace />;
}

export default function AppRouter() {
  return (
    <BrowserRouter>
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

        <Route path="/auth/google/callback" element={<GoogleCallbackPage />} />

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
          path="/onboarding"
          element={
            <PrivateRoute>
              <OnboardingPage />
            </PrivateRoute>
          }
        />

        {/* 404 */}
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </BrowserRouter>
  );
}
