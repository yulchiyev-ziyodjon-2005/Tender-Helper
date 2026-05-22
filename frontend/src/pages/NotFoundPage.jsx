/**
 * TenderHelper AI — 404 Not Found Page
 */

import { Shield, ArrowLeft } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function NotFoundPage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex items-center justify-center bg-surface-50 dark:bg-surface-950 p-4">
      <div className="text-center fade-in">
        <div className="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-surface-100 dark:bg-surface-800 mb-6">
          <Shield className="w-10 h-10 text-surface-400" />
        </div>

        <h1 className="text-6xl font-bold text-surface-300 dark:text-surface-700 mb-2">
          404
        </h1>
        <h2 className="text-xl font-semibold text-surface-900 dark:text-white mb-2">
          Sahifa topilmadi
        </h2>
        <p className="text-surface-500 mb-8 max-w-sm mx-auto">
          Siz qidirgan sahifa mavjud emas yoki ko'chirilgan bo'lishi mumkin.
        </p>

        <button
          onClick={() => navigate('/dashboard')}
          className="inline-flex items-center gap-2 px-6 py-3 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-xl transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Bosh sahifaga qaytish
        </button>
      </div>
    </div>
  );
}
