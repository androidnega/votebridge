/** Primary sidebar navigation — Phase 23 consolidated UX. */

function filterByRole(items, role) {
  return items.filter((item) => !item.roles || item.roles.includes(role));
}

function filterChildren(items, role) {
  return items.map((item) => {
    if (!item.children) return item;
    const children = filterByRole(item.children, role);
    if (!children.length) return { ...item, children: undefined };
    return { ...item, children };
  });
}

const electionManagementChildren = [
  { name: "Elections", to: "/elections", exact: true },
  { name: "Candidates", to: "/election-management/candidates" },
  { name: "Positions", to: "/election-management/positions" },
  { name: "Voter eligibility", to: "/election-management/eligibility" },
];

const studentNav = [
  { name: "Dashboard", to: "/", icon: "home" },
  { name: "Elections", to: "/elections", icon: "elections" },
  { name: "Notifications", to: "/notifications", icon: "notifications" },
  { name: "Profile", to: "/profile", icon: "profile" },
];

const adminNav = [
  { name: "Dashboard", to: "/", icon: "home" },
  {
    name: "Election management",
    to: "/elections",
    icon: "elections",
    key: "election-management",
    children: electionManagementChildren,
  },
  { name: "Results", to: "/results", icon: "results" },
  { name: "Reports", to: "/reports", icon: "analytics" },
  { name: "Profile", to: "/profile", icon: "profile" },
];

const superAdminNav = [
  { name: "Dashboard", to: "/", icon: "home" },
  {
    name: "Election management",
    to: "/elections",
    icon: "elections",
    key: "election-management",
    children: electionManagementChildren,
  },
  { name: "Results", to: "/results", icon: "results" },
  { name: "Reports", to: "/reports", icon: "analytics" },
  { name: "Strong room", to: "/strongroom", icon: "strongroom", roles: ["super_admin"] },
  { name: "Settings", to: "/settings", icon: "settings", roles: ["super_admin"] },
  { name: "Profile", to: "/profile", icon: "profile" },
];

export function getSidebarNav(role) {
  if (role === "super_admin") return filterChildren(superAdminNav, role);
  if (role === "admin") return filterChildren(adminNav, role);
  return studentNav;
}

export function filterSidebarByRole(items, role) {
  return filterByRole(items, role);
}
