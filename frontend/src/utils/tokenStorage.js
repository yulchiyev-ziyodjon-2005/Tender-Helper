const ACCESS_TOKEN_KEY = 'access_token';
const REFRESH_TOKEN_KEY = 'refresh_token';
const SESSION_MODE_KEY = 'tenderhelper_session_mode';
const PASSWORD_CHANGE_KEY = 'tenderhelper_password_change_required';

function activeStorage() {
  return localStorage.getItem(SESSION_MODE_KEY) === 'persistent'
    ? localStorage
    : sessionStorage;
}

export function getAccessToken() {
  return sessionStorage.getItem(ACCESS_TOKEN_KEY)
    || localStorage.getItem(ACCESS_TOKEN_KEY);
}

export function getRefreshToken() {
  return sessionStorage.getItem(REFRESH_TOKEN_KEY)
    || localStorage.getItem(REFRESH_TOKEN_KEY);
}

export function hasStoredSession() {
  return Boolean(getAccessToken() && getRefreshToken());
}

export function requiresStoredPasswordChange() {
  return sessionStorage.getItem(PASSWORD_CHANGE_KEY) === 'true'
    || localStorage.getItem(PASSWORD_CHANGE_KEY) === 'true';
}

export function storeTokens(tokens, persistent = false, requiresPasswordChange = false) {
  clearTokens();
  const storage = persistent ? localStorage : sessionStorage;
  storage.setItem(ACCESS_TOKEN_KEY, tokens.access);
  storage.setItem(REFRESH_TOKEN_KEY, tokens.refresh);
  storage.setItem(PASSWORD_CHANGE_KEY, String(requiresPasswordChange));
  localStorage.setItem(SESSION_MODE_KEY, persistent ? 'persistent' : 'session');
}

export function updateTokens(tokens) {
  const storage = activeStorage();
  if (tokens.access) storage.setItem(ACCESS_TOKEN_KEY, tokens.access);
  if (tokens.refresh) storage.setItem(REFRESH_TOKEN_KEY, tokens.refresh);
}

export function clearTokens() {
  [localStorage, sessionStorage].forEach((storage) => {
    storage.removeItem(ACCESS_TOKEN_KEY);
    storage.removeItem(REFRESH_TOKEN_KEY);
    storage.removeItem(PASSWORD_CHANGE_KEY);
  });
  localStorage.removeItem(SESSION_MODE_KEY);
}
