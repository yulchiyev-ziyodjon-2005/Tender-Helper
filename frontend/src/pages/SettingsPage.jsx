import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Building2, Save, ArrowLeft, Building, Hash, CreditCard, Tag, Loader2, AlertCircle } from 'lucide-react';
import apiClient from '../api/client';

export default function SettingsPage() {
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [isSaved, setIsSaved] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    setIsLoading(true);
    try {
      const { data } = await apiClient.get('/company/profile/');
      setProfile({
        companyName: data.company_name || '',
        stir: data.stir || '',
        companyType: data.company_type || 'mchj',
        hasVat: data.has_vat || false,
        industry: data.industry || '',
      });
    } catch (err) {
      // Profile might not exist yet — allow creation
      if (err.response?.status === 404) {
        setProfile({
          companyName: '',
          stir: '',
          companyType: 'mchj',
          hasVat: false,
          industry: '',
        });
      } else {
        setError('Profil ma\'lumotlarini yuklashda xatolik');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setProfile(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
    setIsSaved(false);
  };

  const handleSave = async (e) => {
    e.preventDefault();
    setIsSaving(true);
    setError(null);
    try {
      await apiClient.patch('/company/profile/', {
        company_name: profile.companyName,
        stir: profile.stir || null,
        company_type: profile.companyType,
        has_vat: profile.hasVat,
        industry: profile.industry,
      });
      setIsSaved(true);
      setTimeout(() => setIsSaved(false), 3000);
    } catch (err) {
      const msg = err.response?.data?.message || err.response?.data?.stir?.[0] || 'Saqlashda xatolik';
      setError(msg);
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-surface-50 dark:bg-surface-950 flex items-center justify-center">
        <Loader2 className="w-10 h-10 text-primary-500 animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-surface-50 dark:bg-surface-950 font-sans pb-12">
      {/* Header */}
      <header className="bg-white dark:bg-surface-900 border-b border-surface-200 dark:border-surface-800 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center gap-4">
          <button 
            onClick={() => navigate('/dashboard')}
            className="p-2 -ml-2 text-surface-500 hover:text-surface-900 dark:hover:text-white hover:bg-surface-100 dark:hover:bg-surface-800 rounded-lg transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div className="flex items-center gap-2">
            <Building2 className="w-5 h-5 text-primary-600 dark:text-primary-400" />
            <h1 className="text-lg font-bold text-surface-900 dark:text-white">
              Kompaniya Profili
            </h1>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white dark:bg-surface-900 rounded-2xl shadow-card border border-surface-200 dark:border-surface-800 overflow-hidden">
          
          <div className="p-6 border-b border-surface-200 dark:border-surface-800 bg-surface-50/50 dark:bg-surface-900/50">
            <h2 className="text-xl font-bold text-surface-900 dark:text-white">Asosiy ma'lumotlar</h2>
            <p className="text-surface-500 text-sm mt-1">
              Ushbu ma'lumotlar AI tahlil qilish va tenderdagi mosligingizni aniqlash uchun kerak bo'ladi.
            </p>
          </div>

          {error && (
            <div className="mx-6 mt-6 p-4 bg-danger-50 dark:bg-danger-900/20 border border-danger-200 dark:border-danger-800 rounded-xl flex items-center gap-3">
              <AlertCircle className="w-5 h-5 text-danger-500 flex-shrink-0" />
              <p className="text-danger-700 dark:text-danger-300 text-sm">{error}</p>
            </div>
          )}

          <form onSubmit={handleSave} className="p-6 sm:p-8 space-y-6">
            
            {/* STIR */}
            <div>
              <label className="text-sm font-semibold text-surface-700 dark:text-surface-300 mb-2 flex items-center gap-2">
                <Hash className="w-4 h-4 text-surface-400" /> STIR (INN)
              </label>
              <input
                type="text"
                name="stir"
                value={profile?.stir || ''}
                onChange={handleChange}
                maxLength={9}
                placeholder="9 xonali raqam"
                className="w-full px-4 py-3 bg-surface-50 dark:bg-surface-950 border border-surface-200 dark:border-surface-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 text-surface-900 dark:text-white font-medium"
              />
            </div>

            {/* Kompaniya Nomi */}
            <div>
              <label className="text-sm font-semibold text-surface-700 dark:text-surface-300 mb-2 flex items-center gap-2">
                <Building className="w-4 h-4 text-surface-400" /> Kompaniya (Tashkilot) nomi
              </label>
              <input
                type="text"
                name="companyName"
                value={profile?.companyName || ''}
                onChange={handleChange}
                placeholder="Masalan: OOO 'Tech Solutions'"
                className="w-full px-4 py-3 bg-surface-50 dark:bg-surface-950 border border-surface-200 dark:border-surface-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 text-surface-900 dark:text-white font-medium"
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Tashkiliy huquqiy shakl */}
              <div>
                <label className="text-sm font-semibold text-surface-700 dark:text-surface-300 mb-2 flex items-center gap-2">
                  <Tag className="w-4 h-4 text-surface-400" /> Tashkiliy shakl
                </label>
                <select
                  name="companyType"
                  value={profile?.companyType || 'mchj'}
                  onChange={handleChange}
                  className="w-full px-4 py-3 bg-surface-50 dark:bg-surface-950 border border-surface-200 dark:border-surface-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 text-surface-900 dark:text-white font-medium"
                >
                  <option value="mchj">MChJ</option>
                  <option value="yatt">YaTT</option>
                  <option value="aj">AJ</option>
                  <option value="tt">TT</option>
                </select>
              </div>

              {/* Soha */}
              <div>
                <label className="text-sm font-semibold text-surface-700 dark:text-surface-300 mb-2 flex items-center gap-2">
                  <Building2 className="w-4 h-4 text-surface-400" /> Faoliyat sohasi
                </label>
                <input
                  type="text"
                  name="industry"
                  value={profile?.industry || ''}
                  onChange={handleChange}
                  placeholder="IT, Qurilish, Tibbiyot..."
                  className="w-full px-4 py-3 bg-surface-50 dark:bg-surface-950 border border-surface-200 dark:border-surface-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 text-surface-900 dark:text-white font-medium"
                />
              </div>
            </div>

            {/* QQS */}
            <div className="pt-4 border-t border-surface-200 dark:border-surface-800">
              <label className="flex items-center gap-4 cursor-pointer p-4 rounded-xl border border-surface-200 dark:border-surface-700 hover:bg-surface-50 dark:hover:bg-surface-800/50 transition-colors">
                <div className="flex-1">
                  <div className="flex items-center gap-2 font-semibold text-surface-900 dark:text-white">
                    <CreditCard className="w-5 h-5 text-surface-400" /> QQS to'lovchisi
                  </div>
                  <p className="text-sm text-surface-500 mt-1 ml-7">
                    Kalkulyatorda QQS (12%) avtomatik hisobga olinadi.
                  </p>
                </div>
                <div className="relative inline-flex items-center">
                  <input 
                    type="checkbox" 
                    name="hasVat"
                    checked={profile?.hasVat || false}
                    onChange={handleChange}
                    className="sr-only peer" 
                  />
                  <div className="w-11 h-6 bg-surface-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 dark:peer-focus:ring-primary-800 rounded-full peer dark:bg-surface-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-surface-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-surface-600 peer-checked:bg-primary-600"></div>
                </div>
              </label>
            </div>

            {/* Submit Button */}
            <div className="pt-6 flex items-center justify-end gap-4 border-t border-surface-200 dark:border-surface-800">
              {isSaved && (
                <span className="text-success-600 dark:text-success-400 font-medium text-sm animate-pulse">
                  ✓ Muvaffaqiyatli saqlandi!
                </span>
              )}
              <button
                type="submit"
                disabled={isSaving}
                className="px-8 py-3 bg-primary-600 hover:bg-primary-700 text-white font-bold rounded-xl transition-all shadow-lg shadow-primary-600/20 hover:shadow-xl disabled:opacity-70 flex items-center gap-2"
              >
                {isSaving ? 'Saqlanmoqda...' : 'Saqlash'} <Save className="w-4 h-4" />
              </button>
            </div>

          </form>
        </div>
      </main>
    </div>
  );
}
