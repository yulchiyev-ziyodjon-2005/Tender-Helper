import apiClient from './client';
import { apiEndpoints } from './endpoints';
import { API_BASE_URL } from '../utils/constants';

export async function loginWithEmail(payload) {
  const { data } = await apiClient.post(apiEndpoints.auth.login, payload);
  return data;
}

export async function registerWithEmail(payload) {
  const { data } = await apiClient.post(apiEndpoints.auth.register, payload);
  return data;
}

export async function sendOtp(phoneNumber) {
  const { data } = await apiClient.post(apiEndpoints.auth.sendOtp, {
    phone_number: phoneNumber,
  });
  return data;
}

export async function verifyOtp(payload) {
  const { data } = await apiClient.post(apiEndpoints.auth.verifyOtp, payload);
  return data;
}

export async function verifyRegistrationPhone(payload) {
  const { data } = await apiClient.post(apiEndpoints.auth.verifyPhone, payload);
  return data;
}

export async function requestPasswordReset(email) {
  const { data } = await apiClient.post(apiEndpoints.auth.forgotPassword, { email });
  return data;
}

export async function resetPassword(payload) {
  const { data } = await apiClient.post(apiEndpoints.auth.resetPassword, payload);
  return data;
}

export async function changePassword(payload) {
  const { data } = await apiClient.post(apiEndpoints.auth.changePassword, payload);
  return data;
}

export async function exchangeGoogleOAuthCode(code) {
  const { data } = await apiClient.post(apiEndpoints.auth.googleExchange, { code });
  return data;
}

export async function fetchGoogleOAuthConfig() {
  const { data } = await apiClient.get(apiEndpoints.auth.googleConfig);
  return data;
}

export function googleOAuthStartUrl(next = '/dashboard') {
  return `${API_BASE_URL}${apiEndpoints.auth.googleStart}?next=${encodeURIComponent(next)}`;
}
