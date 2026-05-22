/**
 * TenderHelper AI — UI Store (Zustand)
 * ======================================
 * Interfeys holati: dark mode, sidebar, toast.
 */

import { create } from 'zustand';

const useUIStore = create((set) => ({
  // Dark mode
  isDarkMode: localStorage.getItem('theme') === 'dark',
  toggleDarkMode: () =>
    set((state) => {
      const newMode = !state.isDarkMode;
      localStorage.setItem('theme', newMode ? 'dark' : 'light');

      // HTML clasiga dark qo'shish/olib tashlash
      if (newMode) {
        document.documentElement.classList.add('dark');
      } else {
        document.documentElement.classList.remove('dark');
      }

      return { isDarkMode: newMode };
    }),

  // Sidebar (desktop)
  isSidebarOpen: true,
  toggleSidebar: () => set((state) => ({ isSidebarOpen: !state.isSidebarOpen })),

  // Mobile menu
  isMobileMenuOpen: false,
  setMobileMenuOpen: (isOpen) => set({ isMobileMenuOpen: isOpen }),

  // Toast notifications
  toasts: [],
  addToast: (toast) =>
    set((state) => ({
      toasts: [
        ...state.toasts,
        {
          id: Date.now(),
          type: 'info',
          duration: 4000,
          ...toast,
        },
      ],
    })),
  removeToast: (id) =>
    set((state) => ({
      toasts: state.toasts.filter((t) => t.id !== id),
    })),
}));

export default useUIStore;
