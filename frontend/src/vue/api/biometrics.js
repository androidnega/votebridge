import apiClient from "./client";
import { unwrapResponse } from "./helpers";

export const biometricsApi = {
  getEnrollmentRequirements() {
    return apiClient.get("/biometrics/enrollment/").then(unwrapResponse);
  },

  enroll(payload) {
    return apiClient.post("/biometrics/enrollment/", payload).then(unwrapResponse);
  },

  verifyLogin(payload) {
    return apiClient.post("/biometrics/verification/login/", payload).then(unwrapResponse);
  },

  verifyStepUp(payload) {
    return apiClient.post("/biometrics/verification/step-up/", payload).then(unwrapResponse);
  },

  requestChallenge(payload = {}) {
    return apiClient.post("/biometrics/challenge/", payload).then(unwrapResponse);
  },

  getStatus() {
    return apiClient.get("/biometrics/status/").then(unwrapResponse);
  },

  getSettings() {
    return apiClient.get("/biometrics/settings/").then(unwrapResponse);
  },

  getHistory(params = {}) {
    return apiClient.get("/biometrics/history/", { params }).then(unwrapResponse);
  },

  getSessionStatus() {
    return apiClient.get("/biometrics/session/status/").then(unwrapResponse);
  },

  validateSession(token) {
    return apiClient.post("/biometrics/session/validate/", { high_assurance_token: token }).then(unwrapResponse);
  },
};
