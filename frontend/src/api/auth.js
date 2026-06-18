import apiClient from './client';
import { API_BASE_URL } from '../utils/constants';

export async function loginWithEmail(payload) {
  const { data } = await apiClient.post('/auth/login/', payload);
  return data;
}

export async function registerWithEmail(payload) {
  const { data } = await apiClient.post('/auth/register/', payload);
  return data;
}

export async function sendOtp(phoneNumber) {
  const { data } = await apiClient.post('/auth/send-otp/', {
    phone_number: phoneNumber,
  });
  return data;
}

export async function verifyRegistrationPhone(payload) {
  const { data } = await apiClient.post('/auth/verify-phone/', payload);
  return data;
}

export async function requestPasswordReset(email) {
  const { data } = await apiClient.post('/auth/forgot-password/', { email });
  return data;
}

export async function resetPassword(payload) {
  const { data } = await apiClient.post('/auth/reset-password/', payload);
  return data;
}

export async function changePassword(payload) {
  const { data } = await apiClient.post('/auth/change-password/', payload);
  return data;
}

export async function exchangeGoogleOAuthCode(code) {
  const { data } = await apiClient.post('/auth/google/exchange/', { code });
  return data;
}

export async function fetchGoogleOAuthConfig() {
  const { data } = await apiClient.get('/auth/google/config/');
  return data;
}

export function googleOAuthStartUrl(next = '/dashboard') {
  return `${API_BASE_URL}/auth/google/start/?next=${encodeURIComponent(next)}`;
}
