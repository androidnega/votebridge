/** Dev-only structured logging for biometric verification flow. */

const PREFIX = "[VoteBridge Bio]";

export function isBiometricDebugEnabled() {
  if (!import.meta.env.DEV) return false;
  try {
    return localStorage.getItem("vb_bio_debug") === "1";
  } catch {
    return false;
  }
}

export const bioDebug = {
  log(event, detail = {}) {
    if (!import.meta.env.DEV) return;
    console.info(PREFIX, event, detail);
  },
  warn(event, detail = {}) {
    if (!import.meta.env.DEV) return;
    console.warn(PREFIX, event, detail);
  },
  error(event, detail = {}) {
    if (!import.meta.env.DEV) return;
    console.error(PREFIX, event, detail);
  },
  metrics(event, detail = {}) {
    if (!isBiometricDebugEnabled()) return;
    console.info(PREFIX, event, detail);
  },
};
