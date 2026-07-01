import axios from "axios";
import {
  clearSession,
  getAccessToken,
  getDeviceFingerprint,
  getRefreshToken,
  isAccessTokenExpired,
  setTokens,
} from "./helpers";
import { bioDebug } from "@/utils/biometricDebug";

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "/api/v1",
  withCredentials: true,
  headers: {
    Accept: "application/json",
  },
});

let refreshPromise = null;

/** Pending-auth biometric endpoints use pending_auth_token — not JWT. */
const PENDING_AUTH_PATHS = ["/biometrics/verification/login/", "/biometrics/challenge/"];

/** Auth endpoints that must not trigger JWT refresh or attach stale tokens. */
const PUBLIC_AUTH_PATHS = [
  "/accounts/auth/login/",
  "/accounts/auth/otp/",
  "/accounts/auth/token/refresh/",
  "/accounts/auth/forgot-password/",
  "/accounts/auth/reset-password/",
];

function isPendingAuthRequest(config) {
  if (config?.skipAuth) return true;
  const url = config?.url || "";
  return PENDING_AUTH_PATHS.some((path) => url.includes(path));
}

function isPublicAuthRequest(config) {
  const url = config?.url || "";
  return PUBLIC_AUTH_PATHS.some((path) => url.includes(path));
}

function requiresAuth(config) {
  return !isPendingAuthRequest(config) && !isPublicAuthRequest(config);
}

export async function refreshAccessToken() {
  if (refreshPromise) {
    return refreshPromise;
  }

  refreshPromise = (async () => {
    const refresh = getRefreshToken();
    if (!refresh) {
      clearSession();
      return false;
    }

    try {
      const response = await axios.post(
        `${apiClient.defaults.baseURL}/accounts/auth/token/refresh/`,
        { refresh },
        { headers: { "Content-Type": "application/json" } }
      );
      const data = response.data?.data || response.data;
      setTokens(data?.access, data?.refresh);
      return Boolean(data?.access);
    } catch {
      clearSession();
      return false;
    } finally {
      refreshPromise = null;
    }
  })();

  return refreshPromise;
}

/** Refresh when the access token is missing or expired before the first protected API call. */
export async function ensureAccessToken() {
  if (getAccessToken() && !isAccessTokenExpired()) {
    return true;
  }
  return refreshAccessToken();
}

apiClient.interceptors.request.use(async (config) => {
  if (requiresAuth(config)) {
    await ensureAccessToken();
    const token = getAccessToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    } else {
      delete config.headers.Authorization;
    }
  } else if (!isPendingAuthRequest(config)) {
    delete config.headers.Authorization;
  }

  config.headers["X-Device-Fingerprint"] = getDeviceFingerprint();

  const isFormData = typeof FormData !== "undefined" && config.data instanceof FormData;
  if (!isFormData && !config.headers["Content-Type"]) {
    config.headers["Content-Type"] = "application/json";
  }

  if (import.meta.env.DEV && config.url?.includes("/biometrics/verification/login/")) {
    bioDebug.log("verification_request_started", {
      hasPendingToken: Boolean(config.data?.pending_auth_token),
      challengeId: config.data?.challenge_id,
      frameCount: config.data?.frames?.length ?? 0,
      skipAuth: isPendingAuthRequest(config),
    });
  }

  return config;
});

apiClient.interceptors.response.use(
  (response) => {
    if (import.meta.env.DEV && response.config?.url?.includes("/biometrics/verification/login/")) {
      bioDebug.log("verification_request_finished", { status: response.status });
    }
    return response;
  },
  async (error) => {
    const originalRequest = error.config;

    if (import.meta.env.DEV && originalRequest?.url?.includes("/biometrics/verification/login/")) {
      bioDebug.error("verification_request_finished", {
        status: error.response?.status,
        code: error.response?.data?.error?.code,
        message: error.response?.data?.error?.message,
      });
    }

    if (!originalRequest || originalRequest._retry) {
      return Promise.reject(error);
    }

    // Biometric verify 401 = verification failed (challenge_failed, etc.), not JWT expiry.
    if (isPendingAuthRequest(originalRequest) || isPublicAuthRequest(originalRequest)) {
      return Promise.reject(error);
    }

    if (error.response?.status === 401 && getRefreshToken()) {
      originalRequest._retry = true;
      const refreshed = await refreshAccessToken();

      if (refreshed) {
        originalRequest.headers.Authorization = `Bearer ${getAccessToken()}`;
        return apiClient(originalRequest);
      }
    }

    if (error.response?.status === 401) {
      clearSession();
      try {
        const { useAuthStore } = await import("@/stores/auth");
        const authStore = useAuthStore();
        authStore.user = null;
        authStore.initialized = true;
        authStore.initializePromise = null;
      } catch {
        /* Pinia may not be ready during bootstrap */
      }
    }

    return Promise.reject(error);
  }
);

export default apiClient;
