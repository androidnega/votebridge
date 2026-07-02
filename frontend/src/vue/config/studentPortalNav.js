import { dashboardPath } from "@/config/routes";

/** Phase 62 — student primary nav: Dashboard, Elections, Notifications only. Profile is header-only. */
export const studentPrimaryNav = [
  { name: "Dashboard", to: dashboardPath(), icon: "home", key: "dashboard" },
  { name: "Elections", to: dashboardPath("my-elections"), icon: "elections", key: "elections" },
  { name: "Notifications", to: dashboardPath("notifications"), icon: "notifications", key: "notifications" },
];

export const studentSupportNav = [
  {
    name: "Help centre",
    to: "/auth/info/help",
    icon: "notifications",
    key: "help",
  },
];
