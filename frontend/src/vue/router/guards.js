import { useAuthStore } from "@/stores/auth";
import { branding } from "@/config/branding";

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
    const allowedRoles = to.meta.roles;

    if (isPublic) {
      return true;
    }

    if (requiresBiometric) {
      const { useBiometricsStore } = await import("@/stores/biometrics");
      const biometricsStore = useBiometricsStore();
      biometricsStore.loadPendingAuth();
      if (!biometricsStore.pendingAuth?.pending_auth_token) {
        return { name: "auth-login", query: { redirect: to.query.redirect } };
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

    if (guestOnly && authStore.isAuthenticated && !requiresOtp && !requiresBiometric) {
      return { name: "home" };
    }

    return true;
  });

  router.afterEach((to) => {
    const pageTitle = to.meta?.title;
    document.title = pageTitle ? `${pageTitle} · ${branding.systemName}` : branding.systemName;
  });
}
