import apiClient from './client';

function unwrapResults(payload) {
  return Array.isArray(payload) ? payload : (payload.results || []);
}

export async function startAnalysis(lotId, payload = {}) {
  const { data } = await apiClient.post('/analysis/start/', {
    lot_id: lotId,
    ...payload,
  });
  return data;
}

export async function fetchAnalysisHistory(params = {}) {
  const { data } = await apiClient.get('/analysis/history/', { params });
  return {
    payload: data,
    results: unwrapResults(data),
  };
}

export async function fetchAnalysisStatus(statusUrl) {
  const { data } = await apiClient.get(statusUrl);
  return data;
}

export async function fetchAnalysisResult(resultUrl) {
  const { data } = await apiClient.get(resultUrl);
  return data;
}

export async function calculateAnalysis(analysisId, payload) {
  const { data } = await apiClient.post(
    `/analysis/${analysisId}/calculate/`,
    payload,
  );
  return data;
}
