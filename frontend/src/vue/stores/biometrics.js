import { defineStore } from "pinia";
import { biometricsApi } from "@/api/biometrics";
import { extractApiError, getDeviceSignals, setSessionMeta, setTokens } from "@/api/helpers";

export const useBiometricsStore = defineStore("biometrics", {
  state: () => ({
    status: null,
    settings: null,
    history: [],
    challenge: null,
    pendingAuth: null,
    highAssuranceToken: sessionStorage.getItem("vb_ha_token") || "",
    loading: false,
    actionLoading: false,
    error: null,
    enrollmentRequirements: null,
  }),

  getters: {
    isEnrolled: (state) => Boolean(state.status?.enrolled),
    requiresVerification: (state) => Boolean(state.status?.required_for_user),
    hasHighAssurance: (state) => Boolean(state.highAssuranceToken),
  },

  actions: {
    setPendingAuth(payload) {
      this.pendingAuth = payload;
      sessionStorage.setItem("vb_pending_auth", JSON.stringify(payload));
    },

    loadPendingAuth() {
      const raw = sessionStorage.getItem("vb_pending_auth");
      if (raw) {
        try {
          this.pendingAuth = JSON.parse(raw);
        } catch {
          this.pendingAuth = null;
        }
      }
      return this.pendingAuth;
    },

    clearPendingAuth() {
      this.pendingAuth = null;
      sessionStorage.removeItem("vb_pending_auth");
    },

    setHighAssuranceToken(token) {
      this.highAssuranceToken = token || "";
      if (token) {
        sessionStorage.setItem("vb_ha_token", token);
      } else {
        sessionStorage.removeItem("vb_ha_token");
      }
    },

    async fetchStatus() {
      this.loading = true;
      this.error = null;
      try {
        this.status = await biometricsApi.getStatus();
        return this.status;
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async fetchSettings() {
      this.loading = true;
      this.error = null;
      try {
        this.settings = await biometricsApi.getSettings();
        return this.settings;
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async fetchHistory(params) {
      this.loading = true;
      this.error = null;
      try {
        this.history = await biometricsApi.getHistory(params);
        return this.history;
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async fetchEnrollmentRequirements() {
      this.enrollmentRequirements = await biometricsApi.getEnrollmentRequirements();
      return this.enrollmentRequirements;
    },

    async enroll(userUuid, images) {
      this.actionLoading = true;
      this.error = null;
      try {
        return await biometricsApi.enroll({ user_uuid: userUuid, images });
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.actionLoading = false;
      }
    },

    async requestChallenge(pendingAuthToken) {
      this.actionLoading = true;
      try {
        this.challenge = await biometricsApi.requestChallenge(
          pendingAuthToken ? { pending_auth_token: pendingAuthToken } : {}
        );
        return this.challenge;
      } finally {
        this.actionLoading = false;
      }
    },

    async verifyLogin({ pendingAuthToken, challengeId, frames }) {
      this.actionLoading = true;
      this.error = null;
      try {
        const result = await biometricsApi.verifyLogin({
          pending_auth_token: pendingAuthToken,
          challenge_id: challengeId,
          frames,
          device_signals: getDeviceSignals(),
        });
        setTokens(result.tokens.access, result.tokens.refresh);
        setSessionMeta({ userUuid: result.user_uuid, sessionUuid: result.session_uuid });
        if (result.high_assurance?.high_assurance_token) {
          this.setHighAssuranceToken(result.high_assurance.high_assurance_token);
        }
        this.clearPendingAuth();
        return result;
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.actionLoading = false;
      }
    },

    async verifyStepUp({ challengeId, frames, action }) {
      this.actionLoading = true;
      this.error = null;
      try {
        const result = await biometricsApi.verifyStepUp({
          challenge_id: challengeId,
          frames,
          action,
        });
        this.setHighAssuranceToken(result.high_assurance_token);
        return result;
      } catch (error) {
        this.error = extractApiError(error);
        throw error;
      } finally {
        this.actionLoading = false;
      }
    },
  },
});
