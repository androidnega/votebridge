import { defineStore } from "pinia";
import { notificationsApi } from "@/api";
import { extractApiError } from "@/api/helpers";
import realtimeService from "@/services/websocket";

export const useNotificationsStore = defineStore("notifications", {
  state: () => ({
    dashboard: null,
    deliveries: [],
    deliveriesTotal: 0,
    templates: [],
    providers: [],
    notifications: [],
    notificationsTotal: 0,
    unreadCount: 0,
    realtimeStatus: "disconnected",
    loading: false,
    actionLoading: false,
    error: null,
    deliveryFilters: { channel: "", status: "", search: "" },
  }),

  actions: {
    async fetchDashboard() {
      this.loading = true;
      this.error = null;
      try {
        this.dashboard = await notificationsApi.getDashboard();
        return this.dashboard;
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async fetchDeliveries(params = {}) {
      this.loading = true;
      this.error = null;
      try {
        const data = await notificationsApi.listDeliveries({
          ...this.deliveryFilters,
          ...params,
        });
        this.deliveries = data.items || [];
        this.deliveriesTotal = data.total || 0;
        return data;
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async fetchTemplates() {
      this.loading = true;
      this.error = null;
      try {
        this.templates = await notificationsApi.listTemplates();
        return this.templates;
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async fetchProviders() {
      this.loading = true;
      this.error = null;
      try {
        this.providers = await notificationsApi.listProviders();
        return this.providers;
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async fetchNotificationCenter(params = {}) {
      this.loading = true;
      this.error = null;
      try {
        const data = await notificationsApi.getNotificationCenter(params);
        this.notifications = data.items || [];
        this.notificationsTotal = data.total || 0;
        this.unreadCount = data.unread_count || 0;
        return data;
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async markRead(uuid) {
      await notificationsApi.markRead(uuid);
      const item = this.notifications.find((n) => n.uuid === uuid);
      if (item) {
        item.is_read = true;
        this.unreadCount = Math.max(0, this.unreadCount - 1);
      }
    },

    async markAllRead() {
      this.actionLoading = true;
      try {
        await notificationsApi.markAllRead();
        this.notifications.forEach((n) => {
          n.is_read = true;
        });
        this.unreadCount = 0;
      } finally {
        this.actionLoading = false;
      }
    },

    async archiveNotification(uuid) {
      await notificationsApi.archiveNotification(uuid);
      this.notifications = this.notifications.filter((n) => n.uuid !== uuid);
    },

    async deleteNotification(uuid) {
      await notificationsApi.deleteNotification(uuid);
      this.notifications = this.notifications.filter((n) => n.uuid !== uuid);
    },

    async retryDelivery(uuid) {
      this.actionLoading = true;
      try {
        await notificationsApi.retryDelivery(uuid);
        await this.fetchDeliveries().catch(() => {});
      } finally {
        this.actionLoading = false;
      }
    },

    async processQueue() {
      this.actionLoading = true;
      try {
        const result = await notificationsApi.processQueue();
        await this.fetchDashboard().catch(() => {});
        await this.fetchDeliveries({ status: "pending" }).catch(() => {});
        return result;
      } finally {
        this.actionLoading = false;
      }
    },

    async testProvider(uuid) {
      this.actionLoading = true;
      try {
        return await notificationsApi.testProvider(uuid);
      } finally {
        this.actionLoading = false;
      }
    },

    async sendTestMessage(payload) {
      this.actionLoading = true;
      try {
        return await notificationsApi.sendTestMessage(payload);
      } finally {
        this.actionLoading = false;
      }
    },

    connectRealtime(isAdmin = false) {
      this.realtimeStatus = "connecting";
      const key = isAdmin ? "communications" : "notifications";
      const connect = isAdmin
        ? realtimeService.connectCommunications.bind(realtimeService)
        : realtimeService.connectNotifications.bind(realtimeService);

      connect({
        onStatusChange: (status) => {
          this.realtimeStatus = status;
        },
        onMessage: (message) => {
          if (message.event === "in_app_notification_created") {
            this.fetchNotificationCenter().catch(() => {});
          }
          if (
            isAdmin &&
            ["communication_delivery_updated", "in_app_notification_created"].includes(message.event)
          ) {
            this.fetchDashboard().catch(() => {});
          }
        },
      });
    },

    disconnectRealtime(isAdmin = false) {
      realtimeService.disconnect(isAdmin ? "communications" : "notifications");
      this.realtimeStatus = "disconnected";
    },
  },
});
