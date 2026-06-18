import { create } from 'zustand';
import {
  clearTokens,
  hasStoredSession,
  requiresStoredPasswordChange,
  storeTokens,
} from '../utils/tokenStorage';

const useAuthStore = create((set) => ({
  user: null,
  isAuthenticated: hasStoredSession(),
  requiresPasswordChange: requiresStoredPasswordChange(),
  isLoading: false,

  setUser: (user) => set({
    user,
    isAuthenticated: hasStoredSession(),
  }),

  login: (tokens, user = null, options = {}) => {
    if (!tokens?.access || !tokens?.refresh) {
      throw new Error('Access and refresh tokens are required.');
    }

    const requiresPasswordChange = Boolean(options.requiresPasswordChange);
    storeTokens(tokens, Boolean(options.remember), requiresPasswordChange);
    set({
      user,
      isAuthenticated: true,
      requiresPasswordChange,
      isLoading: false,
    });
  },

  logout: () => {
    clearTokens();
    set({
      user: null,
      isAuthenticated: false,
      requiresPasswordChange: false,
      isLoading: false,
    });
  },

  setLoading: (isLoading) => set({ isLoading }),
}));

export default useAuthStore;
