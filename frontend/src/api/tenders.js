import apiClient from './client';

function unwrapResults(payload) {
  return Array.isArray(payload) ? payload : (payload.results || []);
}

export async function fetchTenders(params = {}) {
  const { data } = await apiClient.get('/tenders/', { params });
  return {
    payload: data,
    results: unwrapResults(data),
  };
}

export async function fetchTenderById(id) {
  const { data } = await apiClient.get(`/tenders/${id}/`);
  return data;
}
