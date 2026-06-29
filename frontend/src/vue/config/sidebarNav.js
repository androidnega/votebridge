/** Primary sidebar navigation — Phase 25 election workspace UX. */

const studentNav = [
  { name: "Dashboard", to: "/", icon: "home" },
  { name: "Elections", to: "/elections", icon: "elections" },
  { name: "Notifications", to: "/notifications", icon: "notifications" },
  { name: "Profile", to: "/profile", icon: "profile" },
];

const adminNav = [
  { name: "Dashboard", to: "/", icon: "home" },
  { name: "Election workspace", to: "/elections", icon: "elections" },
  { name: "Results", to: "/results", icon: "results" },
  { name: "Reports", to: "/reports", icon: "analytics" },
  { name: "Profile", to: "/profile", icon: "profile" },
];

const superAdminNav = [
  { name: "Dashboard", to: "/", icon: "home" },
  { name: "Election workspace", to: "/elections", icon: "elections" },
  { name: "Results", to: "/results", icon: "results" },
  { name: "Reports", to: "/reports", icon: "analytics" },
  { name: "Strong room", to: "/strongroom", icon: "strongroom", roles: ["super_admin"] },
  { name: "Settings", to: "/settings", icon: "settings", roles: ["super_admin"] },
  { name: "Profile", to: "/profile", icon: "profile" },
];

export function getSidebarNav(role) {
  if (role === "super_admin") return superAdminNav;
  if (role === "admin") return adminNav;
  return studentNav;
}
