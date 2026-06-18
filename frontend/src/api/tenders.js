import apiClient from './client';
import { apiEndpoints } from './endpoints';

function unwrapResults(payload) {
  return Array.isArray(payload) ? payload : (payload.results || []);
}

export async function fetchTenders(params = {}) {
  const { data } = await apiClient.get(apiEndpoints.tenders.list, { params });
  return {
    payload: data,
    results: unwrapResults(data),
  };
}

export async function fetchTenderById(id) {
  const { data } = await apiClient.get(apiEndpoints.tenders.detail(id));
  return data;
}
