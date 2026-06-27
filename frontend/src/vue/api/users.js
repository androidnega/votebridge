import apiClient from "./client";
import { unwrapPaginatedList } from "./pagination";

export const usersApi = {
  list(params = {}) {
    return apiClient.get("/accounts/users/", { params }).then(unwrapPaginatedList);
  },
};
