/** Dev-only structured logging for biometric verification flow. */

const PREFIX = "[VoteBridge Bio]";

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
};
