import apiClient from './client';

export async function fetchSubscriptionEntitlements(params = {}) {
  const { data } = await apiClient.get('/subscriptions/entitlements/', {
    params,
  });
  return data;
}
