import apiClient from "./client";
import { unwrapResponse } from "./helpers";

export const resultsApi = {
  list(params = {}) {
    return apiClient.get("/results/elections/", { params }).then(unwrapResponse);
  },

  get(electionUuid) {
    return apiClient.get(`/results/elections/${electionUuid}/`).then(unwrapResponse);
  },

  generate(electionUuid) {
    return apiClient.post(`/results/elections/${electionUuid}/generate/`).then(unwrapResponse);
  },

  preview(electionUuid) {
    return apiClient.get(`/results/elections/${electionUuid}/preview/`).then(unwrapResponse);
  },

  getIntegrity(electionUuid, params = {}) {
    return apiClient
      .get(`/results/elections/${electionUuid}/integrity/`, { params })
      .then(unwrapResponse);
  },

  certify(electionUuid, payload = {}) {
    return apiClient
      .post(`/results/elections/${electionUuid}/certify/`, payload)
      .then(unwrapResponse);
  },

  publish(electionUuid) {
    return apiClient.post(`/results/elections/${electionUuid}/publish/`).then(unwrapResponse);
  },

  archive(electionUuid) {
    return apiClient.post(`/results/elections/${electionUuid}/archive/`).then(unwrapResponse);
  },

  getCertificationQueue() {
    return apiClient.get("/results/certification-queue/").then(unwrapResponse);
  },

  getPublicationQueue() {
    return apiClient.get("/results/publication-queue/").then(unwrapResponse);
  },

  getArchiveQueue() {
    return apiClient.get("/results/archive-queue/").then(unwrapResponse);
  },

  getReport(electionUuid, format) {
    return apiClient
      .get(`/results/elections/${electionUuid}/reports/${format}/`)
      .then(unwrapResponse);
  },
};
