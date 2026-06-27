import axios from "axios";
import {
  clearSession,
  getAccessToken,
  getDeviceFingerprint,
  getRefreshToken,
  setTokens,
} from "./helpers";

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "/api/v1",
  withCredentials: true,
  headers: {
    Accept: "application/json",
  },
});

let refreshPromise = null;

apiClient.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  config.headers["X-Device-Fingerprint"] = getDeviceFingerprint();

  const isFormData = typeof FormData !== "undefined" && config.data instanceof FormData;
  if (!isFormData && !config.headers["Content-Type"]) {
    config.headers["Content-Type"] = "application/json";
  }

  return config;
});

async function refreshAccessToken() {
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
    return true;
  } catch {
    clearSession();
    return false;
  }
}

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (!originalRequest || originalRequest._retry) {
      return Promise.reject(error);
    }

    if (error.response?.status === 401 && getRefreshToken()) {
      originalRequest._retry = true;
      refreshPromise = refreshPromise || refreshAccessToken();
      const refreshed = await refreshPromise;
      refreshPromise = null;

      if (refreshed) {
        originalRequest.headers.Authorization = `Bearer ${getAccessToken()}`;
        return apiClient(originalRequest);
      }
    }

    return Promise.reject(error);
  }
);

export default apiClient;
