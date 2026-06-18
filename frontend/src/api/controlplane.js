import apiClient from './client';
import { apiEndpoints } from './endpoints';

export async function fetchAdminOverview(params = {}) {
  const { data } = await apiClient.get(apiEndpoints.admin.overview, { params });
  return data;
}

export async function fetchAdminAudit(params = {}) {
  const { data } = await apiClient.get(apiEndpoints.admin.audit, { params });
  return data;
}
