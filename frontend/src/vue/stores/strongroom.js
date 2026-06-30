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
    committee: null,
    accessRequests: [],
    vaultSession: null,
    vaultEvidence: null,
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

    async fetchCommittee(electionUuid) {
      this.loading = true;
      this.error = null;
      try {
        this.committee = await strongroomApi.getCommittee(electionUuid);
        return this.committee;
      } catch (error) {
        this.committee = null;
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async saveCommittee(electionUuid, payload) {
      this.actionLoading = true;
      this.error = null;
      try {
        this.committee = await strongroomApi.saveCommittee(electionUuid, payload);
        return this.committee;
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.actionLoading = false;
      }
    },

    async submitCommittee(electionUuid) {
      this.committee = await strongroomApi.submitCommittee(electionUuid);
      return this.committee;
    },

    async approveCommittee(electionUuid) {
      this.committee = await strongroomApi.approveCommittee(electionUuid);
      return this.committee;
    },

    async fetchAccessRequests(electionUuid) {
      this.accessRequests = await strongroomApi.listAccessRequests(electionUuid);
      return this.accessRequests;
    },

    async createAccessRequest(electionUuid, payload) {
      const request = await strongroomApi.createAccessRequest(electionUuid, payload);
      await this.fetchAccessRequests(electionUuid).catch(() => {});
      return request;
    },

    async reviewAccessRequest(electionUuid, requestUuid, action) {
      const result = await strongroomApi.reviewAccessRequest(electionUuid, requestUuid, action);
      await this.fetchAccessRequests(electionUuid).catch(() => {});
      return result;
    },

    async startVaultSession(electionUuid, accessRequestUuid) {
      this.vaultSession = await strongroomApi.startVaultSession(electionUuid, accessRequestUuid);
      return this.vaultSession;
    },

    async fetchVaultSession(sessionUuid) {
      this.vaultSession = await strongroomApi.getVaultSession(sessionUuid);
      return this.vaultSession;
    },

    async authenticateCustodian(sessionUuid, payload) {
      this.vaultSession = await strongroomApi.authenticateCustodian(sessionUuid, payload);
      return this.vaultSession;
    },

    async fetchVaultEvidence(sessionUuid) {
      this.vaultEvidence = await strongroomApi.getVaultEvidence(sessionUuid);
      return this.vaultEvidence;
    },

    async closeVaultSession(sessionUuid) {
      this.vaultSession = await strongroomApi.closeVaultSession(sessionUuid);
      this.vaultEvidence = null;
      return this.vaultSession;
    },
  },
});
