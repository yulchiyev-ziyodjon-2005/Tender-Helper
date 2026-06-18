import { apiEndpoints, asApiV1Path } from '../src/api/endpoints.js';

const apiBaseUrl = resolveBaseUrl();
const originUrl = new URL(apiBaseUrl).origin;
const email = process.env.API_CONTRACT_EMAIL || '';
const password = process.env.API_CONTRACT_PASSWORD || '';

const checks = [];

function stripTrailingSlash(value) {
  return String(value).replace(/\/+$/, '');
}

function resolveBaseUrl() {
  const explicit = process.env.API_CONTRACT_API_BASE_URL || '';
  if (explicit) {
    return requireAbsoluteUrl(explicit, 'API_CONTRACT_API_BASE_URL');
  }

  const viteBase = process.env.VITE_API_BASE_URL || '';
  if (viteBase && /^https?:\/\//i.test(viteBase)) {
    return requireAbsoluteUrl(viteBase, 'VITE_API_BASE_URL');
  }

  const origin = process.env.API_CONTRACT_ORIGIN || 'http://127.0.0.1:8000';
  const originUrl = requireAbsoluteUrl(origin, 'API_CONTRACT_ORIGIN');
  return `${stripTrailingSlash(originUrl)}/api/v1`;
}

function requireAbsoluteUrl(value, name) {
  try {
    return stripTrailingSlash(new URL(value).toString());
  } catch (error) {
    throw new Error(
      `${name} must be an absolute http(s) URL, got: ${value}. ` +
      `Use API_CONTRACT_ORIGIN=http://127.0.0.1:8000 or API_CONTRACT_API_BASE_URL=https://host/api/v1.`,
    );
  }
}

function urlFor(path) {
  if (path.startsWith('/api/health/')) {
    return `${originUrl}${path}`;
  }
  return `${apiBaseUrl}${path}`;
}

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

function isObject(value) {
  return value !== null && typeof value === 'object' && !Array.isArray(value);
}

async function readJson(response) {
  const text = await response.text();
  if (!text) return null;
  try {
    return JSON.parse(text);
  } catch (error) {
    throw new Error(`Expected JSON from ${response.url}, got: ${text.slice(0, 120)}`);
  }
}

async function request(name, path, options = {}) {
  const response = await fetch(urlFor(path), {
    headers: {
      Accept: 'application/json',
      ...(options.body ? { 'Content-Type': 'application/json' } : {}),
      ...(options.token ? { Authorization: `Bearer ${options.token}` } : {}),
      ...(options.headers || {}),
    },
    method: options.method || 'GET',
    body: options.body ? JSON.stringify(options.body) : undefined,
    redirect: options.redirect || 'manual',
  });
  const data = await readJson(response);
  checks.push({ name, status: response.status });
  return { response, data };
}

function assertErrorEnvelope(data, context) {
  assert(isObject(data), `${context}: error response must be an object`);
  assert(
    typeof data.code === 'string'
    || typeof data.error_code === 'string'
    || typeof data.error === 'string',
    `${context}: error response must expose code/error_code/error`,
  );
  assert(
    typeof data.message === 'string'
    || typeof data.detail === 'string',
    `${context}: error response must expose message/detail`,
  );
}

function assertPaginatedOrArray(data, context) {
  if (Array.isArray(data)) return;
  assert(isObject(data), `${context}: response must be an array or paginated object`);
  assert(Array.isArray(data.results), `${context}: paginated response must include results[]`);
  assert(
    typeof data.count === 'number'
    || data.next === null
    || typeof data.next === 'string',
    `${context}: paginated response must include count/next metadata`,
  );
}

async function checkPublicContract() {
  const health = await request('health', apiEndpoints.health);
  assert(health.response.status === 200, 'health must return HTTP 200');
  assert(health.data?.status === 'ok', 'health.status must be ok');

  const tenders = await request('tenders.list.public', apiEndpoints.tenders.list);
  assert(tenders.response.status === 200, 'public tender list must return HTTP 200');
  assertPaginatedOrArray(tenders.data, 'public tender list');

  const google = await request('auth.googleConfig.public', apiEndpoints.auth.googleConfig);
  assert(google.response.status === 200, 'Google config must return HTTP 200');
  assert(typeof google.data?.enabled === 'boolean', 'Google config must expose enabled boolean');
  assert(typeof google.data?.start_url === 'string', 'Google config must expose start_url');
}

