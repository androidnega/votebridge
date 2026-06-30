/** Canonical application routes — Phase 32. */

export const DASHBOARD_ROOT = "/dashboard";
export const LANDING_PATH = "/";

/** Always land authenticated users on the universal dashboard. */
export function normalizeAuthRedirect(path) {
  if (!path || path === "/" || path === LANDING_PATH) {
    return DASHBOARD_ROOT;
  }

  if (
    path === "/dashboard/student" ||
    path === "/dashboard/admin" ||
    path === "/dashboard/super-admin"
  ) {
    return DASHBOARD_ROOT;
  }

  if (path.startsWith(DASHBOARD_ROOT)) {
    return path;
  }

  const publicPrefixes = ["/auth", "/observe", "/verify", "/maintenance", "/welcome"];
  if (publicPrefixes.some((prefix) => path === prefix || path.startsWith(`${prefix}/`))) {
    return path;
  }

  return `${DASHBOARD_ROOT}${path.startsWith("/") ? path : `/${path}`}`;
}

export function dashboardPath(...segments) {
  const tail = segments.filter(Boolean).join("/");
  return tail ? `${DASHBOARD_ROOT}/${tail}` : DASHBOARD_ROOT;
}
