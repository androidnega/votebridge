import { defineStore } from "pinia";
import { analyticsApi } from "@/api/analytics";
import { extractApiError } from "@/api/helpers";
import realtimeService from "@/services/websocket";

export const useAnalyticsStore = defineStore("analytics", {
  state: () => ({
    overview: null,
    elections: null,
    participation: null,
    departments: [],
    faculties: [],
    programmes: [],
    students: null,
    personal: null,
    security: null,
    fraud: null,
    operations: null,
    communications: null,
    ussd: null,
    strongroom: null,
    historical: null,
    reports: null,
    realtimeStatus: "disconnected",
    loading: false,
    error: null,
  }),

  actions: {
    async fetchOverview() {
      this.loading = true;
      this.error = null;
      try {
        this.overview = await analyticsApi.getOverview();
        return this.overview;
      } catch (e) {
        this.error = extractApiError(e);
        throw e;
      } finally {
        this.loading = false;
      }
    },

    async fetchElections() {
      this.loading = true;
      this.error = null;
      try {
        this.elections = await analyticsApi.getElections();
        return this.elections;
      } catch (e) {
        this.error = extractApiError(e);
        throw e;
      } finally {
        this.loading = false;
      }
    },

    async fetchParticipation() {
      this.loading = true;
      try {
        this.participation = await analyticsApi.getParticipation();
        return this.participation;
      } catch (e) {
        this.error = extractApiError(e);
        throw e;
      } finally {
        this.loading = false;
      }
    },

    async fetchDepartments() {
      this.departments = await analyticsApi.getDepartments();
      return this.departments;
    },

    async fetchFaculties() {
      this.faculties = await analyticsApi.getFaculties();
      return this.faculties;
    },

    async fetchProgrammes() {
      this.programmes = await analyticsApi.getProgrammes();
      return this.programmes;
    },

    async fetchStudents() {
      this.loading = true;
      try {
        this.students = await analyticsApi.getStudents();
        return this.students;
      } catch (e) {
        this.error = extractApiError(e);
        throw e;
      } finally {
        this.loading = false;
      }
    },

    async fetchSecurity() {
      this.loading = true;
      try {
        this.security = await analyticsApi.getSecurity();
        return this.security;
      } catch (e) {
        this.error = extractApiError(e);
        throw e;
      } finally {
        this.loading = false;
      }
    },

    async fetchFraud() {
      this.loading = true;
      try {
        this.fraud = await analyticsApi.getFraud();
        return this.fraud;
      } catch (e) {
        this.error = extractApiError(e);
        throw e;
      } finally {
        this.loading = false;
      }
    },

    async fetchOperations() {
      this.loading = true;
      try {
        this.operations = await analyticsApi.getOperations();
        return this.operations;
      } catch (e) {
        this.error = extractApiError(e);
        throw e;
      } finally {
        this.loading = false;
      }
    },

    async fetchCommunications() {
      this.loading = true;
      try {
        this.communications = await analyticsApi.getCommunications();
        return this.communications;
      } catch (e) {
        this.error = extractApiError(e);
        throw e;
      } finally {
        this.loading = false;
      }
    },

    async fetchUssd() {
      this.loading = true;
      try {
        this.ussd = await analyticsApi.getUssd();
        return this.ussd;
      } catch (e) {
        this.error = extractApiError(e);
        throw e;
      } finally {
        this.loading = false;
      }
    },

    async fetchStrongroom() {
      this.loading = true;
      try {
        this.strongroom = await analyticsApi.getStrongroom();
        return this.strongroom;
      } catch (e) {
        this.error = extractApiError(e);
        throw e;
      } finally {
        this.loading = false;
      }
    },

    async fetchHistorical(period = "daily") {
      this.loading = true;
      try {
        this.historical = await analyticsApi.getHistorical(period);
        return this.historical;
      } catch (e) {
        this.error = extractApiError(e);
        throw e;
      } finally {
        this.loading = false;
      }
    },

    async fetchReport(type, format = "json") {
      this.reports = await analyticsApi.getReport(type, format);
      return this.reports;
    },

    connectRealtime() {
      this.realtimeStatus = "connecting";
      realtimeService.connectAnalytics({
        onStatusChange: (status) => {
          this.realtimeStatus = status;
        },
        onMessage: (message) => {
          if (message.event === "dashboard_stats" && message.data) {
            this.overview = message.data;
          }
        },
      });
    },

    disconnectRealtime() {
      realtimeService.disconnect("analytics");
      this.realtimeStatus = "disconnected";
    },
  },
});
