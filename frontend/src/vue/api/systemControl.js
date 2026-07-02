import apiClient from "./client";
import { unwrapResponse } from "./helpers";

export const systemControlApi = {
  getOverview() {
    return apiClient.get("/system/overview/").then(unwrapResponse);
  },

  getPublicBranding() {
    return apiClient.get("/system/branding/").then(unwrapResponse);
  },

  getMaintenance() {
    return apiClient.get("/system/maintenance/").then(unwrapResponse);
  },

  requestStepUp() {
    return apiClient.post("/system/step-up/challenge/").then(unwrapResponse);
  },

  verifyStepUp(payload) {
    return apiClient.post("/system/step-up/verify/", payload).then(unwrapResponse);
  },

  getInstitution() {
    return apiClient.get("/system/institution/").then(unwrapResponse);
  },

  updateInstitution(data, preview = false) {
    return apiClient
      .patch("/system/institution/", data, { params: preview ? { preview: "true" } : {} })
      .then(unwrapResponse);
  },

  getSettings(category) {
    return apiClient.get(`/system/settings/${category}/`).then(unwrapResponse);
  },

  updateSettings(category, payload) {
    return apiClient.patch(`/system/settings/${category}/`, payload).then(unwrapResponse);
  },

  getRevisions(key) {
    return apiClient.get(`/system/revisions/${encodeURIComponent(key)}/`).then(unwrapResponse);
  },

  rollbackSetting(key, payload) {
    return apiClient.post(`/system/revisions/${encodeURIComponent(key)}/`, payload).then(unwrapResponse);
  },

  getFeatureFlags() {
    return apiClient.get("/system/feature-flags/").then(unwrapResponse);
  },

  updateFeatureFlag(key, payload) {
    return apiClient.patch(`/system/feature-flags/${key}/`, payload).then(unwrapResponse);
  },

  getMaintenanceControl() {
    return apiClient.get("/system/maintenance/control/").then(unwrapResponse);
  },

  updateMaintenance(payload) {
    return apiClient.patch("/system/maintenance/control/", payload).then(unwrapResponse);
  },

  getProviders(type) {
    return apiClient.get("/system/providers/", { params: type ? { type } : {} }).then(unwrapResponse);
  },

  updateProvider(uuid, payload) {
    return apiClient.patch(`/system/providers/${uuid}/`, payload).then(unwrapResponse);
  },

  testProvider(uuid) {
    return apiClient.post(`/system/providers/${uuid}/`).then(unwrapResponse);
  },

  getStorage() {
    return apiClient.get("/system/storage/").then(unwrapResponse);
  },

  cleanupStorage(stepUpToken) {
    return apiClient.post("/system/storage/", { step_up_token: stepUpToken }).then(unwrapResponse);
  },

  getBackups() {
    return apiClient.get("/system/backups/").then(unwrapResponse);
  },

  createBackup(stepUpToken) {
    return apiClient.post("/system/backups/", { step_up_token: stepUpToken }).then(unwrapResponse);
  },

  verifyBackup(uuid) {
    return apiClient.post(`/system/backups/${uuid}/`, { action: "verify" }).then(unwrapResponse);
  },

  getEnvironment() {
    return apiClient.get("/system/environment/").then(unwrapResponse);
  },

  getLicense() {
    return apiClient.get("/system/license/").then(unwrapResponse);
  },

  getRuntime() {
    return apiClient.get("/system/runtime/").then(unwrapResponse);
  },

  resetOperationalData(payload) {
    return apiClient.post("/system/data-reset/", payload).then(unwrapResponse);
  },
};
