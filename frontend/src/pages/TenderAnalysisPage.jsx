import { useCallback, useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Loader2, AlertTriangle, ExternalLink, RotateCw } from 'lucide-react';
import AITenderDashboard from '../components/analysis/AITenderDashboard';
import SmartCalculator from '../components/analysis/SmartCalculator';
import {
  fetchAnalysisHistory,
  fetchAnalysisResult,
  fetchAnalysisStatus,
  startAnalysis,
} from '../api/analysis';
import { apiEndpoints } from '../api/endpoints';
import { fetchTenderById, fetchTenders } from '../api/tenders';

export default function TenderAnalysisPage() {
  const [searchParams] = useSearchParams();
  const lotId = searchParams.get('lotId');     // UUID of the tender
  const lotNumber = searchParams.get('lotNumber'); // lot_number string  
  const freeQuery = searchParams.get('q');     // free text search from search bar
  const navigate = useNavigate();

  const [isLoading, setIsLoading] = useState(true);
  const [analysisPhase, setAnalysisPhase] = useState('');
  const [error, setError] = useState(null);
  const [analysisData, setAnalysisData] = useState(null);
  const [tenderData, setTenderData] = useState(null);
  const [loadingProgress, setLoadingProgress] = useState(0);

  const runAnalysis = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    setLoadingProgress(0);
    
    try {
      let tender = null;

      // Step 1: Find the tender
      if (lotId) {
        // Direct UUID lookup
        setAnalysisPhase('Tender ma\'lumotlari yuklanmoqda...');
        tender = await fetchTenderById(lotId);
      } else {
        // Search by lot_number or free text
        const searchTerm = lotNumber || freeQuery;
        setAnalysisPhase(`"${searchTerm}" qidirilmoqda...`);
        const { results } = await fetchTenders({ search: searchTerm });
        
        if (results.length === 0) {
          setError(`"${searchTerm}" bo'yicha tender topilmadi. Avval bazaga tender qo'shing.`);
          setIsLoading(false);
          return;
        }
        tender = results[0];
      }

      setTenderData(tender);

      // Step 2: Reuse an existing analysis before consuming a new quota unit.
      const reusableAnalysis = await findReusableAnalysis(tender.id);
      if (reusableAnalysis) {
        if (reusableAnalysis.analysis_status === 'completed') {
          setAnalysisPhase('Oldingi AI tahlil natijasi ochilmoqda...');
          setAnalysisData(reusableAnalysis);
          setLoadingProgress(100);
          return;
        }

        setAnalysisPhase('Mavjud AI tahlil jarayoni tekshirilmoqda...');
        const analysis = await pollAnalysisRun({
          id: reusableAnalysis.id,
          status_url: apiEndpoints.analysis.status(reusableAnalysis.id),
          result_url: apiEndpoints.analysis.result(reusableAnalysis.id),
        }, (statusPayload) => {
          setLoadingProgress(statusPayload.progress_percent || 0);
          const phaseLabels = {
            pending: 'AI tahlil navbatda...',
            processing: 'AI risk va moslik omillarini tekshirmoqda...',
            success: 'AI tahlil yakunlandi...',
            failed: 'AI tahlil xatolik bilan yakunlandi...',
          };
          setAnalysisPhase(phaseLabels[statusPayload.status] || 'AI tahlil bajarilmoqda...');
        });
        setAnalysisData(analysis);
        setLoadingProgress(100);
        return;
      }

      // Step 3: Run AI Analysis via backend
      setAnalysisPhase('AI hujjatlarni tahlil qilmoqda...');
      const run = await startAnalysis(tender.id);
      setLoadingProgress(run.progress_percent || 0);

      const analysis = await pollAnalysisRun(run, (statusPayload) => {
        setLoadingProgress(statusPayload.progress_percent || 0);
        const phaseLabels = {
          pending: 'AI tahlil navbatga qo‘yildi...',
          processing: 'AI risk va moslik omillarini tekshirmoqda...',
          success: 'AI tahlil yakunlandi...',
          failed: 'AI tahlil xatolik bilan yakunlandi...',
        };
        setAnalysisPhase(phaseLabels[statusPayload.status] || 'AI tahlil bajarilmoqda...');
      });
      setAnalysisData(analysis);
      setLoadingProgress(100);
    } catch (err) {
      console.error('Analysis error:', err);
      const msg = err.response?.data?.message || err.response?.data?.error_code || err.response?.data?.error || err.message;
      setError(`Tahlil jarayonida xatolik: ${msg}`);
    } finally {
      setIsLoading(false);
    }
  }, [freeQuery, lotId, lotNumber]);

  useEffect(() => {
    if (!lotId && !lotNumber && !freeQuery) {
      navigate('/dashboard');
      return;
    }
    const analysisTimer = setTimeout(runAnalysis, 0);
    return () => clearTimeout(analysisTimer);
  }, [freeQuery, lotId, lotNumber, navigate, runAnalysis]);

  if (isLoading) {
    const steps = ['Qidiruv', 'Hujjatlar', 'Red Flags', 'Xulosa'];
    const loadingStep = Math.min(3, Math.floor((loadingProgress || 0) / 25));
    return (
      <div className="min-h-screen bg-surface-50 dark:bg-surface-950 flex flex-col items-center justify-center p-4">
        <div className="relative mb-6">
          <div className="w-20 h-20 rounded-full border-4 border-primary-100 dark:border-primary-900/30"></div>
          <Loader2 className="w-20 h-20 text-primary-500 animate-spin absolute top-0 left-0" />
        </div>
        <h2 className="text-xl font-bold text-surface-900 dark:text-white mb-2">AI tahlil jarayoni</h2>
        <p className="text-surface-500 text-center max-w-md h-6">{analysisPhase}</p>
        <div className="mt-8 flex gap-4">
          {steps.map((step, i) => {
            const isActive = i === loadingStep;
            const isDone = i < loadingStep;
            return (
              <div key={step} className="flex flex-col items-center gap-2">
                <div className={`w-3 h-3 rounded-full transition-colors duration-500 ${isActive ? 'bg-primary-500 shadow-[0_0_10px_rgba(59,130,246,0.6)] animate-pulse' : isDone ? 'bg-success-500' : 'bg-surface-300 dark:bg-surface-700'}`}></div>
                <span className={`text-xs transition-colors duration-500 ${isActive ? 'text-primary-600 font-bold' : isDone ? 'text-success-600 font-medium' : 'text-surface-400'}`}>{step}</span>
              </div>
            );
          })}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-surface-50 dark:bg-surface-950 flex flex-col items-center justify-center p-4">
        <AlertTriangle className="w-12 h-12 text-danger-500 mb-4" />
        <h2 className="text-xl font-bold text-surface-900 dark:text-white mb-2">Xatolik</h2>
        <p className="text-surface-500 text-center max-w-md mb-6">{error}</p>
        <div className="flex gap-3">
          <button onClick={() => navigate('/dashboard')} className="px-6 py-2.5 bg-surface-200 dark:bg-surface-800 text-surface-700 dark:text-white rounded-lg hover:bg-surface-300 dark:hover:bg-surface-700 font-medium">
            Orqaga
          </button>
          <button onClick={runAnalysis} className="px-6 py-2.5 bg-primary-600 text-white rounded-lg hover:bg-primary-700 font-medium flex items-center gap-2">
            <RotateCw className="w-4 h-4" /> Qayta urinish
          </button>
        </div>
      </div>
    );
  }

  if (!analysisData || !tenderData) return null;

  // Transform backend response to component format
  const displayData = {
    lotId: tenderData.lot_number,
    title: tenderData.title,
    customer: tenderData.buyer_name,
    deadline: tenderData.deadline,
    startPrice: parseFloat(tenderData.start_price),
    currency: 'UZS',
    platform: getPlatformLabel(tenderData.platform_source),
    aiMatchScore: analysisData.eligibility_score,
    summary: analysisData.summary_text,
    redFlags: (analysisData.red_flags || []).map((flag, i) => ({
      id: i + 1,
      title: flag.title,
      description: flag.reason || flag.description,
      level: flag.level === 'blocker' ? 'high' : flag.level === 'warning' ? 'medium' : 'low',
      recommendation: flag.recommendation,
    })),
    requirements: (analysisData.requirements || []).map(r => r.plain || r.original || r),
    missingDocuments: analysisData.missing_documents || [],
    standards: analysisData.standards || [],
    decision: analysisData.decision || {},
    analysisId: analysisData.id,
  };

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
              <span className="text-sm font-medium text-surface-500 dark:text-surface-400">Lot: #{displayData.lotId}</span>
              <h1 className="text-base font-bold text-surface-900 dark:text-white truncate max-w-md md:max-w-xl">
                {displayData.title}
              </h1>
            </div>
          </div>
          <div className="flex items-center gap-3">
            {tenderData.raw_portal_url && (
              <a 
                href={tenderData.raw_portal_url}
                target="_blank" rel="noopener noreferrer"
                className="hidden sm:inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-primary-600 bg-primary-50 dark:bg-primary-900/30 rounded-lg hover:bg-primary-100 transition-colors"
              >
                Manbaga o'tish <ExternalLink className="w-4 h-4" />
              </a>
            )}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Left Column: AI Analysis */}
          <div className="lg:col-span-2 space-y-8">
            <AITenderDashboard data={displayData} />
          </div>

          {/* Right Column: Smart Calculator */}
          <div className="lg:col-span-1">
            <div className="sticky top-24">
              <SmartCalculator tenderPrice={displayData.startPrice} analysisId={displayData.analysisId} />
            </div>
          </div>

        </div>
      </main>
    </div>
  );
}