async function checkAuthGuardContract() {
  const protectedGets = [
    ['auth.me.unauthenticated', apiEndpoints.auth.me],
    ['auth.session.unauthenticated', apiEndpoints.auth.session],
    ['companies.profile.unauthenticated', apiEndpoints.companies.profile],
    ['subscriptions.entitlements.unauthenticated', apiEndpoints.subscriptions.entitlements],
    ['teams.workspace.unauthenticated', apiEndpoints.teams.workspace],
    ['admin.overview.unauthenticated', apiEndpoints.admin.overview],
  ];

  for (const [name, path] of protectedGets) {
    const result = await request(name, path);
    assert(result.response.status === 401, `${name} must return HTTP 401 without token`);
    assertErrorEnvelope(result.data, name);
  }

  const invalidLogin = await request('auth.login.invalid', apiEndpoints.auth.login, {
    method: 'POST',
    body: { email: 'missing@example.invalid', password: 'not-a-real-password' },
  });
  assert([400, 401].includes(invalidLogin.response.status), 'invalid login must return 400/401');
  assertErrorEnvelope(invalidLogin.data, 'invalid login');
}

async function checkAuthenticatedContract() {
  if (!email && !password) {
    console.log('Skipping authenticated contract checks: set API_CONTRACT_EMAIL and API_CONTRACT_PASSWORD.');
    return;
  }
  assert(
    Boolean(email) && Boolean(password),
    'API_CONTRACT_EMAIL and API_CONTRACT_PASSWORD must be provided together.',
  );

  const login = await request('auth.login.valid', apiEndpoints.auth.login, {
    method: 'POST',
    body: { email, password },
  });
  assert(login.response.status === 200, 'valid login must return HTTP 200');
  assert(typeof login.data?.tokens?.access === 'string', 'login must return tokens.access');
  assert(typeof login.data?.tokens?.refresh === 'string', 'login must return tokens.refresh');
  assert(isObject(login.data?.user), 'login must return user object');
  assert(typeof login.data.force_password_change === 'boolean', 'login must expose force_password_change');

  const token = login.data.tokens.access;
  const session = await request('auth.session.authenticated', apiEndpoints.auth.session, { token });
  assert(session.response.status === 200, 'authenticated session must return HTTP 200');
  assert(isObject(session.data), 'session payload must be an object');

  const profile = await request('companies.profile.authenticated', apiEndpoints.companies.profile, { token });
  assert([200, 404].includes(profile.response.status), 'company profile must return 200 or profile_not_found');
  if (profile.response.status === 200) {
    assert(typeof profile.data.company_name === 'string', 'company profile must expose company_name');
  } else {
    assertErrorEnvelope(profile.data, 'company profile missing');
  }

  const entitlements = await request(
    'subscriptions.entitlements.authenticated',
    apiEndpoints.subscriptions.entitlements,
    { token },
  );
  assert([200, 400].includes(entitlements.response.status), 'entitlements must return 200 or profile_required');
  if (entitlements.response.status === 200) {
    assert(typeof entitlements.data.plan === 'string', 'entitlements must expose plan');
    assert(Array.isArray(entitlements.data.entitlements), 'entitlements must expose entitlements[]');
  } else {
    assertErrorEnvelope(entitlements.data, 'entitlements profile_required');
  }

  const team = await request('teams.workspace.authenticated', apiEndpoints.teams.workspace, { token });
  assert([200, 404].includes(team.response.status), 'team workspace must return 200 or company_required');
  if (team.response.status === 200) {
    assert(isObject(team.data.company), 'team workspace must expose company object');
    assert(isObject(team.data.membership), 'team workspace must expose membership object');
  } else {
    assertErrorEnvelope(team.data, 'team workspace company_required');
  }

  const admin = await request('admin.overview.authenticated', apiEndpoints.admin.overview, { token });
  assert([200, 403].includes(admin.response.status), 'admin overview must return 200 or permission/MFA denied');
  if (admin.response.status === 403) assertErrorEnvelope(admin.data, 'admin overview denied');
}

async function main() {
  console.log(`API contract smoke target: ${apiBaseUrl}`);
  assert(
    asApiV1Path(apiEndpoints.auth.login) === '/api/v1/auth/login/',
    'endpoint registry must map auth.login to canonical API v1 path',
  );
  assert(
    apiBaseUrl.startsWith('http://') || apiBaseUrl.startsWith('https://'),
    'API contract smoke requires an absolute http(s) base URL',
  );
  await checkPublicContract();
  await checkAuthGuardContract();
  await checkAuthenticatedContract();

  for (const check of checks) {
    console.log(`${String(check.status).padEnd(3)} ${check.name}`);
  }
  console.log(`API contract smoke passed (${checks.length} checks).`);
}

main().catch((error) => {
  console.error(error.message);
  process.exitCode = 1;
});
