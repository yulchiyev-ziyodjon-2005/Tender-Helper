import { ShieldAlert, CheckCircle2, AlertTriangle, FileText, Bot, Building2 } from 'lucide-react';

export default function AITenderDashboard({ data }) {
  if (!data) return null;

  // Xatarlar darajasiga qarab rang ajratish
  const getFlagColor = (level) => {
    switch(level) {
      case 'high': return 'bg-danger-50 text-danger-700 border-danger-200 dark:bg-danger-900/30 dark:text-danger-300 dark:border-danger-800/50';
      case 'medium': return 'bg-warning-50 text-warning-700 border-warning-200 dark:bg-warning-900/30 dark:text-warning-300 dark:border-warning-800/50';
      default: return 'bg-surface-50 text-surface-700 border-surface-200 dark:bg-surface-800 dark:text-surface-300 dark:border-surface-700';
    }
  };

  const getFlagIcon = (level) => {
    switch(level) {
      case 'high': return <ShieldAlert className="w-5 h-5 text-danger-500 flex-shrink-0 mt-0.5" />;
      case 'medium': return <AlertTriangle className="w-5 h-5 text-warning-500 flex-shrink-0 mt-0.5" />;
      default: return <AlertTriangle className="w-5 h-5 text-surface-500 flex-shrink-0 mt-0.5" />;
    }
  };

  return (
    <div className="space-y-6">
      
      {/* Overview Card */}
      <div className="bg-white dark:bg-surface-900 rounded-2xl p-6 shadow-card border border-surface-200 dark:border-surface-800 flex flex-col md:flex-row gap-6 items-center">
        {/* Match Score Circle */}
        <div className="relative flex-shrink-0 w-32 h-32 flex items-center justify-center">
          <svg className="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
            <path
              className="text-surface-100 dark:text-surface-800"
              strokeWidth="3"
              stroke="currentColor"
              fill="none"
              d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
            />
            <path
              className={`${data.aiMatchScore >= 80 ? 'text-success-500' : data.aiMatchScore >= 50 ? 'text-warning-500' : 'text-danger-500'} transition-all duration-1000 ease-out`}
              strokeDasharray={`${data.aiMatchScore}, 100`}
              strokeWidth="3"
              strokeLinecap="round"
              stroke="currentColor"
              fill="none"
              d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className="text-3xl font-black text-surface-900 dark:text-white">{data.aiMatchScore}%</span>
            <span className="text-xs font-medium text-surface-500 uppercase">Moslik</span>
          </div>
        </div>

        <div className="flex-1 text-center md:text-left">
          <div className="flex items-center justify-center md:justify-start gap-2 mb-2 text-primary-600 dark:text-primary-400 font-semibold">
            <Bot className="w-5 h-5" /> AI Xulosasi
          </div>
          <p className="text-surface-700 dark:text-surface-300 text-lg leading-relaxed">
            Sizning kompaniya profilingiz ushbu tender talablariga {data.aiMatchScore}% mos keladi. 
            Biroq hujjatlarda {data.redFlags.length} ta xavfli shart (Red Flag) aniqlandi. Ishtirok etishdan oldin ularni ko'rib chiqing.
          </p>
          <div className="mt-4 flex flex-wrap gap-4 items-center justify-center md:justify-start text-sm text-surface-600 dark:text-surface-400">
            <div className="flex items-center gap-1.5"><Building2 className="w-4 h-4" /> {data.customer}</div>
          </div>
        </div>
      </div>

      {/* Red Flags Section */}
      <div className="bg-white dark:bg-surface-900 rounded-2xl shadow-card border border-surface-200 dark:border-surface-800 overflow-hidden">
        <div className="p-6 border-b border-surface-200 dark:border-surface-800 bg-surface-50/50 dark:bg-surface-900/50 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <ShieldAlert className="w-6 h-6 text-danger-500" />
            <h2 className="text-xl font-bold text-surface-900 dark:text-white">Red Flags (Yashirin xatarlar)</h2>
          </div>
          <span className="bg-danger-100 text-danger-700 dark:bg-danger-900/40 dark:text-danger-300 py-1 px-3 rounded-full text-sm font-bold">
            {data.redFlags.length} ta xavf
          </span>
        </div>
        <div className="p-6 space-y-4">
          {data.redFlags.map(flag => (
            <div key={flag.id} className={`flex gap-4 p-4 rounded-xl border ${getFlagColor(flag.level)}`}>
              {getFlagIcon(flag.level)}
              <div>
                <h3 className="font-bold mb-1">{flag.title}</h3>
                <p className="text-sm opacity-90 leading-relaxed">{flag.description}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

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
