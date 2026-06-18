/**
 * React escapes rendered strings by default. This helper additionally strips
 * markup/control characters before registry data is copied into editable inputs.
 */
export function sanitizePlainText(value, maxLength = 500) {
  if (value === null || value === undefined) return '';
  const withoutControls = Array.from(String(value))
    .filter((character) => {
      const code = character.codePointAt(0);
      return code === 9 || code === 10 || code === 13 || code > 31 && code !== 127;
    })
    .join('');
  return withoutControls
    .replace(/<[^>]*>/g, '')
    .trim()
    .slice(0, maxLength);
}

export function getApiError(error, fallback) {
  const data = error?.response?.data;
  if (typeof data?.message === 'string') return sanitizePlainText(data.message, 240);
  if (typeof data?.detail === 'string') return sanitizePlainText(data.detail, 240);
  if (typeof data?.error === 'string') return sanitizePlainText(data.error, 240);

  if (data && typeof data === 'object') {
    const first = Object.values(data).flat().find((item) => typeof item === 'string');
    if (first) return sanitizePlainText(first, 240);
  }
  return fallback;
}
