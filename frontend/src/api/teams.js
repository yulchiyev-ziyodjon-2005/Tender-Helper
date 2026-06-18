import apiClient from './client';

export async function fetchTeamWorkspace(params = {}) {
  const { data } = await apiClient.get('/teams/workspace/', { params });
  return data;
}

export async function fetchTeamMembers(params = {}) {
  const { data } = await apiClient.get('/teams/members/', { params });
  return data;
}

export async function inviteTeamMember(payload) {
  const { data } = await apiClient.post('/teams/members/', payload);
  return data;
}

export async function revokeTeamMemberSessions(memberId) {
  const { data } = await apiClient.post(
    `/teams/members/${memberId}/revoke-sessions/`,
  );
  return data;
}
