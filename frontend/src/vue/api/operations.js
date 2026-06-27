import apiClient from "./client";
import { unwrapResponse } from "./helpers";

export const operationsApi = {
  getOverview() {
    return apiClient.get("/operations/overview/").then(unwrapResponse);
  },

  getActivity(params = {}) {
    return apiClient.get("/operations/activity/", { params }).then(unwrapResponse);
  },

  getHealth() {
    return apiClient.get("/operations/health/").then(unwrapResponse);
  },

  getInfrastructure() {
    return apiClient.get("/operations/infrastructure/").then(unwrapResponse);
  },

  getElectionMonitor() {
    return apiClient.get("/operations/elections/").then(unwrapResponse);
  },

  getSessions() {
    return apiClient.get("/operations/sessions/").then(unwrapResponse);
  },

  getCommunications() {
    return apiClient.get("/operations/communications/").then(unwrapResponse);
  },

  getQueues() {
    return apiClient.get("/operations/queues/").then(unwrapResponse);
  },

  getPerformance() {
    return apiClient.get("/operations/performance/").then(unwrapResponse);
  },

  getLogs(params = {}) {
    return apiClient.get("/operations/logs/", { params }).then(unwrapResponse);
  },
};
