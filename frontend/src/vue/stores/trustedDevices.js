import { defineStore } from "pinia";
import { trustedDevicesApi } from "@/api/trustedDevices";
import { extractApiError } from "@/api/helpers";

export const useTrustedDevicesStore = defineStore("trustedDevices", {
  state: () => ({
    devices: [],
    currentDevice: null,
    sessionStatus: null,
    policy: null,
    loading: false,
    actionLoading: false,
    error: null,
    lastRiskReasons: [],
  }),

  getters: {
    activeDevices: (state) => state.devices.filter((d) => d.is_trusted && !d.is_revoked),
    highAssuranceActive: (state) => Boolean(state.sessionStatus?.active),
  },

  actions: {
    setRiskReasons(reasons) {
      this.lastRiskReasons = reasons || [];
    },

    async fetchDevices() {
      this.loading = true;
      this.error = null;
      try {
        this.devices = await trustedDevicesApi.list();
        return this.devices;
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async fetchCurrentDevice() {
      try {
        this.currentDevice = await trustedDevicesApi.getCurrent();
        return this.currentDevice;
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      }
    },

    async fetchSessionStatus() {
      try {
        this.sessionStatus = await trustedDevicesApi.getSessionStatus();
        return this.sessionStatus;
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      }
    },

    async fetchPolicy() {
      this.policy = await trustedDevicesApi.getPolicy();
      return this.policy;
    },

    async fetchDeviceHistory(uuid) {
      return trustedDevicesApi.getHistory(uuid);
    },

    async renameDevice(uuid, name) {
      this.actionLoading = true;
      try {
        await trustedDevicesApi.rename(uuid, name);
        await this.fetchDevices();
      } finally {
        this.actionLoading = false;
      }
    },

    async revokeDevice(uuid) {
      this.actionLoading = true;
      try {
        await trustedDevicesApi.revoke(uuid);
        await this.fetchDevices();
      } finally {
        this.actionLoading = false;
      }
    },

    async assignUniversity(uuid) {
      this.actionLoading = true;
      try {
        await trustedDevicesApi.assignUniversity(uuid);
        await this.fetchDevices();
      } finally {
        this.actionLoading = false;
      }
    },

    async forceReverify() {
      this.actionLoading = true;
      try {
        return await trustedDevicesApi.forceReverify();
      } finally {
        this.actionLoading = false;
      }
    },
  },
});