async function findReusableAnalysis(tenderId) {
  const { results: analyses } = await fetchAnalysisHistory();
  const candidates = analyses.filter((analysis) => (
    analysis.tender_lot?.id === tenderId
    && analysis.analysis_status !== 'failed'
  ));
  return candidates[0] || null;
}

async function pollAnalysisRun(run, onStatus) {
  const statusUrl = run.status_url || apiEndpoints.analysis.status(run.id);
  const resultUrl = run.result_url || apiEndpoints.analysis.result(run.id);
  const startedAt = Date.now();
  const timeoutMs = 120000;

  while (Date.now() - startedAt < timeoutMs) {
    const statusPayload = await fetchAnalysisStatus(statusUrl);
    onStatus?.(statusPayload);
    if (statusPayload.status === 'success') {
      return fetchAnalysisResult(resultUrl);
    }
    if (statusPayload.status === 'failed') {
      throw new Error(statusPayload.error_message || 'AI provider is temporarily unavailable');
    }
    await wait(1500);
  }
  throw new Error('AI tahlil belgilangan vaqtda yakunlanmadi.');
}

function wait(ms) {
  return new Promise((resolve) => {
    window.setTimeout(resolve, ms);
  });
}

function getPlatformLabel(source) {
  const map = {
    'xarid_uzex': 'xarid.uzex.uz',
    'dxarid_uzex': 'dxarid.uzex.uz',
    'exarid_uzex': 'exarid.uzex.uz',
    'e_auksion': 'e-auksion.uz',
    'manual': "Qo'lda kiritilgan",
  };
  return map[source] || source;
}
