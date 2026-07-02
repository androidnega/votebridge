import { defineStore } from "pinia";
import { systemControlApi } from "@/api/systemControl";
import { extractApiError } from "@/api/helpers";

export const useSystemControlStore = defineStore("systemControl", {
  state: () => ({
    overview: null,
    institution: null,
    settings: {},
    featureFlags: [],
    maintenance: null,
    providers: [],
    storage: null,
    backups: [],
    environment: null,
    license: null,
    runtime: null,
    stepUpToken: null,
    stepUpExpiresAt: null,
    loading: false,
    actionLoading: false,
    error: null,
  }),

  getters: {
    hasValidStepUp(state) {
      if (!state.stepUpToken || !state.stepUpExpiresAt) return false;
      return Date.now() < state.stepUpExpiresAt;
    },
  },

  actions: {
    clearError() {
      this.error = null;
    },

    setStepUpToken(token, expiresInSeconds = 300) {
      this.stepUpToken = token;
      this.stepUpExpiresAt = Date.now() + expiresInSeconds * 1000;
    },

    clearStepUp() {
      this.stepUpToken = null;
      this.stepUpExpiresAt = null;
    },

    async fetchOverview() {
      this.loading = true;
      this.error = null;
      try {
        this.overview = await systemControlApi.getOverview();
        return this.overview;
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async fetchInstitution() {
      this.loading = true;
      this.error = null;
      try {
        this.institution = await systemControlApi.getInstitution();
        return this.institution;
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async saveInstitution(data, preview = false) {
      this.actionLoading = true;
      this.error = null;
      try {
        const result = await systemControlApi.updateInstitution(data, preview);
        if (!preview) this.institution = result;
        return result;
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.actionLoading = false;
      }
    },

    async fetchSettings(category) {
      this.loading = true;
      this.error = null;
      try {
        const data = await systemControlApi.getSettings(category);
        this.settings[category] = data;
        return data;
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async saveSettings(category, updates, reason = "") {
      this.actionLoading = true;
      this.error = null;
      try {
        const payload = {
          settings: updates,
          reason,
          step_up_token: this.stepUpToken,
        };
        const data = await systemControlApi.updateSettings(category, payload);
        this.settings[category] = data;
        this.clearStepUp();
        return data;
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.actionLoading = false;
      }
    },

    async fetchFeatureFlags() {
      this.loading = true;
      this.error = null;
      try {
        this.featureFlags = await systemControlApi.getFeatureFlags();
        return this.featureFlags;
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async toggleFeatureFlag(key, enabled) {
      this.actionLoading = true;
      this.error = null;
      try {
        const data = await systemControlApi.updateFeatureFlag(key, {
          enabled,
          step_up_token: this.stepUpToken,
        });
        const idx = this.featureFlags.findIndex((f) => f.key === key);
        if (idx >= 0) this.featureFlags[idx] = data;
        this.clearStepUp();
        return data;
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.actionLoading = false;
      }
    },

    async fetchMaintenance() {
      this.loading = true;
      this.error = null;
      try {
        this.maintenance = await systemControlApi.getMaintenanceControl();
        return this.maintenance;
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async saveMaintenance(data) {
      this.actionLoading = true;
      this.error = null;
      try {
        const payload = { ...data, step_up_token: this.stepUpToken };
        this.maintenance = await systemControlApi.updateMaintenance(payload);
        this.clearStepUp();
        return this.maintenance;
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.actionLoading = false;
      }
    },

    async fetchProviders(type) {
      this.loading = true;
      this.error = null;
      try {
        this.providers = await systemControlApi.getProviders(type);
        return this.providers;
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async saveProvider(uuid, data) {
      this.actionLoading = true;
      this.error = null;
      try {
        const result = await systemControlApi.updateProvider(uuid, {
          ...data,
          step_up_token: this.stepUpToken,
        });
        this.clearStepUp();
        return result;
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.actionLoading = false;
      }
    },

    async testProvider(uuid) {
      this.actionLoading = true;
      try {
        return await systemControlApi.testProvider(uuid);
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.actionLoading = false;
      }
    },

    async fetchStorage() {
      this.loading = true;
      this.error = null;
      try {
        this.storage = await systemControlApi.getStorage();
        return this.storage;
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async fetchBackups() {
      this.loading = true;
      this.error = null;
      try {
        this.backups = await systemControlApi.getBackups();
        return this.backups;
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async createBackup() {
      this.actionLoading = true;
      try {
        const record = await systemControlApi.createBackup(this.stepUpToken);
        this.backups.unshift(record);
        this.clearStepUp();
        return record;
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.actionLoading = false;
      }
    },

    async verifyBackup(uuid) {
      this.actionLoading = true;
      try {
        const record = await systemControlApi.verifyBackup(uuid);
        const idx = this.backups.findIndex((b) => b.uuid === uuid);
        if (idx >= 0) this.backups[idx] = record;
        return record;
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.actionLoading = false;
      }
    },

    async fetchEnvironment() {
      this.loading = true;
      try {
        this.environment = await systemControlApi.getEnvironment();
        return this.environment;
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async fetchLicense() {
      this.loading = true;
      try {
        this.license = await systemControlApi.getLicense();
        return this.license;
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async fetchRuntime() {
      this.loading = true;
      try {
        this.runtime = await systemControlApi.getRuntime();
        return this.runtime;
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async cleanupStorage() {
      this.actionLoading = true;
      try {
        const data = await systemControlApi.cleanupStorage(this.stepUpToken);
        this.clearStepUp();
        return data;
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.actionLoading = false;
      }
    },

    async resetOperationalData(confirmation) {
      this.actionLoading = true;
      this.error = null;
      try {
        const data = await systemControlApi.resetOperationalData({
          confirmation,
          step_up_token: this.stepUpToken,
        });
        this.clearStepUp();
        return data;
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.actionLoading = false;
      }
    },
  },
});
