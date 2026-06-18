import apiClient from './client';
import { apiEndpoints } from './endpoints';

export async function fetchSubscriptionEntitlements(params = {}) {
  const { data } = await apiClient.get(apiEndpoints.subscriptions.entitlements, {
    params,
  });
  return data;
}
