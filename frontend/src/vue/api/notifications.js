import apiClient from "./client";
import { unwrapResponse } from "./helpers";

export const notificationsApi = {
  getDashboard() {
    return apiClient.get("/notifications/dashboard/").then(unwrapResponse);
  },

  listDeliveries(params = {}) {
    return apiClient.get("/notifications/deliveries/", { params }).then(unwrapResponse);
  },

  retryDelivery(logUuid) {
    return apiClient.post(`/notifications/deliveries/${logUuid}/retry/`).then(unwrapResponse);
  },

  processQueue(limit = 50) {
    return apiClient.post("/notifications/queue/process/", { limit }).then(unwrapResponse);
  },

  listTemplates() {
    return apiClient.get("/notifications/templates/").then(unwrapResponse);
  },

  listProviders() {
    return apiClient.get("/notifications/providers/").then(unwrapResponse);
  },

  testProvider(providerUuid) {
    return apiClient.post(`/notifications/providers/${providerUuid}/test/`).then(unwrapResponse);
  },

  sendTestMessage(payload) {
    return apiClient.post("/notifications/test/", payload).then(unwrapResponse);
  },

  getNotificationCenter(params = {}) {
    return apiClient.get("/notifications/center/", { params }).then(unwrapResponse);
  },

  markRead(notificationUuid) {
    return apiClient.post(`/notifications/center/${notificationUuid}/read/`).then(unwrapResponse);
  },

  markAllRead() {
    return apiClient.post("/notifications/center/read-all/").then(unwrapResponse);
  },

  archiveNotification(notificationUuid) {
    return apiClient.post(`/notifications/center/${notificationUuid}/archive/`).then(unwrapResponse);
  },

  deleteNotification(notificationUuid) {
    return apiClient.delete(`/notifications/center/${notificationUuid}/`).then(unwrapResponse);
  },
};
