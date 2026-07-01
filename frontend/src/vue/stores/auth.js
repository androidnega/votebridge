import { defineStore } from "pinia";
import { authApi } from "@/api";
import { ensureAccessToken } from "@/api/client";
import { normalizeAuthRedirect, DASHBOARD_ROOT } from "@/config/routes";
import {
  clearOtpChallenge,
  clearSession,
  extractApiError,
  getAccessToken,
  getOtpChallenge,
  getRefreshToken,
  getUserUuid,
  setOtpChallenge,
  setSessionMeta,
  setTokens,
} from "@/api/helpers";
import realtimeService from "@/services/websocket";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    user: null,
    sessions: [],
    otpChallenge: getOtpChallenge(),
    postLoginRedirect: DASHBOARD_ROOT,
    loading: false,
    otpLoading: false,
    sessionsLoading: false,
    initialized: false,
  }),

  getters: {
    isAuthenticated: (state) =>
      Boolean(state.user?.uuid) || Boolean(getAccessToken() || getRefreshToken()),
    role: (state) => state.user?.role?.name || null,
    roleDisplay: (state) => state.user?.role?.name_display || state.user?.role?.name || "",
    fullName: (state) => {
      if (!state.user) return "";
      return [state.user.first_name, state.user.last_name].filter(Boolean).join(" ");
    },
    isElectionOfficer: (state) => state.user?.role?.name === "admin",
    isStaff: (state) => ["admin", "super_admin"].includes(state.user?.role?.name),
    isAdmin: (state) => state.user?.role?.name === "admin",
    isSuperAdmin: (state) => state.user?.role?.name === "super_admin",
    isStudent: (state) => ["student", "candidate"].includes(state.user?.role?.name),
    hasPendingOtp: (state) => Boolean(state.otpChallenge?.otp_request_uuid),
  },

  actions: {
    async initialize() {
      if (this.initialized) return;
      this.initialized = true;

      if (!getAccessToken() && !getRefreshToken()) {
        clearSession();
        this.user = null;
        return;
      }

      const sessionReady = await ensureAccessToken();
      if (!sessionReady) {
        this.user = null;
        return;
      }

      try {
        await this.fetchProfile();
        if (this.user?.uuid) {
          setSessionMeta({
            userUuid: this.user.uuid,
            sessionUuid: getSessionUuid(),
          });
        }
      } catch {
        clearSession();
        this.user = null;
      }
    },

    async fetchProfile() {
      this.loading = true;
      try {
        this.user = await authApi.getProfile();
        return this.user;
      } catch (error) {
        throw new Error(extractApiError(error));
      } finally {
        this.loading = false;
      }
    },

    async updateProfile(payload) {
      const uuid = this.user?.uuid || getUserUuid();
      if (!uuid) throw new Error("No user session found.");
      this.loading = true;
      try {
        this.user = await authApi.updateProfile(uuid, payload);
        return this.user;
      } catch (error) {
        throw new Error(extractApiError(error));
      } finally {
        this.loading = false;
      }
    },

    async initiateLogin({ identity, password }) {
      this.loading = true;
      const trimmed = identity?.trim() || "";

      try {
        const challenge = await authApi.login({
          identity: trimmed,
          password,
        });

        this.otpChallenge = challenge;
        setOtpChallenge(this.otpChallenge);
        return this.otpChallenge;
      } catch (error) {
        throw new Error(extractApiError(error));
      } finally {
        this.loading = false;
      }
    },

    async verifyOtp(otpCode) {
      if (!this.otpChallenge?.otp_request_uuid) {
        throw new Error("No pending verification. Please sign in again.");
      }

      this.otpLoading = true;
      try {
        const result = await authApi.verifyOtp({
          otp_request_uuid: this.otpChallenge.otp_request_uuid,
          otp_code: otpCode.trim(),
        });

        if (result.requires_biometric) {
          const { useBiometricsStore } = await import("@/stores/biometrics");
          const { useTrustedDevicesStore } = await import("@/stores/trustedDevices");
          const { clearTokens } = await import("@/api/helpers");
          const biometricsStore = useBiometricsStore();
          const trustedStore = useTrustedDevicesStore();
          clearTokens();
          biometricsStore.setPendingAuth(result);
          trustedStore.setRiskReasons(result.risk_reasons || []);
          clearOtpChallenge();
          this.otpChallenge = null;
          return { requiresBiometric: true, pendingAuth: result, riskReasons: result.risk_reasons };
        }

        if (result.requires_enrollment) {
          const { useBiometricsStore } = await import("@/stores/biometrics");
          const { clearTokens } = await import("@/api/helpers");
          const biometricsStore = useBiometricsStore();
          clearTokens();
          biometricsStore.setPendingAuth(result);
          clearOtpChallenge();
          this.otpChallenge = null;
          return { requiresEnrollment: true, pendingAuth: result };
        }

        setTokens(result.tokens.access, result.tokens.refresh);
        setSessionMeta({
          userUuid: result.user_uuid,
          sessionUuid: result.session_uuid,
        });

        clearOtpChallenge();
        this.otpChallenge = null;
        this.postLoginRedirect = normalizeAuthRedirect(result.redirect_path);
        await this.fetchProfile();
        return { user: this.user, redirectPath: this.postLoginRedirect };
      } catch (error) {
        throw new Error(extractApiError(error));
      } finally {
        this.otpLoading = false;
      }
    },

    async resendOtp() {
      if (!this.otpChallenge?.otp_request_uuid) {
        throw new Error("No pending verification. Please sign in again.");
      }

      this.otpLoading = true;
      try {
        const result = await authApi.resendOtp({
          otp_request_uuid: this.otpChallenge.otp_request_uuid,
        });
        this.otpChallenge = {
          ...this.otpChallenge,
          otp_request_uuid: result.otp_request_uuid,
          expires_at: result.expires_at,
          channel: result.channel,
        };
        setOtpChallenge(this.otpChallenge);
        return this.otpChallenge;
      } catch (error) {
        throw new Error(extractApiError(error));
      } finally {
        this.otpLoading = false;
      }
    },

    clearOtpFlow() {
      clearOtpChallenge();
      this.otpChallenge = null;
    },

    async fetchSessions() {
      this.sessionsLoading = true;
      try {
        this.sessions = await authApi.listSessions();
        return this.sessions;
      } catch (error) {
        throw new Error(extractApiError(error));
      } finally {
        this.sessionsLoading = false;
      }
    },

    async revokeSession(sessionUuid) {
      await authApi.revokeSession(sessionUuid);
      this.sessions = this.sessions.filter((session) => session.uuid !== sessionUuid);
    },

    async logout() {
      try {
        if (getRefreshToken()) {
          await authApi.logout();
        }
      } catch {
        /* always clear local session */
      } finally {
        realtimeService.disconnectAll();
        clearSession();
        this.user = null;
        this.sessions = [];
        this.otpChallenge = null;
      }
    },
  },
});
