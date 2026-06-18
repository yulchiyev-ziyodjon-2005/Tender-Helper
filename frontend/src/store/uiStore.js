import { create } from 'zustand';

const THEME_KEY = 'theme';

function getInitialDarkMode() {
  const storedTheme = localStorage.getItem(THEME_KEY);
  if (storedTheme) {
    return storedTheme === 'dark';
  }

  return window.matchMedia?.('(prefers-color-scheme: dark)').matches ?? false;
}

const useUIStore = create((set) => ({
  isDarkMode: getInitialDarkMode(),

  toggleDarkMode: () => set((state) => {
    const isDarkMode = !state.isDarkMode;
    localStorage.setItem(THEME_KEY, isDarkMode ? 'dark' : 'light');
    return { isDarkMode };
  }),

  isSidebarOpen: true,
  toggleSidebar: () => set((state) => ({
    isSidebarOpen: !state.isSidebarOpen,
  })),

  isMobileMenuOpen: false,
  setMobileMenuOpen: (isMobileMenuOpen) => set({ isMobileMenuOpen }),

  toasts: [],
  addToast: (toast) => set((state) => ({
    toasts: [
      ...state.toasts,
      {
        id: crypto.randomUUID(),
        type: 'info',
        duration: 4000,
        ...toast,
      },
    ],
  })),
  removeToast: (id) => set((state) => ({
    toasts: state.toasts.filter((toast) => toast.id !== id),
  })),
}));

export default useUIStore;
