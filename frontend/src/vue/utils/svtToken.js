/** Phase 59 — formatted Secure Voting Token (VB-XXXX-XXXX) + dev demo pool (VB-DEMO-####). */

const SVT_TOKEN_PATTERN = /^VB-[23456789ABCDEFGHJKMNPQRSTUVWXYZ]{4}-[23456789ABCDEFGHJKMNPQRSTUVWXYZ]{4}$/;
const DEMO_SVT_PATTERN = /^VB-DEMO-\d{4}$/;

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

export function normalizeDemoSvtToken(value) {
  const cleaned = String(value || "").trim().toUpperCase();
  const match = cleaned.match(/^VB-DEMO-(\d{4})$/);
  if (!match) return "";
  return `VB-DEMO-${match[1]}`;
}

export function isDemoSvtToken(value) {
  return DEMO_SVT_PATTERN.test(normalizeDemoSvtToken(value));
}

export function normalizeSvtToken(value) {
  const demo = normalizeDemoSvtToken(value);
  if (demo) return demo;
  const body = stripToBody(value);
  if (body.length !== 8) return "";
  return `VB-${body.slice(0, 4)}-${body.slice(4, 8)}`;
}

export function formatSvtTokenInput(value) {
  const demo = normalizeDemoSvtToken(value);
  if (demo) return demo;
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
  const normalized = normalizeSvtToken(value);
  if (!normalized) return false;
  if (isDemoSvtToken(normalized)) return true;
  return SVT_TOKEN_PATTERN.test(normalized);
}

export function looksLikePartialSvtToken(value) {
  if (normalizeDemoSvtToken(value)) return false;
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
  if (isDemoSvtToken(normalized)) {
    const [, , segment] = normalized.split("-");
    return ["VB", "DEMO", segment];
  }
  const [, first, second] = normalized.split("-");
  return ["VB", first, second];
}
