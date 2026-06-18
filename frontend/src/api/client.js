/**
 * TenderHelper AI — Axios API Client
 * =====================================
 * Markazlashtirilgan HTTP client.
 * JWT token interceptor va xato boshqaruvi.
 */

import axios from 'axios';
import { API_BASE_URL } from '../utils/constants';
import { apiEndpoints } from './endpoints';
import {
  clearTokens,
  getAccessToken,
  getRefreshToken,
  updateTokens,
} from '../utils/tokenStorage';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 sekund
  headers: {
    'Content-Type': 'application/json',
  },
});

// ──────────── Request Interceptor ────────────
// Har bir so'rovga JWT token qo'shish
apiClient.interceptors.request.use(
  (config) => {
    const token = getAccessToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// ──────────── Response Interceptor ────────────
// 401 da tokenni yangilash yoki logout qilish
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // 401 Unauthorized — token muddati tugagan
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      const refreshToken = getRefreshToken();
      if (refreshToken) {
        try {
          const { data } = await axios.post(`${API_BASE_URL}${apiEndpoints.auth.refresh}`, {
            refresh: refreshToken,
          });

          // Yangi tokenlarni saqlash
          updateTokens(data);

          // So'rovni qayta yuborish
          originalRequest.headers.Authorization = `Bearer ${data.access}`;
          return apiClient(originalRequest);
        } catch (refreshError) {
          // Refresh ham ishlamadi — logout
          clearTokens();
          window.location.href = '/login';
          return Promise.reject(refreshError);
        }
      } else {
        // Refresh token yo'q — logout
        clearTokens();
        window.location.href = '/login';
      }
    }

    return Promise.reject(error);
  }
);

export default apiClient;
