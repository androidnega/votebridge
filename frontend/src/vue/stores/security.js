import { defineStore } from "pinia";
import { securityApi } from "@/api";
import { extractApiError } from "@/api/helpers";
import realtimeService from "@/services/websocket";

function upsertAlert(feed, alert) {
  const index = feed.findIndex((item) => item.alert_id === alert.alert_id);
  if (index >= 0) {
    feed[index] = { ...feed[index], ...alert };
    return feed;
  }
  return [alert, ...feed];
}

export const useSecurityStore = defineStore("security", {
  state: () => ({
    summary: null,
    alertsFeed: [],
    auditLogs: [],
    realtimeStatus: "disconnected",
    loading: false,
    error: null,
  }),

  actions: {
    async fetchSummary() {
      this.loading = true;
      this.error = null;
      try {
        this.summary = await securityApi.getMonitoringSummary();
        return this.summary;
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async fetchSecurityFeed() {
      this.loading = true;
      this.error = null;
      try {
        const data = await securityApi.getSecurityFeed();
        this.alertsFeed = data.alerts || [];
        if (data.summary) {
          this.summary = { ...this.summary, alerts: data.summary };
        }
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
      realtimeService.connectSecurity({
        onStatusChange: (status) => {
          this.realtimeStatus = status;
        },
        onMessage: (message) => {
          this.handleRealtimeMessage(message);
        },
      });
    },

    disconnectRealtime() {
      realtimeService.disconnect("security");
      this.realtimeStatus = "disconnected";
    },

    handleRealtimeMessage(message) {
      const { event, data } = message;
      if (!data) return;

      if (event === "dashboard_stats" && data.alerts) {
        this.alertsFeed = data.alerts;
        if (data.summary) {
          this.summary = { ...this.summary, alerts: data.summary };
        }
        return;
      }

      if (event === "security_alert_created") {
        this.alertsFeed = upsertAlert(this.alertsFeed, data).slice(0, 25);
        return;
      }

      if (event === "security_alert_resolved") {
        this.alertsFeed = upsertAlert(this.alertsFeed, {
          ...data,
          status: data.status || "resolved",
        }).slice(0, 25);
      }
    },
  },
});
