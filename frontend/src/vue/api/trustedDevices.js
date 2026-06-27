import apiClient from "./client";
import { unwrapResponse } from "./helpers";

export const trustedDevicesApi = {
  list() {
    return apiClient.get("/trusted-devices/").then(unwrapResponse);
  },

  getCurrent() {
    return apiClient.get("/trusted-devices/current/").then(unwrapResponse);
  },

  getPolicy() {
    return apiClient.get("/trusted-devices/policy/").then(unwrapResponse);
  },

  getSessionStatus() {
    return apiClient.get("/trusted-devices/session-status/").then(unwrapResponse);
  },

  getHistory(deviceUuid) {
    return apiClient.get(`/trusted-devices/${deviceUuid}/history/`).then(unwrapResponse);
  },

  rename(deviceUuid, deviceName) {
    return apiClient
      .patch(`/trusted-devices/${deviceUuid}/rename/`, { device_name: deviceName })
      .then(unwrapResponse);
  },

  revoke(deviceUuid, userUuid) {
    const payload = userUuid ? { user_uuid: userUuid } : {};
    return apiClient.post(`/trusted-devices/${deviceUuid}/revoke/`, payload).then(unwrapResponse);
  },

  assignUniversity(deviceUuid) {
    return apiClient.post(`/trusted-devices/${deviceUuid}/assign-university/`).then(unwrapResponse);
  },

  remove(deviceUuid) {
    return apiClient.delete(`/trusted-devices/${deviceUuid}/`).then(unwrapResponse);
  },

  forceReverify() {
    return apiClient.post("/trusted-devices/reverify/").then(unwrapResponse);
  },
};
