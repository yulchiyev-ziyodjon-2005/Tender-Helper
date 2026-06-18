import apiClient from './client';

export async function fetchCompanyProfile() {
  const { data } = await apiClient.get('/companies/profile/');
  return data;
}

export async function updateCompanyProfile(payload) {
  const { data } = await apiClient.patch('/companies/profile/', payload);
  return data;
}

export async function lookupCompanyRegistry(stir) {
  const { data } = await apiClient.post('/companies/registry/lookup/', { stir });
  return data;
}

export async function confirmRegistryDraft(draftId, payload) {
  const { data } = await apiClient.post(
    `/companies/registry/drafts/${draftId}/confirm/`,
    payload,
  );
  return data;
}

export async function skipStirOnboarding(payload) {
  const { data } = await apiClient.post(
    '/companies/onboarding/skip-stir/',
    payload,
  );
  return data;
}
