import { useTranslation } from 'react-i18next';
import { Moon, Sun } from 'lucide-react';
import useUIStore from '../../store/uiStore';

export default function ThemeToggle() {
  const { t } = useTranslation();
  const isDark = useUIStore((state) => state.isDarkMode);
  const toggleTheme = useUIStore((state) => state.toggleDarkMode);

  return (
    <button
      onClick={toggleTheme}
      title={isDark ? t('nav.light_mode') : t('nav.dark_mode')}
      className="p-2 text-surface-500 hover:text-primary-600 dark:text-surface-400 dark:hover:text-primary-400 bg-white dark:bg-surface-900 border border-surface-200 dark:border-surface-700 rounded-lg hover:bg-surface-50 dark:hover:bg-surface-800 transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500"
    >
      {isDark ? (
        <Sun className="w-5 h-5" />
      ) : (
        <Moon className="w-5 h-5" />
      )}
    </button>
  );
}
