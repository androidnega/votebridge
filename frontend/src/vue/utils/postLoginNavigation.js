import { DASHBOARD_ROOT } from "@/config/routes";
import { useAuthStore } from "@/stores/auth";

/** Navigate away from auth screens after tokens and profile are ready. */
export async function navigateAfterLogin(router, redirectPath) {
  const authStore = useAuthStore();
  authStore.establishSession();

  const target = authStore.resolvePostLoginRedirect(redirectPath);
  await router.replace(target);

  if (router.currentRoute.value.path.startsWith("/auth")) {
    await router.replace(DASHBOARD_ROOT);
  }
}
