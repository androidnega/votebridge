import { defineStore } from "pinia";
import { strongroomApi } from "@/api";
import { extractApiError } from "@/api/helpers";
import realtimeService from "@/services/websocket";

export const useStrongroomStore = defineStore("strongroom", {
  state: () => ({
    elections: [],
    dashboard: null,
    custodyTimeline: [],
    verificationResult: null,
    realtimeStatus: "disconnected",
    loading: false,
    actionLoading: false,
    error: null,
  }),

  actions: {
    async fetchElections() {
      this.loading = true;
      this.error = null;
      try {
        this.elections = await strongroomApi.list();
        return this.elections;
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async fetchDashboard(electionUuid) {
      this.loading = true;
      this.error = null;
      try {
        this.dashboard = await strongroomApi.getDashboard(electionUuid);
        this.custodyTimeline = this.dashboard.custody_timeline || [];
        return this.dashboard;
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async verifyIntegrity(electionUuid) {
      this.actionLoading = true;
      this.error = null;
      try {
        const report = await strongroomApi.verifyIntegrity(electionUuid);
        await this.fetchDashboard(electionUuid).catch(() => {});
        return report;
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.actionLoading = false;
      }
    },

    async lockElection(electionUuid) {
      this.actionLoading = true;
      this.error = null;
      try {
        const result = await strongroomApi.lockElection(electionUuid);
        await this.fetchDashboard(electionUuid).catch(() => {});
        return result;
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.actionLoading = false;
      }
    },

    async publicVerify(electionUuid, verificationHash) {
      this.actionLoading = true;
      this.error = null;
      this.verificationResult = null;
      try {
        this.verificationResult = await strongroomApi.publicVerify(
          electionUuid,
          verificationHash
        );
        return this.verificationResult;
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.actionLoading = false;
      }
    },

    connectRealtime() {
      this.realtimeStatus = "connecting";
      realtimeService.connectStrongroom({
        onStatusChange: (status) => {
          this.realtimeStatus = status;
        },
        onMessage: (message) => {
          if (
            ["strongroom_sealed", "strongroom_verified", "election_locked", "integrity_check_completed"].includes(
              message.event
            ) &&
            message.data
          ) {
            this.fetchElections().catch(() => {});
            if (this.dashboard?.election_uuid === message.data.election_uuid) {
              this.fetchDashboard(message.data.election_uuid).catch(() => {});
            }
          }
        },
      });
    },

    disconnectRealtime() {
      realtimeService.disconnect("strongroom");
      this.realtimeStatus = "disconnected";
    },

    clearDashboard() {
      this.dashboard = null;
      this.custodyTimeline = [];
    },
  },
});
