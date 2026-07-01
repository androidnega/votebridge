import { useAuthStore } from "@/stores/auth";
import { branding } from "@/config/branding";
import { DASHBOARD_ROOT, normalizeAuthRedirect } from "@/config/routes";

export function setupRouterGuards(router) {
  router.beforeEach(async (to) => {
    const authStore = useAuthStore();

    if (!authStore.initialized) {
      await authStore.initialize();
    }

    const requiresAuth = to.matched.some((record) => record.meta.requiresAuth);
    const guestOnly = to.matched.some((record) => record.meta.guest);
    const isPublic = to.matched.some((record) => record.meta.public);
    const requiresOtp = to.meta.requiresOtp;
    const requiresBiometric = to.meta.requiresBiometric;
    const requiresEnrollment = to.meta.requiresEnrollment;
    const allowedRoles = to.meta.roles;

    if (isPublic) {
      return true;
    }

    if (requiresBiometric || requiresEnrollment) {
      const { useBiometricsStore } = await import("@/stores/biometrics");
      const biometricsStore = useBiometricsStore();
      biometricsStore.loadPendingAuth();

      try {
        await biometricsStore.fetchStatus();
      } catch {
        /* status optional for guard */
      }

      if (biometricsStore.status && !biometricsStore.status.module_enabled) {
        biometricsStore.clearPendingAuth();
        return { name: "auth-login", query: { redirect: to.query.redirect } };
      }

      if (!biometricsStore.pendingAuth?.pending_auth_token) {
        return { name: "auth-login", query: { redirect: to.query.redirect } };
      }
      if (requiresEnrollment && !biometricsStore.pendingAuth?.requires_enrollment) {
        return { name: "auth-biometric-verify", query: to.query };
      }
      if (requiresBiometric && biometricsStore.pendingAuth?.requires_enrollment) {
        return { name: "auth-biometric-enroll", query: to.query };
      }
    }

    if (requiresOtp && !authStore.hasPendingOtp) {
      return { name: "auth-login", query: { redirect: to.query.redirect } };
    }

    if (requiresAuth && !authStore.isAuthenticated) {
      return {
        name: "auth-login",
        query: { redirect: to.fullPath !== "/auth/login" ? to.fullPath : undefined },
      };
    }

    if (allowedRoles?.length && authStore.role && !allowedRoles.includes(authStore.role)) {
      return { name: "forbidden" };
    }

    if (to.meta.requiresVaultSession) {
      const { strongroomApi } = await import("@/api/strongroom");
      const sessionUuid = to.params.sessionUuid;
      const electionUuid = to.params.uuid;
      if (!sessionUuid || !electionUuid) {
        return { name: "forbidden" };
      }
      try {
        const session = await strongroomApi.getVaultSession(sessionUuid);
        if (to.meta.requiresActiveVault && session.status !== "active") {
          if (session.status === "awaiting_custodians") {
            return {
              name: "election-vault-terminal",
              params: { uuid: electionUuid, sessionUuid },
            };
          }
          return { name: "election-vault-access", params: { uuid: electionUuid } };
        }
        if (["resealed", "expired", "closed"].includes(session.status)) {
          return { name: "election-vault-access", params: { uuid: electionUuid } };
        }
      } catch {
        return { name: "election-vault-access", params: { uuid: electionUuid } };
      }
    }

    if (guestOnly && authStore.isAuthenticated && !requiresOtp && !requiresBiometric && !requiresEnrollment) {
      const redirect = normalizeAuthRedirect(
        typeof to.query.redirect === "string" ? to.query.redirect : DASHBOARD_ROOT
      );
      return redirect.startsWith("/") ? redirect : { name: "dashboard" };
    }

    return true;
  });

  router.afterEach((to) => {
    const pageTitle = to.meta?.title;
    document.title = pageTitle ? `${pageTitle} · ${branding.systemName}` : branding.systemName;
  });
}
