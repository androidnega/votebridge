import { defineStore } from "pinia";
import { operationsApi } from "@/api/operations";
import { extractApiError } from "@/api/helpers";
import realtimeService from "@/services/websocket";

export const useOperationsStore = defineStore("operations", {
  state: () => ({
    overview: null,
    activity: { items: [], total: 0 },
    health: null,
    infrastructure: null,
    elections: [],
    sessions: null,
    communications: null,
    queues: null,
    performance: null,
    logs: { items: [], total: 0 },
    activityFilters: { category: "", search: "", hours: 24 },
    logsFilters: { search: "", hours: 24, event_type: "" },
    realtimeStatus: "disconnected",
    liveEvents: [],
    loading: false,
    error: null,
  }),

  actions: {
    async fetchOverview() {
      this.loading = true;
      this.error = null;
      try {
        this.overview = await operationsApi.getOverview();
        return this.overview;
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async fetchActivity(params = {}) {
      this.loading = true;
      this.error = null;
      try {
        const data = await operationsApi.getActivity({
          ...this.activityFilters,
          ...params,
        });
        this.activity = data;
        return data;
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async loadMoreActivity() {
      const data = await operationsApi.getActivity({
        ...this.activityFilters,
        offset: this.activity.items.length,
        limit: 50,
      });
      this.activity = {
        ...data,
        items: [...this.activity.items, ...data.items],
      };
    },

    async fetchHealth() {
      this.loading = true;
      this.error = null;
      try {
        this.health = await operationsApi.getHealth();
        return this.health;
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async fetchInfrastructure() {
      this.loading = true;
      this.error = null;
      try {
        this.infrastructure = await operationsApi.getInfrastructure();
        return this.infrastructure;
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async fetchElectionMonitor() {
      this.loading = true;
      this.error = null;
      try {
        this.elections = await operationsApi.getElectionMonitor();
        return this.elections;
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async fetchSessions() {
      this.loading = true;
      this.error = null;
      try {
        this.sessions = await operationsApi.getSessions();
        return this.sessions;
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async fetchCommunications() {
      this.loading = true;
      this.error = null;
      try {
        this.communications = await operationsApi.getCommunications();
        return this.communications;
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async fetchQueues() {
      this.loading = true;
      this.error = null;
      try {
        this.queues = await operationsApi.getQueues();
        return this.queues;
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async fetchPerformance() {
      this.loading = true;
      this.error = null;
      try {
        this.performance = await operationsApi.getPerformance();
        return this.performance;
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async fetchLogs(params = {}) {
      this.loading = true;
      this.error = null;
      try {
        const data = await operationsApi.getLogs({
          ...this.logsFilters,
          ...params,
        });
        this.logs = data;
        return data;
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    connectRealtime() {
      this.realtimeStatus = "connecting";
      realtimeService.connectOperations({
        onStatusChange: (status) => {
          this.realtimeStatus = status;
        },
        onMessage: (message) => {
          if (message.event === "dashboard_stats" && message.data) {
            this.overview = message.data;
          } else if (message.event && message.data) {
            this.liveEvents.unshift({
              id: `${message.event}-${Date.now()}`,
              event_type: message.event,
              title: message.event.replace(/\./g, " "),
              description: JSON.stringify(message.data).slice(0, 120),
              timestamp: message.timestamp || new Date().toISOString(),
              category: "system",
            });
            this.liveEvents = this.liveEvents.slice(0, 100);
          }
        },
      });
    },

    disconnectRealtime() {
      realtimeService.disconnect("operations");
      this.realtimeStatus = "disconnected";
    },
  },
});
