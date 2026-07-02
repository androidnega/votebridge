/** Primary sidebar navigation — Phase 62 role-focused IA. */

import { dashboardPath } from "@/config/routes";

const studentNav = [
  { name: "Dashboard", to: dashboardPath(), icon: "home" },
  { name: "Elections", to: dashboardPath("my-elections"), icon: "elections", key: "elections" },
  { name: "Notifications", to: dashboardPath("notifications"), icon: "notifications" },
];

const adminNav = [
  { name: "Dashboard", to: dashboardPath(), icon: "home" },
  { name: "Elections", to: dashboardPath("elections"), icon: "elections", key: "elections" },
  { name: "Results", to: dashboardPath("results"), icon: "results" },
  { name: "Reports", to: dashboardPath("reports"), icon: "analytics" },
];

const superAdminNav = [
  { name: "Dashboard", to: dashboardPath(), icon: "home" },
  { name: "Results", to: dashboardPath("results"), icon: "results" },
  { name: "Reports", to: dashboardPath("reports"), icon: "analytics" },
  { name: "Settings", to: dashboardPath("settings"), icon: "settings", roles: ["super_admin"] },
];

export function getSidebarNav(role) {
  if (role === "super_admin") return superAdminNav;
  if (role === "admin") return adminNav;
  return studentNav;
}
