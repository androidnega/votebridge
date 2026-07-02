import { defineStore } from "pinia";
import { electionsApi } from "@/api";
import { extractApiError } from "@/api/helpers";

export const useElectionStore = defineStore("election", {
  state: () => ({
    elections: [],
    currentElection: null,
    readinessReport: null,
    filters: {
      search: "",
      status: "",
    },
    loading: false,
    readinessLoading: false,
    actionLoading: false,
    pendingLifecycleAction: null,
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
      this.readinessReport = null;
    },

    async fetchReadiness(uuid) {
      this.readinessLoading = true;
      this.error = null;
      try {
        this.readinessReport = await electionsApi.getReadiness(uuid);
        return this.readinessReport;
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.readinessLoading = false;
      }
    },

    async openElection(uuid) {
      this.actionLoading = true;
      this.error = null;
      try {
        this.currentElection = await electionsApi.open(uuid);
        this.readinessReport = null;
        return this.currentElection;
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.actionLoading = false;
      }
    },

    async createElection(payload) {
      this.actionLoading = true;
      this.error = null;
      try {
        const election = await electionsApi.create(payload);
        this.elections = [election, ...this.elections];
        return election;
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.actionLoading = false;
      }
    },

    async updateElection(uuid, payload) {
      this.actionLoading = true;
      this.error = null;
      try {
        const election = await electionsApi.update(uuid, payload);
        this.currentElection = election;
        return election;
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.actionLoading = false;
      }
    },

    async scheduleElection(uuid) {
      return this._lifecycle(uuid, () => electionsApi.schedule(uuid));
    },

    async pauseElection(uuid) {
      return this._lifecycle(uuid, () => electionsApi.pause(uuid));
    },

    async closeElection(uuid) {
      return this._lifecycle(uuid, () => electionsApi.close(uuid));
    },

    async archiveElection(uuid) {
      return this._lifecycle(uuid, () => electionsApi.archive(uuid));
    },

    async deleteElection(uuid) {
      this.actionLoading = true;
      this.error = null;
      try {
        await electionsApi.delete(uuid);
        this.elections = this.elections.filter((item) => item.uuid !== uuid);
        if (this.currentElection?.uuid === uuid) {
          this.currentElection = null;
          this.readinessReport = null;
        }
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.actionLoading = false;
      }
    },

    setPendingLifecycleAction(action) {
      this.pendingLifecycleAction = action;
    },

    clearPendingLifecycleAction() {
      this.pendingLifecycleAction = null;
    },

    async _lifecycle(uuid, fn) {
      this.actionLoading = true;
      this.error = null;
      try {
        this.currentElection = await fn();
        this.readinessReport = null;
        return this.currentElection;
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.actionLoading = false;
      }
    },
  },
});
