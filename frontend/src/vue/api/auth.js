import apiClient from "./client";
import { getDeviceSignals, getRefreshToken, unwrapResponse } from "./helpers";

export const authApi = {
  login(credentials) {
    return apiClient
      .post("/accounts/auth/login/", credentials)
      .then(unwrapResponse);
  },

  verifyOtp(payload) {
    return apiClient
      .post("/accounts/auth/otp/verify/", {
        ...payload,
        device_signals: getDeviceSignals(),
      })
      .then(unwrapResponse);
  },

  resendOtp(payload) {
    return apiClient
      .post("/accounts/auth/otp/resend/", payload)
      .then(unwrapResponse);
  },

  refresh(refreshToken) {
    return apiClient
      .post("/accounts/auth/token/refresh/", { refresh: refreshToken })
      .then(unwrapResponse);
  },

  logout() {
    const refresh = getRefreshToken();
    return apiClient
      .post("/accounts/auth/logout/", { refresh })
      .then(unwrapResponse);
  },

  getProfile() {
    return apiClient.get("/accounts/auth/me/").then(unwrapResponse);
  },

  updateProfile(_uuid, payload) {
    return apiClient.patch("/accounts/auth/me/", payload).then(unwrapResponse);
  },

  listSessions() {
    return apiClient.get("/accounts/auth/sessions/").then(unwrapResponse);
  },

  revokeSession(sessionUuid) {
    return apiClient
      .post(`/accounts/auth/sessions/${sessionUuid}/revoke/`)
      .then(unwrapResponse);
  },
};
