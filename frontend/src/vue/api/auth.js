import apiClient from "./client";
import { getRefreshToken, getUserUuid, unwrapResponse } from "./helpers";

export const authApi = {
  login(credentials) {
    return apiClient
      .post("/accounts/auth/login/", credentials)
      .then(unwrapResponse);
  },

  verifyOtp(payload) {
    return apiClient
      .post("/accounts/auth/otp/verify/", payload)
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
    const uuid = getUserUuid();
    if (!uuid) {
      return Promise.reject(new Error("No user session found."));
    }
    return apiClient.get(`/accounts/users/${uuid}/`).then(unwrapResponse);
  },

  updateProfile(uuid, payload) {
    return apiClient.patch(`/accounts/users/${uuid}/`, payload).then(unwrapResponse);
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
