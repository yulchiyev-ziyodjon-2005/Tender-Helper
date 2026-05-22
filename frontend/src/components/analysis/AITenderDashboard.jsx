import { ShieldAlert, CheckCircle2, AlertTriangle, FileText, Bot, Building2, FileWarning, BookOpen, Lightbulb, Info } from 'lucide-react';
import { useTranslation } from 'react-i18next';

export default function AITenderDashboard({ data }) {
  const { t } = useTranslation();

  if (!data) return null;

  // Determine color coding based on score
  const getScoreColor = (score) => {
    if (score >= 80) return 'text-success-500';
    if (score >= 50) return 'text-warning-500';
    return 'text-danger-500';
  };

  const getFlagColor = (level) => {
    switch (level) {
      case 'high': return 'bg-danger-50/50 dark:bg-danger-900/10 border-danger-100 dark:border-danger-800/30 text-danger-700 dark:text-danger-300';
      case 'medium': return 'bg-warning-50/50 dark:bg-warning-900/10 border-warning-100 dark:border-warning-800/30 text-warning-700 dark:text-warning-300';
      default: return 'bg-surface-50 dark:bg-surface-800/50 border-surface-200 dark:border-surface-700 text-surface-700 dark:text-surface-300';
    }
  };

  const getFlagIcon = (level) => {
    switch (level) {
      case 'high': return <ShieldAlert className="w-5 h-5 text-danger-500 mt-0.5 flex-shrink-0" />;
      case 'medium': return <AlertTriangle className="w-5 h-5 text-warning-500 mt-0.5 flex-shrink-0" />;
      default: return <Info className="w-5 h-5 text-surface-500 mt-0.5 flex-shrink-0" />;
    }
  };

  const scoreColor = getScoreColor(data.aiMatchScore);

  return (
    <div className="space-y-6">
      
      {/* Overview Card */}
      <div className="bg-white dark:bg-surface-900 rounded-2xl p-6 sm:p-8 shadow-card border border-surface-200 dark:border-surface-800 flex flex-col md:flex-row items-center gap-8 relative overflow-hidden">
        {/* Decorative background element */}
        <div className="absolute top-0 right-0 w-64 h-64 bg-primary-500/5 rounded-full blur-3xl -translate-y-1/2 translate-x-1/3"></div>
        
        {/* Score Circle */}
        <div className="relative w-40 h-40 flex-shrink-0">
          <svg className="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
            <path className="text-surface-100 dark:text-surface-800" strokeWidth="3" stroke="currentColor" fill="none"
              d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
            <path className={`${scoreColor} transition-all duration-1000 ease-out`}
              strokeDasharray={`${data.aiMatchScore}, 100`} strokeWidth="3" strokeLinecap="round" stroke="currentColor" fill="none"
              d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className="text-3xl font-black text-surface-900 dark:text-white">{data.aiMatchScore}%</span>
            <span className="text-xs font-medium text-surface-500 uppercase">{t('match')}</span>
          </div>
        </div>

        <div className="flex-1 text-center md:text-left">
          <div className="flex items-center justify-center md:justify-start gap-2 mb-2 text-primary-600 dark:text-primary-400 font-semibold">
            <Bot className="w-5 h-5" /> {t('ai_analysis')}
          </div>
          <p className="text-surface-700 dark:text-surface-300 text-lg leading-relaxed">
            {data.summary || `Sizning kompaniya profilingiz ushbu tender talablariga ${data.aiMatchScore}% mos keladi.`}
          </p>
          <div className="mt-4 flex flex-wrap gap-4 items-center justify-center md:justify-start text-sm text-surface-600 dark:text-surface-400">
            <div className="flex items-center gap-1.5"><Building2 className="w-4 h-4" /> {data.customer || t('customer')}</div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Recommendation Box */}
        {data.decision && data.decision.recommendation && (
        <div className="bg-white dark:bg-surface-900 rounded-2xl shadow-card border border-surface-200 dark:border-surface-800 overflow-hidden">
          <div className="p-6 border-b border-surface-200 dark:border-surface-800 flex items-center gap-2">
            <Lightbulb className="w-6 h-6 text-warning-500" />
            <h2 className="text-xl font-bold text-surface-900 dark:text-white">{t('ai_recommendation')}</h2>
          </div>
          <div className="p-6">
            <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-full text-sm font-bold mb-4 ${
              data.aiMatchScore >= 75 ? 'bg-success-100 text-success-700 dark:bg-success-900/30 dark:text-success-300' :
              data.aiMatchScore >= 50 ? 'bg-warning-100 text-warning-700 dark:bg-warning-900/30 dark:text-warning-300' :
              'bg-danger-100 text-danger-700 dark:bg-danger-900/30 dark:text-danger-300'
            }`}>
              {data.decision.recommendation}
            </div>
            
            {data.decision.next_actions && data.decision.next_actions.length > 0 && (
              <div className="mt-4">
                <h4 className="text-sm font-semibold text-surface-600 dark:text-surface-400 mb-3">{t('next_steps')}:</h4>
                <ul className="space-y-2">
                  {data.decision.next_actions.map((action, i) => (
                    <li key={i} className="flex items-start gap-3 text-surface-700 dark:text-surface-300">
                      <span className="w-6 h-6 rounded-full bg-primary-100 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400 flex items-center justify-center text-xs font-bold flex-shrink-0">{i + 1}</span>
                      <span>{action}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
            
            {data.decision.disclaimer && (
              <p className="mt-4 text-xs text-surface-400 italic">{data.decision.disclaimer}</p>
            )}
          </div>
        </div>
        )}

      {/* Red Flags Section */}
      <div className="bg-white dark:bg-surface-900 rounded-2xl shadow-card border border-surface-200 dark:border-surface-800 overflow-hidden">
        <div className="p-6 border-b border-surface-200 dark:border-surface-800 bg-surface-50/50 dark:bg-surface-900/50 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <ShieldAlert className="w-6 h-6 text-danger-500" />
            <h2 className="text-xl font-bold text-surface-900 dark:text-white">Red Flags (Yashirin xatarlar)</h2>
          </div>
          <span className={`py-1 px-3 rounded-full text-sm font-bold ${
            data.redFlags.length > 0 ? 'bg-danger-100 text-danger-700 dark:bg-danger-900/40 dark:text-danger-300' :
            'bg-success-100 text-success-700 dark:bg-success-900/40 dark:text-success-300'
          }`}>
            {data.redFlags.length > 0 ? `${data.redFlags.length} ta xavf` : 'Xavf topilmadi'}
          </span>
        </div>
        <div className="p-6 space-y-4">
          {data.redFlags.length === 0 && (
            <div className="text-center py-4">
              <CheckCircle2 className="w-10 h-10 text-success-400 mx-auto mb-2" />
              <p className="text-surface-500">Ushbu tenderda yashirin xatarlar aniqlanmadi.</p>
            </div>
          )}
          {data.redFlags.map(flag => (
            <div key={flag.id} className={`flex gap-4 p-4 rounded-xl border ${getFlagColor(flag.level)}`}>
              {getFlagIcon(flag.level)}
              <div className="flex-1">
                <h3 className="font-bold mb-1">{flag.title}</h3>
                <p className="text-sm opacity-90 leading-relaxed">{flag.description}</p>
                {flag.recommendation && (
                  <p className="text-sm mt-2 font-medium opacity-80">💡 {flag.recommendation}</p>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
      </div>

      {/* Missing Documents */}
      {data.missingDocuments && data.missingDocuments.length > 0 && (
        <div className="bg-white dark:bg-surface-900 rounded-2xl shadow-card border border-surface-200 dark:border-surface-800 overflow-hidden">
          <div className="p-6 border-b border-surface-200 dark:border-surface-800 flex items-center gap-2">
            <FileWarning className="w-6 h-6 text-warning-500" />
            <h2 className="text-xl font-bold text-surface-900 dark:text-white">Kerakli Hujjatlar</h2>
          </div>
          <div className="p-6 space-y-3">
            {data.missingDocuments.map((doc, i) => (
              <div key={i} className="flex items-start gap-3 p-3 rounded-lg bg-warning-50/50 dark:bg-warning-900/10 border border-warning-100 dark:border-warning-800/30">
                <FileText className="w-5 h-5 text-warning-500 flex-shrink-0 mt-0.5" />
                <div>
                  <h4 className="font-semibold text-surface-900 dark:text-white">{doc.name}</h4>
                  <p className="text-sm text-surface-500">{doc.reason}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Standards */}
      {data.standards && data.standards.length > 0 && (
        <div className="bg-white dark:bg-surface-900 rounded-2xl shadow-card border border-surface-200 dark:border-surface-800 overflow-hidden">
          <div className="p-6 border-b border-surface-200 dark:border-surface-800 flex items-center gap-2">
            <BookOpen className="w-6 h-6 text-primary-500" />
            <h2 className="text-xl font-bold text-surface-900 dark:text-white">Standartlar va Sertifikatlar</h2>
          </div>
          <div className="p-6 space-y-3">
            {data.standards.map((std, i) => (
              <div key={i} className="flex items-start gap-3 p-3 rounded-lg bg-primary-50/50 dark:bg-primary-900/10 border border-primary-100 dark:border-primary-800/30">
                <CheckCircle2 className="w-5 h-5 text-primary-500 flex-shrink-0 mt-0.5" />
                <div>
                  <h4 className="font-semibold text-surface-900 dark:text-white">{std.name}</h4>
                  <p className="text-sm text-surface-500">{std.meaning}</p>
                  {std.action && <p className="text-sm text-primary-600 dark:text-primary-400 mt-1">→ {std.action}</p>}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Key Requirements Section */}
      <div className="bg-white dark:bg-surface-900 rounded-2xl shadow-card border border-surface-200 dark:border-surface-800 overflow-hidden">
        <div className="p-6 border-b border-surface-200 dark:border-surface-800 flex items-center gap-2">
          <FileText className="w-6 h-6 text-primary-500" />
          <h2 className="text-xl font-bold text-surface-900 dark:text-white">Asosiy Texnik Talablar</h2>
        </div>
        <div className="p-6">
          <ul className="space-y-4">
            {data.requirements.map((req, idx) => (
              <li key={idx} className="flex items-start gap-3 text-surface-700 dark:text-surface-300">
                <CheckCircle2 className="w-5 h-5 text-success-500 flex-shrink-0 mt-0.5" />
                <span className="leading-relaxed">{req}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

    </div>
  );
}
