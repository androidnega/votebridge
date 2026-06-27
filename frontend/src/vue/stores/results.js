import { defineStore } from "pinia";
import { resultsApi } from "@/api";
import { extractApiError } from "@/api/helpers";
import realtimeService from "@/services/websocket";

export const useResultsStore = defineStore("results", {
  state: () => ({
    results: [],
    currentResult: null,
    certificationQueue: [],
    publicationQueue: [],
    archiveQueue: [],
    integrityReport: null,
    reportPayload: null,
    realtimeStatus: "disconnected",
    loading: false,
    actionLoading: false,
    error: null,
  }),

  getters: {
    publishedResults: (state) =>
      state.results.filter((r) => r.result_status === "published"),
  },

  actions: {
    async fetchResults(params = {}) {
      this.loading = true;
      this.error = null;
      try {
        this.results = await resultsApi.list(params);
        return this.results;
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async fetchResult(electionUuid) {
      this.loading = true;
      this.error = null;
      try {
        this.currentResult = await resultsApi.get(electionUuid);
        return this.currentResult;
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async generateResults(electionUuid) {
      this.actionLoading = true;
      this.error = null;
      try {
        this.currentResult = await resultsApi.generate(electionUuid);
        await this.fetchResults().catch(() => {});
        return this.currentResult;
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.actionLoading = false;
      }
    },

    async fetchIntegrity(electionUuid, acknowledgeFraud = false) {
      this.actionLoading = true;
      this.error = null;
      try {
        this.integrityReport = await resultsApi.getIntegrity(electionUuid, {
          acknowledge_fraud: acknowledgeFraud ? "true" : "false",
        });
        return this.integrityReport;
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.actionLoading = false;
      }
    },

    async certify(electionUuid, payload = {}) {
      this.actionLoading = true;
      this.error = null;
      try {
        this.currentResult = await resultsApi.certify(electionUuid, payload);
        await this.fetchQueues().catch(() => {});
        return this.currentResult;
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.actionLoading = false;
      }
    },

    async publish(electionUuid) {
      this.actionLoading = true;
      this.error = null;
      try {
        this.currentResult = await resultsApi.publish(electionUuid);
        await this.fetchQueues().catch(() => {});
        return this.currentResult;
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.actionLoading = false;
      }
    },

    async archive(electionUuid) {
      this.actionLoading = true;
      this.error = null;
      try {
        this.currentResult = await resultsApi.archive(electionUuid);
        await this.fetchQueues().catch(() => {});
        return this.currentResult;
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.actionLoading = false;
      }
    },

    async fetchQueues() {
      try {
        const [certification, publication, archive] = await Promise.all([
          resultsApi.getCertificationQueue().catch(() => []),
          resultsApi.getPublicationQueue().catch(() => []),
          resultsApi.getArchiveQueue().catch(() => []),
        ]);
        this.certificationQueue = certification;
        this.publicationQueue = publication;
        this.archiveQueue = archive;
      } catch {
        /* non-fatal */
      }
    },

    async fetchReport(electionUuid, format) {
      this.actionLoading = true;
      try {
        this.reportPayload = await resultsApi.getReport(electionUuid, format);
        return this.reportPayload;
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.actionLoading = false;
      }
    },

    connectRealtime() {
      this.realtimeStatus = "connecting";
      realtimeService.connectResults({
        onStatusChange: (status) => {
          this.realtimeStatus = status;
        },
        onMessage: (message) => {
          this.handleRealtimeMessage(message);
        },
      });
    },

    disconnectRealtime() {
      realtimeService.disconnect("results");
      this.realtimeStatus = "disconnected";
    },

    handleRealtimeMessage(message) {
      const { event, data } = message;
      if (!data?.election_uuid) return;

      const patch = {
        result_status: data.result_status,
        turnout_percentage: data.turnout_percentage,
        total_votes_cast: data.total_votes_cast,
      };

      const index = this.results.findIndex((r) => r.election_uuid === data.election_uuid);
      if (index >= 0) {
        this.results[index] = { ...this.results[index], ...patch };
      }

      if (this.currentResult?.election_uuid === data.election_uuid) {
        this.currentResult = { ...this.currentResult, ...patch, ...data };
      }

      if (["results_generated", "results_certified", "results_published"].includes(event)) {
        this.fetchQueues().catch(() => {});
        if (!this.results.length) {
          this.fetchResults().catch(() => {});
        }
      }
    },

    clearCurrent() {
      this.currentResult = null;
      this.integrityReport = null;
      this.reportPayload = null;
    },
  },
});
