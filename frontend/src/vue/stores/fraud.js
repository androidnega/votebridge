import { defineStore } from "pinia";
import { fraudApi } from "@/api";
import { extractApiError } from "@/api/helpers";
import realtimeService from "@/services/websocket";

function upsertCase(feed, fraudCase) {
  const index = feed.findIndex((item) => item.fraud_case_id === fraudCase.fraud_case_id);
  if (index >= 0) {
    feed[index] = { ...feed[index], ...fraudCase };
    return feed;
  }
  return [fraudCase, ...feed];
}

export const useFraudStore = defineStore("fraud", {
  state: () => ({
    integrityReport: null,
    cases: [],
    casesFeed: [],
    realtimeStatus: "disconnected",
    loading: false,
    error: null,
  }),

  actions: {
    async fetchIntegrityReport(params = {}) {
      this.loading = true;
      this.error = null;
      try {
        this.integrityReport = await fraudApi.getIntegrityReport(params);
        return this.integrityReport;
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async fetchCases(params = {}) {
      this.loading = true;
      this.error = null;
      try {
        this.cases = await fraudApi.listCases(params);
        return this.cases;
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async fetchFraudFeed() {
      this.loading = true;
      this.error = null;
      try {
        const data = await fraudApi.getFraudFeed();
        this.casesFeed = data.cases || [];
        if (data.summary) {
          this.integrityReport = data.summary;
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
      realtimeService.connectFraud({
        onStatusChange: (status) => {
          this.realtimeStatus = status;
        },
        onMessage: (message) => {
          this.handleRealtimeMessage(message);
        },
      });
    },

    disconnectRealtime() {
      realtimeService.disconnect("fraud");
      this.realtimeStatus = "disconnected";
    },

    handleRealtimeMessage(message) {
      const { event, data } = message;
      if (!data) return;

      if (event === "dashboard_stats") {
        if (data.cases) {
          this.casesFeed = data.cases;
        }
        if (data.summary) {
          this.integrityReport = data.summary;
        }
        if (data.fraud_cases) {
          this.integrityReport = { ...this.integrityReport, ...data.fraud_cases };
        }
        return;
      }

      if (event === "fraud_case_created") {
        this.casesFeed = upsertCase(this.casesFeed, data).slice(0, 25);
        if (this.integrityReport) {
          this.integrityReport = {
            ...this.integrityReport,
            open_cases: (this.integrityReport.open_cases || 0) + 1,
          };
        }
        return;
      }

      if (event === "fraud_case_resolved" || event === "fraud_case_escalated") {
        this.casesFeed = upsertCase(this.casesFeed, data).slice(0, 25);
        if (event === "fraud_case_resolved" && this.integrityReport) {
          this.integrityReport = {
            ...this.integrityReport,
            open_cases: Math.max(0, (this.integrityReport.open_cases || 0) - 1),
            resolved_cases: (this.integrityReport.resolved_cases || 0) + 1,
          };
        }
      }
    },
  },
});
