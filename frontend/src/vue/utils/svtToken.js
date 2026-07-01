/** Phase 56 — six-digit Secure Voting Token. */
const SVT_TOKEN_PATTERN = /^\d{6}$/;

export function normalizeSvtToken(value) {
  return String(value || "").replace(/\D/g, "").slice(0, 6);
}

export function isValidSvtToken(value) {
  return SVT_TOKEN_PATTERN.test(normalizeSvtToken(value));
}

export function looksLikePartialSvtToken(value) {
  const normalized = normalizeSvtToken(value);
  return normalized.length > 0 && normalized.length < 6;
}

export function formatSvtTokenInput(value) {
  return normalizeSvtToken(value);
}
