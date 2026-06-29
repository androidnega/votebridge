import apiClient from "./client";
import { unwrapPaginatedList } from "./pagination";
import { unwrapResponse } from "./helpers";

export const electionsApi = {
  list(params = {}) {
    return apiClient.get("/elections/", { params }).then(unwrapPaginatedList);
  },

  get(uuid) {
    return apiClient.get(`/elections/${uuid}/`).then(unwrapResponse);
  },

  create(payload) {
    return apiClient.post("/elections/", payload).then(unwrapResponse);
  },

  update(uuid, payload) {
    return apiClient.patch(`/elections/${uuid}/`, payload).then(unwrapResponse);
  },

  delete(uuid) {
    return apiClient.delete(`/elections/${uuid}/`);
  },

  schedule(uuid) {
    return apiClient.post(`/elections/${uuid}/schedule/`).then(unwrapResponse);
  },

  open(uuid) {
    return apiClient.post(`/elections/${uuid}/open/`).then(unwrapResponse);
  },

  getReadiness(uuid) {
    return apiClient.get(`/elections/${uuid}/readiness/`).then(unwrapResponse);
  },

  pause(uuid) {
    return apiClient.post(`/elections/${uuid}/pause/`).then(unwrapResponse);
  },

  close(uuid) {
    return apiClient.post(`/elections/${uuid}/close/`).then(unwrapResponse);
  },

  archive(uuid) {
    return apiClient.post(`/elections/${uuid}/archive/`).then(unwrapResponse);
  },

  listPositions(electionUuid, params = {}) {
    return apiClient
      .get(`/elections/${electionUuid}/positions/`, { params })
      .then(unwrapPaginatedList);
  },

  listCandidates(electionUuid, params = {}) {
    return apiClient
      .get(`/elections/${electionUuid}/candidates/`, { params })
      .then(unwrapPaginatedList);
  },

  createPosition(electionUuid, payload) {
    return apiClient
      .post(`/elections/${electionUuid}/positions/`, payload)
      .then(unwrapResponse);
  },

  updatePosition(electionUuid, positionUuid, payload) {
    return apiClient
      .patch(`/elections/${electionUuid}/positions/${positionUuid}/`, payload)
      .then(unwrapResponse);
  },

  deletePosition(electionUuid, positionUuid) {
    return apiClient.delete(`/elections/${electionUuid}/positions/${positionUuid}/`);
  },

  createCandidate(electionUuid, payload) {
    return apiClient
      .post(`/elections/${electionUuid}/candidates/`, payload)
      .then(unwrapResponse);
  },

  updateCandidate(electionUuid, candidateUuid, payload) {
    return apiClient
      .patch(`/elections/${electionUuid}/candidates/${candidateUuid}/`, payload)
      .then(unwrapResponse);
  },

  deleteCandidate(electionUuid, candidateUuid) {
    return apiClient.delete(`/elections/${electionUuid}/candidates/${candidateUuid}/`);
  },

  approveCandidate(electionUuid, candidateUuid) {
    return apiClient
      .post(`/elections/${electionUuid}/candidates/${candidateUuid}/approve/`)
      .then(unwrapResponse);
  },

  rejectCandidate(electionUuid, candidateUuid) {
    return apiClient
      .post(`/elections/${electionUuid}/candidates/${candidateUuid}/reject/`)
      .then(unwrapResponse);
  },

  listEligibility(electionUuid, params = {}) {
    return apiClient
      .get(`/elections/${electionUuid}/eligibility/`, { params })
      .then(unwrapPaginatedList);
  },

  createEligibility(electionUuid, payload) {
    return apiClient
      .post(`/elections/${electionUuid}/eligibility/`, payload)
      .then(unwrapResponse);
  },

  updateEligibility(electionUuid, recordUuid, payload) {
    return apiClient
      .patch(`/elections/${electionUuid}/eligibility/${recordUuid}/`, payload)
      .then(unwrapResponse);
  },

  deleteEligibility(electionUuid, recordUuid) {
    return apiClient.delete(`/elections/${electionUuid}/eligibility/${recordUuid}/`);
  },

  bulkEligibility(electionUuid, payload) {
    return apiClient
      .post(`/elections/${electionUuid}/eligibility/bulk/`, payload)
      .then(unwrapResponse);
  },

  createCandidateWithImage(electionUuid, payload, imageFile) {
    const form = new FormData();
    Object.entries(payload).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== "") {
        form.append(key, value);
      }
    });
    if (imageFile) form.append("image", imageFile);
    return apiClient
      .post(`/elections/${electionUuid}/candidates/`, form, {
        headers: { "Content-Type": "multipart/form-data" },
      })
      .then(unwrapResponse);
  },

  updateCandidateWithImage(electionUuid, candidateUuid, payload, imageFile) {
    const form = new FormData();
    Object.entries(payload).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== "") {
        form.append(key, value);
      }
    });
    if (imageFile) form.append("image", imageFile);
    return apiClient
      .patch(`/elections/${electionUuid}/candidates/${candidateUuid}/`, form, {
        headers: { "Content-Type": "multipart/form-data" },
      })
      .then(unwrapResponse);
  },
};
