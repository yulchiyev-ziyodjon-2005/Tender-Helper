import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Shield, Search, BrainCircuit, CheckCircle2, ChevronRight, BarChart3, Clock, MapPin } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import ThemeToggle from '../components/ui/ThemeToggle';
import LanguageSwitcher from '../components/ui/LanguageSwitcher';

export default function LandingPage() {
  // Hero Slider Images
  const heroImages = [
    "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=1920&q=80",
    "https://images.unsplash.com/photo-1504307651254-35680f356dfd?auto=format&fit=crop&w=1920&q=80",
    "https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=1920&q=80"
  ];

  const [currentImageIndex, setCurrentImageIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentImageIndex((prevIndex) => (prevIndex + 1) % heroImages.length);
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  // Mock Tenders Data to show real-world-like content
  const mockTenders = [
    {
      id: "24110012",
      title: "Kompyuter texnikalari va server uskunalarini xarid qilish",
      customer: "O'zbekiston Respublikasi Raqamli Texnologiyalar Vazirligi",
      price: "1 250 000 000 UZS",
      deadline: "2026-06-01",
      platform: "xarid.uzex.uz",
      tags: ["IT", "Uskunalar"],
      image: "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&w=600&q=80"
    },
    {
      id: "24110085",
      title: "Yangi ofis binosi uchun zamonaviy mebel jihozlari yetkazib berish",
      customer: "O'zsanoatqurilishbank ATB",
      price: "450 000 000 UZS",
      deadline: "2026-05-28",
      platform: "exarid.uzex.uz",
      tags: ["Mebel", "Korporativ"],
      image: "https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&w=600&q=80"
    },
    {
      id: "24110103",
      title: "Bulutli infratuzilma (Cloud) ijara xizmatlari",
      customer: "Elektron Hukumat Markazi",
      price: "890 000 000 UZS",
      deadline: "2026-06-15",
      platform: "xarid.uzex.uz",
      tags: ["IT", "Xizmatlar"],
      image: "https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=600&q=80"
    }
  ];

  return (
    <div className="min-h-screen bg-surface-50 dark:bg-surface-950 font-sans transition-colors duration-300">
      
      {/* ──────────────── NAVBAR ──────────────── */}
      <nav className="sticky top-0 z-50 bg-white/80 dark:bg-surface-900/80 backdrop-blur-md border-b border-surface-200 dark:border-surface-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-20">
            {/* Logo */}
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 flex items-center justify-center">
                <img src="/logo/logo-cropped.png" alt="Logo" className="w-full h-full object-contain" />
              </div>
              <span className="text-xl font-bold text-surface-900 dark:text-white hidden sm:block">
                TenderHelper
              </span>
            </div>

            {/* Desktop Menu */}
            <div className="hidden md:flex items-center gap-8">
              <a href="#features" className="text-sm font-medium text-surface-600 hover:text-primary-600 dark:text-surface-300 dark:hover:text-primary-400 transition-colors">Imkoniyatlar</a>
              <a href="#tenders" className="text-sm font-medium text-surface-600 hover:text-primary-600 dark:text-surface-300 dark:hover:text-primary-400 transition-colors">Ochiq Tenderlar</a>
            </div>

            {/* Auth & Toggles */}
            <div className="flex items-center gap-4">
              <ThemeToggle />
              <LanguageSwitcher />
              
              <Link to="/login" className="hidden sm:inline-flex text-sm font-medium text-surface-700 dark:text-surface-200 hover:text-primary-600 dark:hover:text-primary-400 transition-colors">
                Kirish
              </Link>
              <Link to="/login" className="inline-flex items-center justify-center px-5 py-2.5 text-sm font-medium text-white bg-primary-600 rounded-lg hover:bg-primary-700 transition-colors shadow-sm shadow-primary-600/20">
                Boshlash
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* ──────────────── HERO SECTION ──────────────── */}
      <section className="relative overflow-hidden pt-24 pb-32 min-h-[600px] flex items-center">
        {/* Background Slider */}
        <div className="absolute inset-0 z-0">
          <AnimatePresence mode="wait">
            <motion.img
              key={currentImageIndex}
              src={heroImages[currentImageIndex]}
              initial={{ opacity: 0, scale: 1.05 }}
              animate={{ opacity: 0.15, scale: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 1.5 }}
              className="absolute inset-0 w-full h-full object-cover mix-blend-luminosity dark:opacity-[0.05]"
              alt="Hero Background"
            />
          </AnimatePresence>
          {/* Gradient Overlay for Readability */}
          <div className="absolute inset-0 bg-gradient-to-b from-surface-50/80 via-surface-50/90 to-surface-50 dark:from-surface-950/80 dark:via-surface-950/90 dark:to-surface-950"></div>
        </div>

        <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-400 text-sm font-medium mb-6 border border-primary-100 dark:border-primary-800 backdrop-blur-sm">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-primary-500"></span>
              </span>
              Gemini AI 2.5 Flash bilan ishlaydi
            </span>

            <h1 className="text-5xl md:text-7xl font-extrabold text-surface-900 dark:text-white tracking-tight mb-8">
              Tenderlarda <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary-600 to-success-500">AI Mentor</span> orqali yutish ehtimolini oshiring
            </h1>
            
            <p className="max-w-2xl mx-auto text-lg md:text-xl text-surface-600 dark:text-surface-400 mb-10 leading-relaxed">
              Davlat va korporativ xaridlarda hujjatlarni AI yordamida tahlil qiling. Red Flag xatarlarini aniqlang, raqobatchilarni o'rganing va aniq xarajatlar kalkulyatsiyasi orqali yutuqqa erishing.
            </p>

            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link to="/login" className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-8 py-4 text-base font-semibold text-white bg-primary-600 rounded-xl hover:bg-primary-700 transition-all shadow-lg shadow-primary-600/25 hover:shadow-xl hover:shadow-primary-600/30 hover:-translate-y-0.5">
                Platformaga kirish
                <ChevronRight className="w-5 h-5" />
              </Link>
              <a href="#tenders" className="w-full sm:w-auto inline-flex items-center justify-center px-8 py-4 text-base font-semibold text-surface-700 dark:text-white bg-white/80 dark:bg-surface-800/80 backdrop-blur-md border border-surface-200 dark:border-surface-700 rounded-xl hover:bg-white dark:hover:bg-surface-700 transition-all shadow-sm">
                Hozirgi tenderlar
              </a>
            </div>
            
            <div className="mt-10 flex items-center justify-center gap-6 text-sm text-surface-600 dark:text-surface-400 font-medium">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-5 h-5 text-success-500" /> STIR orqali ro'yxatdan o'tish
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-5 h-5 text-success-500" /> Bepul tahlil limitlari
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* ──────────────── MOCK TENDERS SECTION ──────────────── */}
      <section id="tenders" className="py-20 bg-white dark:bg-surface-900 border-y border-surface-200 dark:border-surface-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-end mb-12">
            <div>
              <h2 className="text-3xl font-bold text-surface-900 dark:text-white mb-4">Ochiq Tender Lotlari</h2>
              <p className="text-surface-600 dark:text-surface-400">O'zbekistondagi so'nggi davlat va korporativ xaridlar ro'yxati.</p>
            </div>
            <Link to="/login" className="hidden sm:inline-flex items-center gap-2 text-primary-600 dark:text-primary-400 font-medium hover:underline">
              Barchasini ko'rish <ChevronRight className="w-4 h-4" />
            </Link>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {mockTenders.map((tender, idx) => (
              <motion.div 
                key={tender.id}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: idx * 0.1 }}
                className="group flex flex-col bg-surface-50 dark:bg-surface-950 border border-surface-200 dark:border-surface-800 rounded-2xl overflow-hidden hover:shadow-xl hover:shadow-surface-200/50 dark:hover:shadow-surface-900/50 transition-all hover:-translate-y-1"
              >
                {/* Image Section */}
                <div className="relative h-48 overflow-hidden">
                  <div className="absolute inset-0 bg-gradient-to-t from-surface-900/80 to-transparent z-10" />
                  <img 
                    src={tender.image} 
                    alt={tender.title} 
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                  />
                  <div className="absolute top-4 right-4 z-20">
                    <span className="text-xs font-semibold text-surface-900 bg-white px-3 py-1 rounded-full shadow-sm">
                      {tender.platform}
                    </span>
                  </div>
                  <div className="absolute bottom-4 left-4 z-20 text-white">
                    <span className="text-xs font-medium text-white/80 mb-1 block">Boshlang'ich narx</span>
                    <span className="text-lg font-bold">{tender.price}</span>
                  </div>
                </div>

                {/* Content Section */}
                <div className="p-6 flex flex-col flex-1">
                  <div className="flex justify-between items-start mb-3">
                    <span className="text-xs font-medium text-primary-600 dark:text-primary-400 bg-primary-50 dark:bg-primary-900/30 px-2.5 py-1 rounded-md border border-primary-100 dark:border-primary-800/50">
                      Lot: #{tender.id}
                    </span>
                  </div>
                  
                  <h3 className="text-lg font-semibold text-surface-900 dark:text-white leading-tight mb-3 line-clamp-2">
                    {tender.title}
                  </h3>
                  
                  <p className="text-sm text-surface-600 dark:text-surface-400 mb-6 line-clamp-2 flex items-start gap-2">
                    <MapPin className="w-4 h-4 mt-0.5 flex-shrink-0 text-surface-400" />
                    {tender.customer}
                  </p>

                  <div className="mt-auto">
                    <div className="flex items-center justify-between text-sm mb-6 pb-6 border-b border-surface-200 dark:border-surface-800">
                      <span className="text-surface-500">Tugash sanasi:</span>
                      <span className="font-semibold text-danger-600 dark:text-danger-400 flex items-center gap-1.5">
                        <Clock className="w-4 h-4" /> {tender.deadline}
                      </span>
                    </div>

                    <div className="flex flex-wrap gap-2 mb-6">
                      {tender.tags.map(tag => (
                        <span key={tag} className="px-2.5 py-1 text-xs font-medium bg-surface-200 dark:bg-surface-800 text-surface-700 dark:text-surface-300 rounded">
                          {tag}
                        </span>
                      ))}
                    </div>

                    <Link to="/login" className="flex items-center justify-center gap-2 w-full py-3 text-sm font-semibold text-surface-700 dark:text-white bg-white dark:bg-surface-800 border-2 border-surface-200 dark:border-surface-700 hover:border-primary-600 dark:hover:border-primary-500 hover:text-primary-600 dark:hover:text-primary-400 rounded-xl transition-all">
                      AI orqali tahlil qilish <ChevronRight className="w-4 h-4" />
                    </Link>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ──────────────── FEATURES SECTION ──────────────── */}
      <section id="features" className="py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-surface-900 dark:text-white mb-6">
              Biznesingiz uchun Enterprise darajasidagi vositalar
            </h2>
            <p className="text-lg text-surface-600 dark:text-surface-400">
              Tenderlarda xato qilmang. AI va ma'lumotlar tahlili orqali xarajatlarni to'g'ri hisoblab, xavflarni oldindan ko'ring.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            <div className="bg-white dark:bg-surface-900 rounded-2xl p-8 border border-surface-200 dark:border-surface-800 shadow-sm hover:shadow-card transition-all group">
              <div className="w-12 h-12 rounded-xl bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <BrainCircuit className="w-6 h-6 text-primary-600 dark:text-primary-400" />
              </div>
              <h3 className="text-xl font-semibold text-surface-900 dark:text-white mb-3">AI Tahlil</h3>
              <p className="text-surface-600 dark:text-surface-400 text-sm leading-relaxed">
                Texnik topshiriqlarni Gemini AI orqali yuridik va mantiqiy jihatdan tahlil qiling.
              </p>
            </div>

            <div className="bg-white dark:bg-surface-900 rounded-2xl p-8 border border-surface-200 dark:border-surface-800 shadow-sm hover:shadow-card transition-all group">
              <div className="w-12 h-12 rounded-xl bg-success-100 dark:bg-success-900/30 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <Shield className="w-6 h-6 text-success-600 dark:text-success-400" />
              </div>
              <h3 className="text-xl font-semibold text-surface-900 dark:text-white mb-3">Red Flags</h3>
              <p className="text-surface-600 dark:text-surface-400 text-sm leading-relaxed">
                Yashirin shartlar va qattiq jarimalar xavfi (Red Flag) bo'lsa darhol ogohlantirish oling.
              </p>
            </div>

            <div className="bg-white dark:bg-surface-900 rounded-2xl p-8 border border-surface-200 dark:border-surface-800 shadow-sm hover:shadow-card transition-all group">
              <div className="w-12 h-12 rounded-xl bg-amber-100 dark:bg-amber-900/30 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <BarChart3 className="w-6 h-6 text-amber-600 dark:text-amber-400" />
              </div>
              <h3 className="text-xl font-semibold text-surface-900 dark:text-white mb-3">Smart Kalkulyator</h3>
              <p className="text-surface-600 dark:text-surface-400 text-sm leading-relaxed">
                Xarajatlar, zakalat, operator komissiyasi va sof foydani real vaqtda hisoblab boring (Stop-loss funksiyasi bilan).
              </p>
            </div>

            <div className="bg-white dark:bg-surface-900 rounded-2xl p-8 border border-surface-200 dark:border-surface-800 shadow-sm hover:shadow-card transition-all group">
              <div className="w-12 h-12 rounded-xl bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <Search className="w-6 h-6 text-blue-600 dark:text-blue-400" />
              </div>
              <h3 className="text-xl font-semibold text-surface-900 dark:text-white mb-3">Raqobatchilar</h3>
              <p className="text-surface-600 dark:text-surface-400 text-sm leading-relaxed">
                Xarid portalidagi boshqa ishtirokchilar tarixi va g'alaba ko'rsatkichlari bazasi.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ──────────────── CTA & FOOTER ──────────────── */}
      <footer className="bg-surface-900 text-surface-300 pt-16 pb-8 border-t border-surface-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold text-white mb-6">Biznesingizni keyingi bosqichga olib chiqing</h2>
          <p className="text-surface-400 max-w-2xl mx-auto mb-10">Platformadan hoziroq bepul foydalanishni boshlang va tenderlarda ishtirok etish samaradorligini oshiring.</p>
          <Link to="/login" className="inline-flex items-center justify-center px-8 py-4 text-base font-semibold text-surface-900 bg-white rounded-xl hover:bg-surface-50 transition-colors mb-16">
            Bepul Ro'yxatdan O'tish
          </Link>
          
          <div className="pt-8 border-t border-surface-800 flex flex-col md:flex-row items-center justify-between gap-4 text-sm">
            <div className="flex items-center gap-2">
              <img src="/logo/logo-cropped.png" alt="Logo" className="w-6 h-6 rounded grayscale" />
              <span className="text-white font-medium">TenderHelper AI</span>
            </div>
            <p>© 2026 TenderHelper. Barcha huquqlar himoyalangan.</p>
            <div className="flex gap-4">
              <a href="#" className="hover:text-white transition-colors">Maxfiylik Siyosati</a>
              <a href="#" className="hover:text-white transition-colors">Foydalanish Shartlari</a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
