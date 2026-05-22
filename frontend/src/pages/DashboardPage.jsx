import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Shield, Search, BarChart3, Calculator, LogOut, Filter, SlidersHorizontal, MapPin, Calendar, Building2, CheckCircle2 } from 'lucide-react';
import useAuthStore from '../store/authStore';
import ThemeToggle from '../components/ui/ThemeToggle';
import LanguageSwitcher from '../components/ui/LanguageSwitcher';

export default function DashboardPage() {
  const navigate = useNavigate();
  const logout = useAuthStore((state) => state.logout);
  const [searchQuery, setSearchQuery] = useState('');

  const stats = [
    { label: 'Faol tenderlar', value: '1,248', icon: Search, color: 'text-primary-500' },
    { label: 'Tahlillarim', value: '0 / 4', icon: BarChart3, color: 'text-success-500' },
    { label: 'O\'rtacha moslik', value: '85%', icon: Calculator, color: 'text-warning-500' },
  ];

  const handleAnalyze = (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    // Navigate to analysis page with the query
    navigate(`/analysis?q=${encodeURIComponent(searchQuery)}`);
  };

  const mockRecentTenders = [
    { id: '24110012', title: 'Kompyuter texnikalari va server uskunalarini xarid qilish', customer: 'Raqamli Texnologiyalar Vazirligi', price: '1,250,000,000 UZS', deadline: '01.06.2026', platform: 'xarid.uzex.uz', tags: ['IT', 'Uskunalar'] },
    { id: '24110085', title: 'Yangi ofis binosi uchun zamonaviy mebel jihozlari', customer: 'O\'zsanoatqurilishbank ATB', price: '450,000,000 UZS', deadline: '28.05.2026', platform: 'etender.uzex.uz', tags: ['Mebel', 'Korporativ'] },
    { id: '24110103', title: 'Bulutli infratuzilma (Cloud) ijara xizmatlari', customer: 'Elektron Hukumat Markazi', price: '890,000,000 UZS', deadline: '15.06.2026', platform: 'xarid.uzex.uz', tags: ['IT', 'Xizmatlar'] },
  ];

  return (
    <div className="min-h-screen bg-surface-50 dark:bg-surface-950 font-sans transition-colors duration-300">
      {/* Top Navbar */}
      <header className="sticky top-0 z-50 bg-white/80 dark:bg-surface-900/80 backdrop-blur-md border-b border-surface-200 dark:border-surface-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <img src="/logo/logo-cropped.png" alt="Logo" className="h-8 w-auto object-contain hidden sm:block" />
            <span className="font-bold text-xl text-surface-900 dark:text-white">
              TenderHelper <span className="text-primary-600">AI</span>
            </span>
          </div>

          <div className="flex items-center gap-4">
            <ThemeToggle />
            <LanguageSwitcher />
            <span className="hidden sm:inline-flex items-center gap-1 text-sm font-medium text-surface-600 bg-surface-100 dark:bg-surface-800 px-3 py-1.5 rounded-full border border-surface-200 dark:border-surface-700">
              <CheckCircle2 className="w-4 h-4 text-success-500" /> Bepul Tarif
            </span>
            <button
              onClick={() => navigate('/settings')}
              className="p-2 text-surface-500 hover:text-primary-600 rounded-lg hover:bg-surface-100 dark:hover:bg-surface-800 transition-colors"
              title="Sozlamalar"
            >
              <Building2 className="w-5 h-5" />
            </button>
            <button
              onClick={logout}
              className="p-2 text-surface-500 hover:text-danger-500 rounded-lg hover:bg-danger-50 dark:hover:bg-danger-500/10 transition-colors"
              title="Chiqish"
            >
              <LogOut className="w-5 h-5" />
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {/* Main Search Section (Hero-style) */}
        <div className="bg-white dark:bg-surface-900 rounded-3xl p-8 sm:p-12 mb-8 shadow-card border border-surface-200 dark:border-surface-800 text-center relative overflow-hidden">
          {/* Subtle background glow */}
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-2xl h-full bg-primary-500/5 dark:bg-primary-500/10 blur-3xl pointer-events-none rounded-full" />
          
          <div className="relative z-10 max-w-3xl mx-auto">
            <div className="w-16 h-16 bg-primary-100 dark:bg-primary-900/30 rounded-2xl flex items-center justify-center mx-auto mb-6">
              <Search className="w-8 h-8 text-primary-600 dark:text-primary-400" />
            </div>
            <h1 className="text-3xl sm:text-4xl font-extrabold text-surface-900 dark:text-white mb-4">
              Lot raqami, havola yoki nomi
            </h1>
            <p className="text-surface-600 dark:text-surface-400 mb-8 text-lg">
              Tender hujjatlarini Gemini AI orqali yuridik va moliyaviy tahlil qilish uchun qidiring.
            </p>

            <form onSubmit={handleAnalyze} className="relative flex flex-col sm:flex-row gap-3">
              <div className="relative flex-1">
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-6 h-6 text-surface-400" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Masalan: 24110012 yoki https://xarid.uzex.uz/..."
                  className="w-full pl-12 pr-4 py-4 sm:py-5 bg-surface-50 dark:bg-surface-950 border border-surface-200 dark:border-surface-700 rounded-2xl focus:outline-none focus:ring-2 focus:ring-primary-500 text-lg text-surface-900 dark:text-white placeholder:text-surface-400 transition-shadow shadow-inner"
                />
              </div>
              <button
                type="submit"
                disabled={!searchQuery.trim()}
                className="px-8 py-4 sm:py-5 bg-primary-600 hover:bg-primary-700 text-white font-bold text-lg rounded-2xl transition-colors shadow-lg shadow-primary-600/25 hover:shadow-xl hover:-translate-y-0.5 disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap flex items-center justify-center gap-2"
              >
                Tahlil qilish <BarChart3 className="w-5 h-5" />
              </button>
            </form>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 mb-8">
          {stats.map((stat) => (
            <div key={stat.label} className="bg-white dark:bg-surface-900 rounded-2xl p-6 shadow-sm border border-surface-200 dark:border-surface-800 flex items-center gap-4">
              <div className={`p-3 rounded-xl bg-surface-100 dark:bg-surface-800 ${stat.color}`}>
                <stat.icon className="w-6 h-6" />
              </div>
              <div>
                <p className="text-sm font-medium text-surface-500 dark:text-surface-400">{stat.label}</p>
                <p className="text-2xl font-bold text-surface-900 dark:text-white tabular-nums">
                  {stat.value}
                </p>
              </div>
            </div>
          ))}
        </div>

        {/* Content Layout: Filters + Recent */}
        <div className="flex flex-col lg:flex-row gap-8">
          
          {/* Sidebar Filters */}
          <aside className="w-full lg:w-72 flex-shrink-0">
            <div className="bg-white dark:bg-surface-900 rounded-2xl p-6 shadow-sm border border-surface-200 dark:border-surface-800 sticky top-24">
              <div className="flex items-center gap-2 mb-6 pb-4 border-b border-surface-200 dark:border-surface-800">
                <SlidersHorizontal className="w-5 h-5 text-surface-500" />
                <h3 className="text-lg font-bold text-surface-900 dark:text-white">Filtrlar</h3>
              </div>
              
              <div className="space-y-6">
                <div>
                  <label className="text-sm font-semibold text-surface-700 dark:text-surface-300 mb-3 block">Platforma</label>
                  <div className="space-y-2">
                    {['Barchasi', 'xarid.uzex.uz', 'etender.uzex.uz', 'Kooperatsiya'].map(platform => (
                      <label key={platform} className="flex items-center gap-3 cursor-pointer group">
                        <input type="radio" name="platform" defaultChecked={platform === 'Barchasi'} className="w-4 h-4 text-primary-600 border-surface-300 focus:ring-primary-600 bg-surface-50 dark:bg-surface-800 dark:border-surface-600" />
                        <span className="text-sm text-surface-600 dark:text-surface-400 group-hover:text-surface-900 dark:group-hover:text-white transition-colors">{platform}</span>
                      </label>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="text-sm font-semibold text-surface-700 dark:text-surface-300 mb-3 block">Boshlang'ich Narx</label>
                  <div className="flex items-center gap-2">
                    <input type="number" placeholder="Dan" className="w-full px-3 py-2 text-sm bg-surface-50 dark:bg-surface-950 border border-surface-200 dark:border-surface-700 rounded-lg focus:outline-none focus:ring-1 focus:ring-primary-500" />
                    <span className="text-surface-400">-</span>
                    <input type="number" placeholder="Gacha" className="w-full px-3 py-2 text-sm bg-surface-50 dark:bg-surface-950 border border-surface-200 dark:border-surface-700 rounded-lg focus:outline-none focus:ring-1 focus:ring-primary-500" />
                  </div>
                </div>

                <div>
                  <label className="text-sm font-semibold text-surface-700 dark:text-surface-300 mb-3 block">Soha / Kategoriya</label>
                  <select className="w-full px-3 py-2 text-sm bg-surface-50 dark:bg-surface-950 border border-surface-200 dark:border-surface-700 rounded-lg focus:outline-none focus:ring-1 focus:ring-primary-500 text-surface-700 dark:text-surface-300">
                    <option>Barcha sohalar</option>
                    <option>IT va Dasturlash</option>
                    <option>Qurilish va ta'mirlash</option>
                    <option>Mebel va ofis jihozlari</option>
                  </select>
                </div>
                
                <button className="w-full py-2.5 bg-surface-100 hover:bg-surface-200 dark:bg-surface-800 dark:hover:bg-surface-700 text-surface-700 dark:text-surface-200 text-sm font-semibold rounded-lg transition-colors">
                  Filtrni qo'llash
                </button>
              </div>
            </div>
          </aside>

          {/* Main List */}
          <div className="flex-1">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-surface-900 dark:text-white">Tavsiya etilgan tenderlar</h2>
              <button className="text-sm font-medium text-primary-600 dark:text-primary-400 hover:underline">Barchasini ko'rish</button>
            </div>

            <div className="space-y-4">
              {mockRecentTenders.map(tender => (
                <div key={tender.id} className="bg-white dark:bg-surface-900 rounded-2xl p-6 shadow-sm border border-surface-200 dark:border-surface-800 hover:shadow-md transition-shadow group cursor-pointer" onClick={() => navigate(`/analysis?q=${tender.id}`)}>
                  <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <span className="px-2.5 py-1 text-xs font-bold text-primary-700 dark:text-primary-300 bg-primary-100 dark:bg-primary-900/40 rounded-md border border-primary-200 dark:border-primary-800">
                          Lot: #{tender.id}
                        </span>
                        <span className="px-2.5 py-1 text-xs font-medium text-surface-600 dark:text-surface-400 bg-surface-100 dark:bg-surface-800 rounded-md">
                          {tender.platform}
                        </span>
                      </div>
                      <h3 className="text-lg font-bold text-surface-900 dark:text-white mb-2 group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors">
                        {tender.title}
                      </h3>
                      <div className="flex items-center gap-2 text-sm text-surface-500 dark:text-surface-400 mb-4">
                        <Building2 className="w-4 h-4 flex-shrink-0" />
                        <span>{tender.customer}</span>
                      </div>
                      <div className="flex flex-wrap gap-2">
                        {tender.tags.map(tag => (
                          <span key={tag} className="px-2 py-1 text-xs font-medium text-surface-600 dark:text-surface-300 bg-surface-50 dark:bg-surface-800 rounded border border-surface-200 dark:border-surface-700">
                            {tag}
                          </span>
                        ))}
                      </div>
                    </div>

                    <div className="flex flex-col md:items-end justify-between md:h-full gap-4 md:gap-0 mt-4 md:mt-0 pt-4 md:pt-0 border-t md:border-t-0 border-surface-200 dark:border-surface-800">
                      <div className="text-left md:text-right">
                        <p className="text-xs text-surface-500 dark:text-surface-400 mb-1">Boshlang'ich narx</p>
                        <p className="text-xl font-black text-surface-900 dark:text-white tabular-nums">
                          {tender.price}
                        </p>
                      </div>
                      <div className="flex items-center justify-between md:justify-end gap-6 w-full">
                        <div className="flex items-center gap-1.5 text-sm text-danger-600 dark:text-danger-400 font-medium">
                          <Calendar className="w-4 h-4" />
                          {tender.deadline}
                        </div>
                        <button className="px-4 py-2 bg-surface-100 dark:bg-surface-800 hover:bg-primary-50 dark:hover:bg-primary-900/30 text-surface-700 dark:text-white hover:text-primary-600 dark:hover:text-primary-400 text-sm font-semibold rounded-lg transition-colors border border-surface-200 dark:border-surface-700 hover:border-primary-300 dark:hover:border-primary-700">
                          Tahlil qilish
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>

          </div>
        </div>
      </main>
    </div>
  );
}
