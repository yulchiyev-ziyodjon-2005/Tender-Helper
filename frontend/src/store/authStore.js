/**
 * TenderHelper AI — Auth Store (Zustand)
 * ========================================
 * Autentifikatsiya holatini boshqarish.
 */

import { create } from 'zustand';

const useAuthStore = create((set) => ({
  // State
  user: null,
  isAuthenticated: !!localStorage.getItem('access_token'),
  isLoading: false,

  // Actions
  setUser: (user) => set({ user, isAuthenticated: true }),

  login: (tokens, user = null) => {
    localStorage.setItem('access_token', tokens.access);
    localStorage.setItem('refresh_token', tokens.refresh);
    set({ isAuthenticated: true, user });
  },

  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    set({ user: null, isAuthenticated: false });
  },

  setLoading: (isLoading) => set({ isLoading }),
}));

export default useAuthStore;
