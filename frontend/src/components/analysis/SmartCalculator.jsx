import { useState, useEffect } from 'react';
import { Calculator, AlertTriangle, TrendingDown, TrendingUp, Info, ExternalLink } from 'lucide-react';
import apiClient from '../../api/client';

export default function SmartCalculator({ tenderPrice = 0, analysisId }) {
  // Inputs
  const [cost, setCost] = useState('');
  
  // Settings
  const vatRate = 0.12; // 12%
  const uzexRate = 0.0015; // 0.15%
  const guaranteeRate = 0.03; // 3% zakalat
  
  // Results
  const [results, setResults] = useState({
    vat: 0,
    uzexFee: 0,
    guarantee: 0,
    totalCost: 0,
    profit: 0,
    profitMargin: 0,
    stopLoss: 0
  });

  useEffect(() => {
    const rawCost = Number(cost.replace(/[^0-9]/g, '')) || 0;
    const winPrice = tenderPrice; 

    const vat = rawCost * vatRate;
    const uzexFee = winPrice * uzexRate;
    const guarantee = winPrice * guaranteeRate;
    
    const totalCost = rawCost + vat + uzexFee;
    const profit = winPrice - totalCost;
    const profitMargin = winPrice > 0 ? (profit / winPrice) * 100 : 0;
    const stopLoss = totalCost;

    setResults({ vat, uzexFee, guarantee, totalCost, profit, profitMargin, stopLoss });

    // Sync with backend if analysisId is provided
    if (analysisId && rawCost > 0) {
      const syncDebounce = setTimeout(() => {
        apiClient.post(`/analysis/${analysisId}/calculate/`, {
          raw_material_cost: rawCost,
          logistics_cost: 0,
          labor_cost: 0,
          other_expenses: 0
        }).catch(err => console.error('Calculator sync failed:', err));
      }, 1000);
      return () => clearTimeout(syncDebounce);
    }
  }, [cost, tenderPrice, analysisId]);

  const formatMoney = (amount) => {
    return new Intl.NumberFormat('uz-UZ', { style: 'currency', currency: 'UZS', maximumFractionDigits: 0 }).format(amount);
  };

  const handleCostChange = (e) => {
    // Fowmatlash bilan kiritish
    const val = e.target.value.replace(/[^0-9]/g, '');
    if (val) {
      setCost(new Intl.NumberFormat('uz-UZ').format(val));
    } else {
      setCost('');
    }
  };

  return (
    <div className="bg-white dark:bg-surface-900 rounded-2xl shadow-card border border-surface-200 dark:border-surface-800 overflow-hidden">
      <div className="p-6 border-b border-surface-200 dark:border-surface-800 bg-surface-50/50 dark:bg-surface-900/50 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Calculator className="w-5 h-5 text-primary-600 dark:text-primary-400" />
          <h2 className="text-lg font-bold text-surface-900 dark:text-white">Smart Kalkulyator</h2>
        </div>
      </div>

      <div className="p-6 space-y-6">
        {/* Boshlang'ich Narx */}
        <div>
          <label className="text-xs font-semibold text-surface-500 uppercase tracking-wider mb-2 block">Lot Boshlang'ich Narxi</label>
          <div className="text-xl font-black text-surface-900 dark:text-white tabular-nums">
            {formatMoney(tenderPrice)}
          </div>
        </div>

        {/* Tannarx Input */}
        <div>
          <label className="text-sm font-semibold text-surface-700 dark:text-surface-300 mb-2 flex items-center justify-between">
            Tannarxingiz (Xarajatlar)
            <div className="group relative">
              <Info className="w-4 h-4 text-surface-400 cursor-help" />
              <div className="absolute right-0 bottom-full mb-2 w-48 p-2 bg-surface-800 text-white text-xs rounded shadow-lg hidden group-hover:block z-10">
                Logistika, tovar narxi va boshqa operatsion xarajatlarni qo'shib yozing. (QQS siz)
              </div>
            </div>
          </label>
          <div className="relative">
            <input
              type="text"
              value={cost}
              onChange={handleCostChange}
              placeholder="Masalan: 1 500 000"
              className="w-full px-4 py-3 bg-surface-50 dark:bg-surface-950 border border-surface-200 dark:border-surface-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 font-bold text-lg tabular-nums text-surface-900 dark:text-white"
            />
            <span className="absolute right-4 top-1/2 -translate-y-1/2 text-surface-400 font-medium">UZS</span>
          </div>
        </div>

        {/* Hisob kitoblar ro'yxati */}
        <div className="bg-surface-50 dark:bg-surface-950/50 rounded-xl p-4 space-y-3 text-sm">
          <div className="flex justify-between text-surface-600 dark:text-surface-400">
            <span>Tannarx qismi:</span>
            <span className="font-medium">{cost ? formatMoney(Number(cost.replace(/[^0-9]/g, ''))) : '0 UZS'}</span>
          </div>
          <div className="flex justify-between text-surface-600 dark:text-surface-400">
            <span>QQS (12%):</span>
            <span className="font-medium text-danger-500">+{formatMoney(results.vat)}</span>
          </div>
          <div className="flex justify-between text-surface-600 dark:text-surface-400">
            <span>UzEx komissiyasi (0.15%):</span>
            <span className="font-medium text-danger-500">+{formatMoney(results.uzexFee)}</span>
          </div>
          <div className="pt-3 border-t border-surface-200 dark:border-surface-800 flex justify-between font-bold text-surface-900 dark:text-white">
            <span>Jami Xarajat:</span>
            <span>{formatMoney(results.totalCost)}</span>
          </div>
        </div>

        {/* Zakalat eslatmasi */}
        <div className="flex items-start gap-3 p-3 rounded-xl bg-primary-50 dark:bg-primary-900/20 border border-primary-100 dark:border-primary-800/50">
          <AlertTriangle className="w-5 h-5 text-primary-500 flex-shrink-0 mt-0.5" />
          <p className="text-xs text-primary-700 dark:text-primary-300">
            <strong>Eslatma:</strong> Qatnashish uchun RKP hisobingizda qo'shimcha {formatMoney(results.guarantee)} (3% zakalat) bo'lishi talab etiladi. Bu summa yutqazsangiz qaytariladi.
          </p>
        </div>

        {/* Foyda va Stop-loss */}
        <div className="pt-4 border-t border-surface-200 dark:border-surface-800">
          <div className="flex items-center justify-between mb-4">
            <div>
              <p className="text-xs font-semibold text-surface-500 uppercase tracking-wider mb-1">Kutilayotgan Foyda</p>
              <p className={`text-2xl font-black tabular-nums flex items-center gap-2 ${results.profit > 0 ? 'text-success-500' : results.profit < 0 ? 'text-danger-500' : 'text-surface-900 dark:text-white'}`}>
                {results.profit > 0 ? <TrendingUp className="w-6 h-6" /> : results.profit < 0 ? <TrendingDown className="w-6 h-6" /> : null}
                {formatMoney(results.profit)}
              </p>
            </div>
            <div className={`text-right ${results.profit > 0 ? 'text-success-500' : results.profit < 0 ? 'text-danger-500' : 'text-surface-500'}`}>
              <span className="text-xs font-bold bg-current/10 px-2.5 py-1 rounded-md">{results.profitMargin.toFixed(1)}% marja</span>
            </div>
          </div>

          <div className="bg-surface-900 text-white rounded-xl p-4 flex justify-between items-center mb-4">
            <div>
              <p className="text-surface-400 text-xs mb-1">Stop-Loss (Minimum narx)</p>
              <p className="font-bold text-lg">{formatMoney(results.stopLoss)}</p>
            </div>
            <div className="w-8 h-8 rounded-full bg-danger-500/20 flex items-center justify-center">
              <div className="w-3 h-3 rounded-full bg-danger-500 animate-pulse"></div>
            </div>
          </div>

          <a 
            href="https://xarid.uzex.uz/" 
            target="_blank" 
            rel="noopener noreferrer"
            className="w-full flex items-center justify-center gap-2 bg-primary-600 hover:bg-primary-700 text-white font-bold py-4 px-6 rounded-xl transition-colors shadow-lg shadow-primary-500/30"
          >
            Tenderda ishtirok etish <ExternalLink className="w-5 h-5" />
          </a>
        </div>

      </div>
    </div>
  );
}
