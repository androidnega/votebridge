/** Legacy route redirects — Phase 32 backward compatibility. */

const LEGACY_APP_PREFIXES = [
  "profile",
  "forbidden",
  "error",
  "election-management",
  "security",
  "fraud",
  "results",
  "strongroom",
  "communications",
  "notifications",
  "ussd",
  "operations",
  "platform",
  "system-control",
  "settings",
  "biometrics",
  "analytics",
  "reports",
  "elections",
];

export const legacyRedirectRoutes = [
  { path: "/welcome", redirect: "/" },
  { path: "/welcome/:pathMatch(.*)*", redirect: "/" },
  { path: "/observe", redirect: "/" },
  { path: "/observe/:pathMatch(.*)*", redirect: "/" },
  { path: "/dashboard/student", redirect: "/dashboard" },
  { path: "/dashboard/admin", redirect: "/dashboard" },
  { path: "/dashboard/super-admin", redirect: "/dashboard" },
  ...LEGACY_APP_PREFIXES.flatMap((prefix) => [
    {
      path: `/${prefix}`,
      redirect: `/dashboard/${prefix}`,
    },
    {
      path: `/${prefix}/:pathMatch(.*)*`,
      redirect: (to) => `/dashboard/${prefix}/${to.params.pathMatch}`,
    },
  ]),
];
