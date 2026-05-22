import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Building2, Briefcase, Tag, Phone, ShieldCheck, ChevronRight, ChevronLeft } from 'lucide-react';
import OTPVerification from '../components/auth/OTPVerification';

export default function OnboardingPage() {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    businessType: '',
    industry: '',
    tags: [],
    phone: '',
  });

  const businessTypes = [
    { id: 'supplier', label: "Yetkazib beruvchi (Xaridorga sotuvchi)", icon: Briefcase },
    { id: 'customer', label: "Xaridor (Tender e'lon qiluvchi)", icon: Building2 },
    { id: 'both', label: "Ikkalasi ham", icon: Tag },
  ];

  const handleNext = () => setStep(s => Math.min(s + 1, 3));
  const handlePrev = () => setStep(s => Math.max(s - 1, 1));

  const completeOnboarding = () => {
    // TODO: Send user settings to API (PATCH /api/v1/auth/me/)
    // ...
    navigate('/dashboard');
  };

  return (
    <div className="min-h-screen bg-surface-50 dark:bg-surface-950 flex items-center justify-center p-4">
      <div className="w-full max-w-2xl bg-white dark:bg-surface-900 rounded-2xl shadow-card border border-surface-200 dark:border-surface-800 overflow-hidden">
        
        {/* Progress Bar */}
        <div className="bg-surface-100 dark:bg-surface-800 h-1.5 w-full">
          <motion.div 
            className="bg-primary-600 h-full"
            initial={{ width: '33%' }}
            animate={{ width: `${(step / 3) * 100}%` }}
          />
        </div>

        <div className="p-8 md:p-12">
          <AnimatePresence mode="wait">
            
            {/* STEP 1: Business Type */}
            {step === 1 && (
              <motion.div
                key="step1"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
              >
                <h2 className="text-2xl font-bold text-surface-900 dark:text-white mb-2">
                  TenderHelper'ga xush kelibsiz!
                </h2>
                <p className="text-surface-500 mb-8">
                  AI sizga mos tenderlarni topishi uchun quyidagilardan birini tanlang.
                </p>

                <div className="grid gap-4 mb-8">
                  {businessTypes.map((type) => {
                    const Icon = type.icon;
                    const isSelected = formData.businessType === type.id;
                    return (
                      <button
                        key={type.id}
                        onClick={() => setFormData({ ...formData, businessType: type.id })}
                        className={`flex items-center gap-4 p-4 rounded-xl border-2 text-left transition-all ${
                          isSelected 
                            ? 'border-primary-600 bg-primary-50 dark:bg-primary-900/20' 
                            : 'border-surface-200 dark:border-surface-700 hover:border-primary-300 dark:hover:border-primary-700'
                        }`}
                      >
                        <div className={`p-3 rounded-lg ${isSelected ? 'bg-primary-600 text-white' : 'bg-surface-100 dark:bg-surface-800 text-surface-600 dark:text-surface-400'}`}>
                          <Icon className="w-6 h-6" />
                        </div>
                        <div>
                          <h3 className={`font-semibold ${isSelected ? 'text-primary-900 dark:text-primary-100' : 'text-surface-900 dark:text-white'}`}>
                            {type.label}
                          </h3>
                        </div>
                      </button>
                    );
                  })}
                </div>

                <div className="flex justify-end">
                  <button
                    onClick={handleNext}
                    disabled={!formData.businessType}
                    className="flex items-center gap-2 px-6 py-3 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-lg disabled:opacity-50 transition-colors"
                  >
                    Keyingisi <ChevronRight className="w-5 h-5" />
                  </button>
                </div>
              </motion.div>
            )}

            {/* STEP 2: Phone Linking */}
            {step === 2 && (
              <motion.div
                key="step2"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
              >
                <div className="flex items-center gap-4 mb-6">
                  <button onClick={handlePrev} className="p-2 text-surface-500 hover:text-surface-900 dark:hover:text-white bg-surface-100 dark:bg-surface-800 rounded-lg">
                    <ChevronLeft className="w-5 h-5" />
                  </button>
                  <h2 className="text-2xl font-bold text-surface-900 dark:text-white">
                    Telefon raqamni ulash
                  </h2>
                </div>
                
                <p className="text-surface-500 mb-8">
                  Profil xavfsizligi va muhim tender xabarnomalari uchun telefon raqamingizni tasdiqlang.
                </p>

                <div className="bg-surface-50 dark:bg-surface-950 p-6 rounded-xl border border-surface-200 dark:border-surface-800 flex items-start gap-4 mb-8">
                  <ShieldCheck className="w-6 h-6 text-success-500 flex-shrink-0 mt-1" />
                  <div>
                    <h4 className="text-sm font-semibold text-surface-900 dark:text-white">Nega bu kerak?</h4>
                    <ul className="text-sm text-surface-500 mt-2 space-y-1 list-disc list-inside">
                      <li>Akkauntni to'liq himoyalash</li>
                      <li>Lotlar haqida SMS xabarnomalar olish</li>
                      <li>Smart Kalkulyatordan cheklovsiz foydalanish</li>
                    </ul>
                  </div>
                </div>

                <div className="flex justify-between items-center">
                  <button onClick={handleNext} className="text-surface-500 hover:text-surface-900 dark:text-surface-400 text-sm font-medium">
                    Hozircha o'tkazib yuborish
                  </button>
                  <button
                    onClick={() => setStep(2.5)}
                    className="flex items-center gap-2 px-6 py-3 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-lg transition-colors"
                  >
                    Raqamni tasdiqlash
                  </button>
                </div>
              </motion.div>
            )}

            {/* STEP 2.5: OTP Flow */}
            {step === 2.5 && (
              <motion.div
                key="step2.5"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 20 }}
              >
                {/* OTPVerification component requires a phone number to be set. 
                    In a real flow, we'd show a phone input first, then verify. 
                    For UI demonstration, we simulate successful linking. */}
                <h2 className="text-xl font-bold text-surface-900 dark:text-white mb-4">Raqam kiritish (Tez kunda...)</h2>
                <p className="text-surface-500 mb-6">SMS OTP integratsiyasi ulanmoqda...</p>
                <button onClick={() => setStep(3)} className="w-full py-3 bg-success-600 hover:bg-success-700 text-white rounded-lg">Tasdiqlandi deb hisoblaymiz →</button>
              </motion.div>
            )}

            {/* STEP 3: Finish */}
            {step === 3 && (
              <motion.div
                key="step3"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                className="text-center py-8"
              >
                <div className="w-20 h-20 bg-success-100 dark:bg-success-900/30 rounded-full flex items-center justify-center mx-auto mb-6">
                  <CheckCircle2 className="w-10 h-10 text-success-600 dark:text-success-400" />
                </div>
                <h2 className="text-3xl font-bold text-surface-900 dark:text-white mb-4">
                  Barchasi tayyor!
                </h2>
                <p className="text-surface-500 mb-8 max-w-sm mx-auto">
                  Endi AI Tender Mentor sizga yordam berishga tayyor. Asosiy panelga (Dashboard) o'tishingiz mumkin.
                </p>

                <button
                  onClick={completeOnboarding}
                  className="px-8 py-4 bg-primary-600 hover:bg-primary-700 text-white font-semibold rounded-xl shadow-lg shadow-primary-600/25 transition-all hover:-translate-y-1"
                >
                  Dashboard'ga o'tish
                </button>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}
