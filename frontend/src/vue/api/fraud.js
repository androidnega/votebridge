import apiClient from "./client";
import { unwrapResponse } from "./helpers";

export const fraudApi = {
  listAlerts(params = {}) {
    return apiClient.get("/fraud/alerts/", { params }).then(unwrapResponse);
  },

  getAlert(alertId) {
    return apiClient.get(`/fraud/alerts/${alertId}/`).then(unwrapResponse);
  },

  reviewAlert(alertId) {
    return apiClient.post(`/fraud/alerts/${alertId}/review/`).then(unwrapResponse);
  },

  resolveAlert(alertId) {
    return apiClient.post(`/fraud/alerts/${alertId}/resolve/`).then(unwrapResponse);
  },

  escalateAlert(alertId) {
    return apiClient.post(`/fraud/alerts/${alertId}/escalate/`).then(unwrapResponse);
  },

  listCases(params = {}) {
    return apiClient.get("/fraud/cases/", { params }).then(unwrapResponse);
  },

  getCase(fraudCaseId) {
    return apiClient.get(`/fraud/cases/${fraudCaseId}/`).then(unwrapResponse);
  },

  getIntegrityReport(params = {}) {
    return apiClient
      .get("/fraud/integrity-report/", { params })
      .then(unwrapResponse);
  },

  getTimeline(fraudCaseId) {
    return apiClient
      .get(`/fraud/cases/${fraudCaseId}/timeline/`)
      .then(unwrapResponse);
  },

  getFraudFeed() {
    return apiClient.get("/dashboard/fraud-feed/").then(unwrapResponse);
  },
};
