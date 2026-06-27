import { defineStore } from "pinia";
import { electionsApi } from "@/api";
import { extractApiError } from "@/api/helpers";

export const useElectionStore = defineStore("election", {
  state: () => ({
    elections: [],
    currentElection: null,
    filters: {
      search: "",
      status: "",
    },
    loading: false,
    error: null,
  }),

  getters: {
    activeElections: (state) =>
      state.elections.filter((item) => ["open", "paused"].includes(item.status)),
  },

  actions: {
    async fetchElections(params = {}) {
      this.loading = true;
      this.error = null;
      try {
        const query = {
          search: this.filters.search || undefined,
          status: this.filters.status || undefined,
          ...params,
        };
        const result = await electionsApi.list(query);
        this.elections = result.items;
        return result;
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async fetchElection(uuid) {
      this.loading = true;
      this.error = null;
      try {
        this.currentElection = await electionsApi.get(uuid);
        return this.currentElection;
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    setFilters(filters) {
      this.filters = { ...this.filters, ...filters };
    },

    clearCurrent() {
      this.currentElection = null;
    },
  },
});
