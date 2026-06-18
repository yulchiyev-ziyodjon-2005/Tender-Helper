import apiClient from './client';
import { apiEndpoints } from './endpoints';

export async function fetchCompanyProfile() {
  const { data } = await apiClient.get(apiEndpoints.companies.profile);
  return data;
}

export async function updateCompanyProfile(payload) {
  const { data } = await apiClient.patch(apiEndpoints.companies.profile, payload);
  return data;
}

export async function lookupCompanyRegistry(stir) {
  const { data } = await apiClient.post(apiEndpoints.companies.registryLookup, { stir });
  return data;
}

export async function confirmRegistryDraft(draftId, payload) {
  const { data } = await apiClient.post(
    apiEndpoints.companies.registryDraftConfirm(draftId),
    payload,
  );
  return data;
}

export async function skipStirOnboarding(payload) {
  const { data } = await apiClient.post(
    apiEndpoints.companies.skipStir,
    payload,
  );
  return data;
}
