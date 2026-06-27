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
};
