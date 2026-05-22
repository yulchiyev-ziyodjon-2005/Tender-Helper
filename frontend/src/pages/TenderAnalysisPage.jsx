import { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Loader2, AlertTriangle, ExternalLink } from 'lucide-react';
import AITenderDashboard from '../components/analysis/AITenderDashboard';
import SmartCalculator from '../components/analysis/SmartCalculator';

export default function TenderAnalysisPage() {
  const [searchParams] = useSearchParams();
  const query = searchParams.get('q');
  const navigate = useNavigate();

  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [analysisData, setAnalysisData] = useState(null);

  useEffect(() => {
    if (!query) {
      navigate('/dashboard');
      return;
    }

    // Har qanday so'rov bo'lganda mock data qaytarishni simulyatsiya qilamiz
    const fetchAnalysis = async () => {
      setIsLoading(true);
      setError(null);
      
      try {
        // API chaqiruvini simulyatsiya qilish (1.5 soniya)
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        // Mock data
        setAnalysisData({
          lotId: query.replace(/[^0-9]/g, '') || '24110012',
          title: "Kompyuter texnikalari va server uskunalarini xarid qilish",
          customer: "O'zbekiston Respublikasi Raqamli Texnologiyalar Vazirligi",
          deadline: "2026-06-01",
          startPrice: 1250000000,
          currency: 'UZS',
          platform: "xarid.uzex.uz",
          aiMatchScore: 85,
          redFlags: [
            { id: 1, title: 'Yetkazib berish muddati', description: 'Yetkazib berish muddati atigi 5 ish kuni qilib belgilangan. Bu server uskunalari importi uchun juda xavfli.', level: 'high' },
            { id: 2, title: 'Jarima (Penya)', description: 'Kechikish uchun kunlik penya 0.5% (qonunchilikda odatda 0.4% bo\'ladi).', level: 'high' },
            { id: 3, title: 'To\'lov sharti', description: 'Oldindan to\'lov 15%, qolgan 85% ish tugagandan so\'ng. Aylanma mablag\'ingiz yetarliligiga ishonch hosil qiling.', level: 'medium' }
          ],
          requirements: [
            "Barcha kompyuterlar kamida Core i7 13-avlod, 16GB RAM bo'lishi shart.",
            "Server uskunalari xalqaro sifat sertifikatlariga ega bo'lishi kerak.",
            "Kafolat muddati kamida 3 yil etib belgilanishi zarur."
          ]
        });
      } catch (err) {
        setError('Tahlil ma\'lumotlarini olishda xatolik yuz berdi.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchAnalysis();
  }, [query, navigate]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-surface-50 dark:bg-surface-950 flex flex-col items-center justify-center p-4">
        <Loader2 className="w-12 h-12 text-primary-500 animate-spin mb-4" />
        <h2 className="text-xl font-bold text-surface-900 dark:text-white mb-2">AI hujjatlarni tahlil qilmoqda...</h2>
        <p className="text-surface-500 text-center max-w-md">Gemini AI tizimi {query} bo'yicha texnik topshiriqlarni va yashirin shartlarni izlamoqda.</p>
      </div>
    );
  }

  if (error || !analysisData) {
    return (
      <div className="min-h-screen bg-surface-50 dark:bg-surface-950 flex flex-col items-center justify-center p-4">
        <AlertTriangle className="w-12 h-12 text-danger-500 mb-4" />
        <h2 className="text-xl font-bold text-surface-900 dark:text-white mb-4">{error || "Ma'lumot topilmadi"}</h2>
        <button onClick={() => navigate('/dashboard')} className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700">
          Orqaga qaytish
        </button>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-surface-50 dark:bg-surface-950 pb-12">
      {/* Header */}
      <header className="bg-white dark:bg-surface-900 border-b border-surface-200 dark:border-surface-800 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button 
              onClick={() => navigate('/dashboard')}
              className="p-2 -ml-2 text-surface-500 hover:text-surface-900 dark:hover:text-white hover:bg-surface-100 dark:hover:bg-surface-800 rounded-lg transition-colors"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
            <div className="flex flex-col">
              <span className="text-sm font-medium text-surface-500 dark:text-surface-400">Lot: #{analysisData.lotId}</span>
              <h1 className="text-base font-bold text-surface-900 dark:text-white truncate max-w-md md:max-w-xl">
                {analysisData.title}
              </h1>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <a 
              href={`https://${analysisData.platform}/purchase/competition/detail/${analysisData.lotId}`}
              target="_blank" rel="noopener noreferrer"
              className="hidden sm:inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-primary-600 bg-primary-50 dark:bg-primary-900/30 rounded-lg hover:bg-primary-100 transition-colors"
            >
              Manbaga o'tish <ExternalLink className="w-4 h-4" />
            </a>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Left Column: AI Analysis */}
          <div className="lg:col-span-2 space-y-8">
            <AITenderDashboard data={analysisData} />
          </div>

          {/* Right Column: Smart Calculator */}
          <div className="lg:col-span-1">
            <div className="sticky top-24">
              <SmartCalculator tenderPrice={analysisData.startPrice} />
            </div>
          </div>

        </div>
      </main>
    </div>
  );
}
