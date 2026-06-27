import apiClient from "./client";
import { unwrapResponse } from "./helpers";

export const securityApi = {
  requestSvt(electionUuid) {
    return apiClient
      .post(`/security/elections/${electionUuid}/svt/request/`)
      .then(unwrapResponse);
  },

  validateSvt(electionUuid, tokenCode) {
    return apiClient
      .post(`/security/elections/${electionUuid}/svt/validate/`, {
        token_code: tokenCode,
      })
      .then(unwrapResponse);
  },

  verifySvt(tokenCode) {
    return apiClient
      .post("/security/svt/verify/", { token_code: tokenCode })
      .then(unwrapResponse);
  },

  getMonitoringSummary() {
    return apiClient.get("/security/monitoring/summary/").then(unwrapResponse);
  },

  listAuditLogs(params = {}) {
    return apiClient
      .get("/security/monitoring/audit-logs/", { params })
      .then(unwrapResponse);
  },

  listDevices(params = {}) {
    return apiClient
      .get("/security/monitoring/devices/", { params })
      .then(unwrapResponse);
  },

  listLocations(params = {}) {
    return apiClient
      .get("/security/monitoring/locations/", { params })
      .then(unwrapResponse);
  },

  getSecurityFeed() {
    return apiClient.get("/dashboard/security-feed/").then(unwrapResponse);
  },
};
