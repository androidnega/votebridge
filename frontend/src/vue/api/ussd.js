import apiClient from "./client";
import { unwrapResponse } from "./helpers";

export const ussdApi = {
  getIntegration() {
    return apiClient.get("/ussd/integration/").then(unwrapResponse);
  },

  getDashboard() {
    return apiClient.get("/ussd/dashboard/").then(unwrapResponse);
  },

  listSessions(params = {}) {
    return apiClient.get("/ussd/sessions/", { params }).then(unwrapResponse);
  },

  getSession(sessionUuid) {
    return apiClient.get(`/ussd/sessions/${sessionUuid}/`).then(unwrapResponse);
  },

  listLogs(params = {}) {
    return apiClient.get("/ussd/logs/", { params }).then(unwrapResponse);
  },
};
