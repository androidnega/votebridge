const ACCESS_TOKEN_KEY = "vb_access_token";
const REFRESH_TOKEN_KEY = "vb_refresh_token";
const USER_UUID_KEY = "vb_user_uuid";
const SESSION_UUID_KEY = "vb_session_uuid";
const DEVICE_FINGERPRINT_KEY = "vb_device_fingerprint";
const OTP_CHALLENGE_KEY = "vb_otp_challenge";

export function getAccessToken() {
  return localStorage.getItem(ACCESS_TOKEN_KEY);
}

export function getRefreshToken() {
  return localStorage.getItem(REFRESH_TOKEN_KEY);
}

export function getUserUuid() {
  return localStorage.getItem(USER_UUID_KEY);
}

export function getSessionUuid() {
  return localStorage.getItem(SESSION_UUID_KEY);
}

export function setTokens(access, refresh) {
  if (access) localStorage.setItem(ACCESS_TOKEN_KEY, access);
  if (refresh) localStorage.setItem(REFRESH_TOKEN_KEY, refresh);
}

export function setSessionMeta({ userUuid, sessionUuid } = {}) {
  if (userUuid) localStorage.setItem(USER_UUID_KEY, userUuid);
  if (sessionUuid) localStorage.setItem(SESSION_UUID_KEY, sessionUuid);
}

export function clearTokens() {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
}

export function clearSession() {
  clearTokens();
  localStorage.removeItem(USER_UUID_KEY);
  localStorage.removeItem(SESSION_UUID_KEY);
  sessionStorage.removeItem(OTP_CHALLENGE_KEY);
}

export function getOtpChallenge() {
  const raw = sessionStorage.getItem(OTP_CHALLENGE_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

export function setOtpChallenge(challenge) {
  sessionStorage.setItem(OTP_CHALLENGE_KEY, JSON.stringify(challenge));
}

export function clearOtpChallenge() {
  sessionStorage.removeItem(OTP_CHALLENGE_KEY);
}

export function getDeviceFingerprint() {
  let fingerprint = localStorage.getItem(DEVICE_FINGERPRINT_KEY);
  if (!fingerprint) {
    const parts = [
      navigator.userAgent,
      navigator.language,
      screen.width,
      screen.height,
      screen.colorDepth,
      Intl.DateTimeFormat().resolvedOptions().timeZone,
    ];
    fingerprint = parts.join("|");
    localStorage.setItem(DEVICE_FINGERPRINT_KEY, fingerprint);
  }
  return fingerprint;
}

export function extractApiError(error) {
  const data = error?.response?.data;
  if (data?.error?.message) return data.error.message;
  if (data?.errors && typeof data.errors === "object") {
    const first = Object.values(data.errors).flat()[0];
    if (first) return String(first);
  }
  return error?.message || "Request failed";
}

export function unwrapResponse(response) {
  const payload = response.data;
  if (payload && typeof payload === "object" && "success" in payload) {
    if (!payload.success) {
      throw new Error(payload.error?.message || "Request failed");
    }
    return payload.data;
  }
  return payload;
}
