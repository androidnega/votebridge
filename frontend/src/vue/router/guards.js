import { useAuthStore } from "@/stores/auth";

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
    const allowedRoles = to.meta.roles;

    if (isPublic) {
      return true;
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

    if (guestOnly && authStore.isAuthenticated && !requiresOtp) {
      return { name: "home" };
    }

    return true;
  });
}
