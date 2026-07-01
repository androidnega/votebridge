/** Phase 59 — formatted Secure Voting Token (VB-XXXX-XXXX). */

const SVT_TOKEN_PATTERN = /^VB-[23456789ABCDEFGHJKMNPQRSTUVWXYZ]{4}-[23456789ABCDEFGHJKMNPQRSTUVWXYZ]{4}$/;

function stripToBody(value) {
  let cleaned = String(value || "")
    .replace(/[^A-Za-z0-9]/g, "")
    .toUpperCase();
  if (cleaned.startsWith("SVT")) {
    cleaned = cleaned.slice(3);
  } else if (cleaned.startsWith("VB")) {
    cleaned = cleaned.slice(2);
  }
  return cleaned.slice(0, 8);
}

export function normalizeSvtToken(value) {
  const body = stripToBody(value);
  if (body.length !== 8) return "";
  return `VB-${body.slice(0, 4)}-${body.slice(4, 8)}`;
}

export function formatSvtTokenInput(value) {
  const body = stripToBody(value);
  if (!body.length) return "";
  let formatted = "VB";
  formatted += `-${body.slice(0, 4)}`;
  if (body.length > 4) {
    formatted += `-${body.slice(4, 8)}`;
  }
  return formatted;
}

export function isValidSvtToken(value) {
  return SVT_TOKEN_PATTERN.test(normalizeSvtToken(value));
}

export function looksLikePartialSvtToken(value) {
  const body = stripToBody(value);
  return body.length > 0 && body.length < 8;
}

export function svtTokenSegments(value) {
  const normalized = normalizeSvtToken(value);
  if (!normalized) {
    const partial = formatSvtTokenInput(value);
    const parts = partial.split("-");
    return [parts[0] || "VB", parts[1] || "", parts[2] || ""];
  }
  const [, first, second] = normalized.split("-");
  return ["VB", first, second];
}
