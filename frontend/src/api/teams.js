import apiClient from './client';
import { apiEndpoints } from './endpoints';

export async function fetchTeamWorkspace(params = {}) {
  const { data } = await apiClient.get(apiEndpoints.teams.workspace, { params });
  return data;
}

export async function fetchTeamMembers(params = {}) {
  const { data } = await apiClient.get(apiEndpoints.teams.members, { params });
  return data;
}

export async function inviteTeamMember(payload) {
  const { data } = await apiClient.post(apiEndpoints.teams.members, payload);
  return data;
}

export async function revokeTeamMemberSessions(memberId) {
  const { data } = await apiClient.post(
    apiEndpoints.teams.revokeSessions(memberId),
  );
  return data;
}
