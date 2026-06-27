import { defineStore } from "pinia";
import { ussdApi } from "@/api";
import { extractApiError } from "@/api/helpers";
import realtimeService from "@/services/websocket";

export const useUssdStore = defineStore("ussd", {
  state: () => ({
    dashboard: null,
    sessions: [],
    sessionsTotal: 0,
    logs: [],
    logsTotal: 0,
    currentSession: null,
    realtimeStatus: "disconnected",
    loading: false,
    error: null,
    sessionFilters: { status: "", search: "" },
    logFilters: { outcome: "", search: "" },
  }),

  actions: {
    async fetchDashboard() {
      this.loading = true;
      this.error = null;
      try {
        this.dashboard = await ussdApi.getDashboard();
        return this.dashboard;
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async fetchSessions(params = {}) {
      this.loading = true;
      this.error = null;
      try {
        const data = await ussdApi.listSessions({ ...this.sessionFilters, ...params });
        this.sessions = data.items || [];
        this.sessionsTotal = data.total || 0;
        return data;
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
        const data = await ussdApi.listLogs({ ...this.logFilters, ...params });
        this.logs = data.items || [];
        this.logsTotal = data.total || 0;
        return data;
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async fetchSessionDetail(uuid) {
      this.loading = true;
      try {
        const data = await ussdApi.getSession(uuid);
        this.currentSession = data;
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
      realtimeService.connectUssd({
        onStatusChange: (status) => {
          this.realtimeStatus = status;
        },
        onMessage: (message) => {
          if (["ussd_session_updated", "ussd_vote_completed"].includes(message.event)) {
            this.fetchDashboard().catch(() => {});
            this.fetchSessions().catch(() => {});
          }
        },
      });
    },

    disconnectRealtime() {
      realtimeService.disconnect("ussd");
      this.realtimeStatus = "disconnected";
    },
  },
});
