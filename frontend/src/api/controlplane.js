import apiClient from './client';

export async function fetchAdminOverview(params = {}) {
  const { data } = await apiClient.get('/admin/overview/', { params });
  return data;
}

export async function fetchAdminAudit(params = {}) {
  const { data } = await apiClient.get('/admin/audit/', { params });
  return data;
}
