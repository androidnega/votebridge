import apiClient from "./client";
import { unwrapResponse } from "./helpers";

export const analyticsApi = {
  getOverview() {
    return apiClient.get("/analytics/overview/").then(unwrapResponse);
  },
  getElections() {
    return apiClient.get("/analytics/elections/").then(unwrapResponse);
  },
  getElectionLiveTrend(electionUuid) {
    return apiClient.get(`/analytics/elections/${electionUuid}/live-trend/`).then(unwrapResponse);
  },
  getElectionResultsAnalytics(electionUuid) {
    return apiClient
      .get(`/analytics/elections/${electionUuid}/results-analytics/`)
      .then(unwrapResponse);
  },
  getParticipation() {
    return apiClient.get("/analytics/participation/").then(unwrapResponse);
  },
  getDepartments() {
    return apiClient.get("/analytics/departments/").then(unwrapResponse);
  },
  getFaculties() {
    return apiClient.get("/analytics/faculties/").then(unwrapResponse);
  },
  getProgrammes() {
    return apiClient.get("/analytics/programmes/").then(unwrapResponse);
  },
  getStudents() {
    return apiClient.get("/analytics/students/").then(unwrapResponse);
  },
  getPersonal() {
    return apiClient.get("/analytics/personal/").then(unwrapResponse);
  },
  getSecurity() {
    return apiClient.get("/analytics/security/").then(unwrapResponse);
  },
  getFraud() {
    return apiClient.get("/analytics/fraud/").then(unwrapResponse);
  },
  getOperations() {
    return apiClient.get("/analytics/operations/").then(unwrapResponse);
  },
  getCommunications() {
    return apiClient.get("/analytics/communications/").then(unwrapResponse);
  },
  getUssd() {
    return apiClient.get("/analytics/ussd/").then(unwrapResponse);
  },
  getStrongroom() {
    return apiClient.get("/analytics/strongroom/").then(unwrapResponse);
  },
  getHistorical(period = "daily") {
    return apiClient.get("/analytics/historical/", { params: { period } }).then(unwrapResponse);
  },
  getReport(type, format = "json", params = {}) {
    return apiClient.get(`/analytics/reports/${type}/`, { params: { format, ...params } }).then(unwrapResponse);
  },
};
