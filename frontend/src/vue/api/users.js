import apiClient from "./client";
import { unwrapResponse } from "./helpers";
import { unwrapPaginatedList } from "./pagination";

export const usersApi = {
  list(params = {}) {
    return apiClient.get("/accounts/users/", { params }).then(unwrapPaginatedList);
  },

  create(payload) {
    return apiClient.post("/accounts/users/", payload).then(unwrapResponse);
  },

  activate(uuid) {
    return apiClient.post(`/accounts/users/${uuid}/activate/`).then(unwrapResponse);
  },

  deactivate(uuid) {
    return apiClient.post(`/accounts/users/${uuid}/deactivate/`).then(unwrapResponse);
  },

  unverify(uuid) {
    return apiClient.post(`/accounts/users/${uuid}/unverify/`).then(unwrapResponse);
  },
};
