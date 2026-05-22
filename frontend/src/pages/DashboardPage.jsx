/**
 * TenderHelper AI — Dashboard Page
 * ==================================
 * Asosiy boshqaruv paneli.
 * To'liq implementatsiya BOSQICH 4 da.
 */

import { Shield, Search, BarChart3, Calculator, LogOut } from 'lucide-react';
import useAuthStore from '../store/authStore';

export default function DashboardPage() {
  const logout = useAuthStore((state) => state.logout);

  const stats = [
    { label: 'Faol tenderlar', value: '—', icon: Search, color: 'text-primary-500' },
    { label: 'Tahlillarim', value: '0 / 4', icon: BarChart3, color: 'text-success-500' },
    { label: 'O\'rtacha moslik', value: '—', icon: Calculator, color: 'text-warning-500' },
  ];

  return (
    <div className="min-h-screen bg-surface-50 dark:bg-surface-950">
      {/* Top Navbar */}
      <header className="sticky top-0 z-50 bg-white dark:bg-surface-900 border-b border-surface-200 dark:border-surface-800 glass">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-primary-600 flex items-center justify-center">
              <Shield className="w-5 h-5 text-white" />
            </div>
            <span className="font-bold text-lg text-surface-900 dark:text-white">
              TenderHelper
            </span>
          </div>

          <div className="flex items-center gap-3">
            <span className="hidden sm:inline text-sm text-surface-500 bg-surface-100 dark:bg-surface-800 px-3 py-1 rounded-full">
              Bepul tarif
            </span>
            <button
              onClick={logout}
              className="p-2 text-surface-400 hover:text-danger-500 rounded-lg hover:bg-surface-100 dark:hover:bg-surface-800 transition-colors"
              title="Chiqish"
            >
              <LogOut className="w-5 h-5" />
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome */}
        <div className="mb-8 fade-in">
          <h1 className="text-2xl font-bold text-surface-900 dark:text-white">
            Xush kelibsiz! 👋
          </h1>
          <p className="text-surface-500 mt-1">
            TenderHelper AI — sizning tender mentoring
          </p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
          {stats.map((stat) => (
            <div
              key={stat.label}
              className="bg-white dark:bg-surface-900 rounded-xl p-5 shadow-card slide-up"
            >
              <div className="flex items-center gap-3">
                <div className={`p-2 rounded-lg bg-surface-100 dark:bg-surface-800 ${stat.color}`}>
                  <stat.icon className="w-5 h-5" />
                </div>
                <div>
                  <p className="text-sm text-surface-500">{stat.label}</p>
                  <p className="text-xl font-bold text-surface-900 dark:text-white tabular-nums">
                    {stat.value}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Placeholder Content */}
        <div className="bg-white dark:bg-surface-900 rounded-xl p-8 shadow-card text-center slide-up">
          <div className="w-16 h-16 rounded-2xl bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center mx-auto mb-4">
            <Search className="w-8 h-8 text-primary-500" />
          </div>
          <h2 className="text-lg font-semibold text-surface-900 dark:text-white mb-2">
            Tenderlarni qidiring
          </h2>
          <p className="text-surface-500 max-w-md mx-auto">
            Tender lotlari va qidiruv tizimi BOSQICH 4 da ishga tushadi.
            Hozircha infratuzilma tayyor — API 200 qaytarmoqda.
          </p>
          <div className="mt-4 inline-flex items-center gap-2 text-sm text-success-500 bg-success-50 dark:bg-success-500/10 px-4 py-2 rounded-full">
            <div className="w-2 h-2 rounded-full bg-success-500 animate-pulse"></div>
            API Status: OK
          </div>
        </div>
      </main>
    </div>
  );
}
