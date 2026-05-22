import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, BarChart3, Calculator, LogOut, SlidersHorizontal, Calendar, Building2, CheckCircle2, Loader2, AlertCircle, Settings } from 'lucide-react';
import useAuthStore from '../store/authStore';
import ThemeToggle from '../components/ui/ThemeToggle';
import LanguageSwitcher from '../components/ui/LanguageSwitcher';
import apiClient from '../api/client';

export default function DashboardPage() {
  const navigate = useNavigate();
  const logout = useAuthStore((state) => state.logout);
  const [searchQuery, setSearchQuery] = useState('');
  
  // Real API state
  const [tenders, setTenders] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedPlatform, setSelectedPlatform] = useState('');
  const [priceMin, setPriceMin] = useState('');
  const [priceMax, setPriceMax] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');

  // Tenderlarni backenddan yuklash
  const fetchTenders = async (params = {}) => {
    setIsLoading(true);
    setError(null);
    try {
      const queryParams = new URLSearchParams();
      if (params.search) queryParams.set('search', params.search);
      if (params.platform_source) queryParams.set('platform_source', params.platform_source);
      if (params.start_price_min) queryParams.set('start_price_min', params.start_price_min);
      if (params.start_price_max) queryParams.set('start_price_max', params.start_price_max);
      if (params.category) queryParams.set('category', params.category);
      
      const url = `/tenders/?${queryParams.toString()}`;
      const { data } = await apiClient.get(url);
      // DRF returns paginated or list
      setTenders(Array.isArray(data) ? data : (data.results || []));
    } catch (err) {
      console.error('Tenders fetch error:', err);
      setError('Tenderlarni yuklashda xatolik yuz berdi');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchTenders();
  }, []);

  const handleAnalyze = (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    navigate(`/analysis?q=${encodeURIComponent(searchQuery)}`);
  };

  const handleFilterApply = () => {
    fetchTenders({
      platform_source: selectedPlatform,
      start_price_min: priceMin,
      start_price_max: priceMax,
      category: selectedCategory,
    });
  };

  const handleTenderClick = (tender) => {
    navigate(`/analysis?lotId=${tender.id}&lotNumber=${tender.lot_number}`);
  };

  const formatMoney = (amount) => {
    return new Intl.NumberFormat('uz-UZ').format(amount) + ' UZS';
  };

  const formatDate = (dateStr) => {
    return new Date(dateStr).toLocaleDateString('uz-UZ', { day: '2-digit', month: '2-digit', year: 'numeric' });
  };

  const getPlatformLabel = (source) => {
    const map = {
      'xarid_uzex': 'xarid.uzex.uz',
      'dxarid_uzex': 'dxarid.uzex.uz',
      'exarid_uzex': 'exarid.uzex.uz',
      'e_auksion': 'e-auksion.uz',
      'manual': "Qo'lda kiritilgan",
    };
    return map[source] || source;
  };

  const getDaysLeft = (deadline) => {
    const days = Math.ceil((new Date(deadline) - new Date()) / (1000 * 60 * 60 * 24));
    return days;
  };

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
              <Settings className="w-5 h-5" />
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
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-2xl h-full bg-primary-500/5 dark:bg-primary-500/10 blur-3xl pointer-events-none rounded-full" />
          
          <div className="relative z-10 max-w-3xl mx-auto">
            <div className="w-16 h-16 bg-primary-100 dark:bg-primary-900/30 rounded-2xl flex items-center justify-center mx-auto mb-6">
              <Search className="w-8 h-8 text-primary-600 dark:text-primary-400" />
            </div>
            <h1 className="text-3xl sm:text-4xl font-extrabold text-surface-900 dark:text-white mb-4">
              Lot raqami, havola yoki nomi
            </h1>
            <p className="text-surface-600 dark:text-surface-400 mb-8 text-lg">
              Tender hujjatlarini AI orqali yuridik va moliyaviy tahlil qilish uchun qidiring.
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
          {[
            { label: 'Faol tenderlar', value: isLoading ? '...' : tenders.length.toLocaleString(), icon: Search, color: 'text-primary-500' },
            { label: 'Tahlillarim', value: '0 / 4', icon: BarChart3, color: 'text-success-500' },
            { label: 'O\'rtacha moslik', value: '—', icon: Calculator, color: 'text-warning-500' },
          ].map((stat) => (
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
                    {[
                      { value: '', label: 'Barchasi' },
                      { value: 'xarid_uzex', label: 'xarid.uzex.uz' },
                      { value: 'dxarid_uzex', label: 'dxarid.uzex.uz' },
                      { value: 'exarid_uzex', label: 'exarid.uzex.uz' },
                    ].map(platform => (
                      <label key={platform.label} className="flex items-center gap-3 cursor-pointer group">
                        <input 
                          type="radio" 
                          name="platform" 
                          checked={selectedPlatform === platform.value}
                          onChange={() => setSelectedPlatform(platform.value)} 
                          className="w-4 h-4 text-primary-600 border-surface-300 focus:ring-primary-600 bg-surface-50 dark:bg-surface-800 dark:border-surface-600" 
                        />
                        <span className="text-sm text-surface-600 dark:text-surface-400 group-hover:text-surface-900 dark:group-hover:text-white transition-colors">{platform.label}</span>
                      </label>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="text-sm font-semibold text-surface-700 dark:text-surface-300 mb-3 block">Boshlang'ich Narx</label>
                  <div className="flex items-center gap-2">
                    <input type="number" placeholder="Dan" value={priceMin} onChange={e => setPriceMin(e.target.value)} className="w-full px-3 py-2 text-sm bg-surface-50 dark:bg-surface-950 border border-surface-200 dark:border-surface-700 rounded-lg focus:outline-none focus:ring-1 focus:ring-primary-500" />
                    <span className="text-surface-400">-</span>
                    <input type="number" placeholder="Gacha" value={priceMax} onChange={e => setPriceMax(e.target.value)} className="w-full px-3 py-2 text-sm bg-surface-50 dark:bg-surface-950 border border-surface-200 dark:border-surface-700 rounded-lg focus:outline-none focus:ring-1 focus:ring-primary-500" />
                  </div>
                </div>

                <div>
                  <label className="text-sm font-semibold text-surface-700 dark:text-surface-300 mb-3 block">Soha / Kategoriya</label>
                  <select value={selectedCategory} onChange={e => setSelectedCategory(e.target.value)} className="w-full px-3 py-2 text-sm bg-surface-50 dark:bg-surface-950 border border-surface-200 dark:border-surface-700 rounded-lg focus:outline-none focus:ring-1 focus:ring-primary-500 text-surface-700 dark:text-surface-300">
                    <option value="">Barcha sohalar</option>
                    <option value="IT uskunalar">IT va Dasturlash</option>
                    <option value="Qurilish">Qurilish va ta'mirlash</option>
                    <option value="Mebel">Mebel va ofis jihozlari</option>
                    <option value="Tibbiyot">Tibbiyot</option>
                    <option value="Transport">Transport</option>
                  </select>
                </div>
                
                <button 
                  onClick={handleFilterApply}
                  className="w-full py-2.5 bg-primary-600 hover:bg-primary-700 text-white text-sm font-semibold rounded-lg transition-colors"
                >
                  Filtrni qo'llash
                </button>
              </div>
            </div>
          </aside>

          {/* Main List */}
          <div className="flex-1">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-surface-900 dark:text-white">Faol Tenderlar</h2>
              <span className="text-sm text-surface-500">{tenders.length} ta natija</span>
            </div>

            {isLoading && (
              <div className="bg-white dark:bg-surface-900 rounded-2xl p-12 shadow-sm border border-surface-200 dark:border-surface-800 flex flex-col items-center justify-center">
                <Loader2 className="w-10 h-10 text-primary-500 animate-spin mb-4" />
                <p className="text-surface-500 font-medium">Tenderlar yuklanmoqda...</p>
              </div>
            )}

            {error && (
              <div className="bg-danger-50 dark:bg-danger-900/20 border border-danger-200 dark:border-danger-800 rounded-2xl p-6 flex items-center gap-4">
                <AlertCircle className="w-6 h-6 text-danger-500 flex-shrink-0" />
                <div>
                  <p className="text-danger-700 dark:text-danger-300 font-semibold">{error}</p>
                  <button onClick={() => fetchTenders()} className="text-sm text-danger-600 underline mt-1">Qaytadan urinib ko'rish</button>
                </div>
              </div>
            )}

            {!isLoading && !error && tenders.length === 0 && (
              <div className="bg-white dark:bg-surface-900 rounded-2xl p-12 shadow-sm border border-surface-200 dark:border-surface-800 text-center">
                <Search className="w-12 h-12 text-surface-300 mx-auto mb-4" />
                <p className="text-surface-500 font-medium">Hozircha tenderlar topilmadi</p>
                <p className="text-surface-400 text-sm mt-1">Scraper seed_tenders buyrug'ini ishga tushiring</p>
              </div>
            )}

            <div className="space-y-4">
              {tenders.map(tender => {
                const daysLeft = getDaysLeft(tender.deadline);
                return (
                <div key={tender.id} className="bg-white dark:bg-surface-900 rounded-2xl p-6 shadow-sm border border-surface-200 dark:border-surface-800 hover:shadow-md transition-shadow group cursor-pointer" onClick={() => handleTenderClick(tender)}>
                  <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2 flex-wrap">
                        <span className="px-2.5 py-1 text-xs font-bold text-primary-700 dark:text-primary-300 bg-primary-100 dark:bg-primary-900/40 rounded-md border border-primary-200 dark:border-primary-800">
                          Lot: #{tender.lot_number}
                        </span>
                        <span className="px-2.5 py-1 text-xs font-medium text-surface-600 dark:text-surface-400 bg-surface-100 dark:bg-surface-800 rounded-md">
                          {getPlatformLabel(tender.platform_source)}
                        </span>
                        {tender.category && (
                          <span className="px-2 py-1 text-xs font-medium text-surface-600 dark:text-surface-300 bg-surface-50 dark:bg-surface-800 rounded border border-surface-200 dark:border-surface-700">
                            {tender.category}
                          </span>
                        )}
                      </div>
                      <h3 className="text-lg font-bold text-surface-900 dark:text-white mb-2 group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors">
                        {tender.title}
                      </h3>
                      <div className="flex items-center gap-2 text-sm text-surface-500 dark:text-surface-400">
                        <Building2 className="w-4 h-4 flex-shrink-0" />
                        <span>{tender.buyer_name || 'Buyurtmachi nomi ko\'rsatilmagan'}</span>
                      </div>
                    </div>

                    <div className="flex flex-col md:items-end justify-between md:h-full gap-4 md:gap-0 mt-4 md:mt-0 pt-4 md:pt-0 border-t md:border-t-0 border-surface-200 dark:border-surface-800">
                      <div className="text-left md:text-right">
                        <p className="text-xs text-surface-500 dark:text-surface-400 mb-1">Boshlang'ich narx</p>
                        <p className="text-xl font-black text-surface-900 dark:text-white tabular-nums">
                          {formatMoney(tender.start_price)}
                        </p>
                      </div>
                      <div className="flex items-center justify-between md:justify-end gap-6 w-full mt-3">
                        <div className={`flex items-center gap-1.5 text-sm font-medium ${daysLeft <= 5 ? 'text-danger-600 dark:text-danger-400' : 'text-warning-600 dark:text-warning-400'}`}>
                          <Calendar className="w-4 h-4" />
                          {daysLeft > 0 ? `${daysLeft} kun qoldi` : 'Muddati o\'tgan'}
                        </div>
                        <button className="px-4 py-2 bg-surface-100 dark:bg-surface-800 hover:bg-primary-50 dark:hover:bg-primary-900/30 text-surface-700 dark:text-white hover:text-primary-600 dark:hover:text-primary-400 text-sm font-semibold rounded-lg transition-colors border border-surface-200 dark:border-surface-700 hover:border-primary-300 dark:hover:border-primary-700">
                          Tahlil qilish
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              )})}
            </div>

          </div>
        </div>
      </main>
    </div>
  );
}
