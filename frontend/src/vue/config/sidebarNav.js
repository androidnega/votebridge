/** Primary sidebar navigation — Phase 32 universal dashboard namespace. */

import { dashboardPath } from "@/config/routes";

const studentNav = [
  { name: "Dashboard", to: dashboardPath(), icon: "home" },
  { name: "Elections", to: dashboardPath("elections"), icon: "elections" },
  { name: "Notifications", to: dashboardPath("notifications"), icon: "notifications" },
  { name: "Profile", to: dashboardPath("profile"), icon: "profile" },
];

const adminNav = [
  { name: "Dashboard", to: dashboardPath(), icon: "home" },
  { name: "Election workspace", to: dashboardPath("elections"), icon: "elections" },
  { name: "Results", to: dashboardPath("results"), icon: "results" },
  { name: "Reports", to: dashboardPath("reports"), icon: "analytics" },
  { name: "Profile", to: dashboardPath("profile"), icon: "profile" },
];

const superAdminNav = [
  { name: "Dashboard", to: dashboardPath(), icon: "home" },
  { name: "Results", to: dashboardPath("results"), icon: "results" },
  { name: "Reports", to: dashboardPath("reports"), icon: "analytics" },
  { name: "Settings", to: dashboardPath("settings"), icon: "settings", roles: ["super_admin"] },
  { name: "Profile", to: dashboardPath("profile"), icon: "profile" },
];

export function getSidebarNav(role) {
  if (role === "super_admin") return superAdminNav;
  if (role === "admin") return adminNav;
  return studentNav;
}
