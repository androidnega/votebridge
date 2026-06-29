/** In-page module navigation — Phase 25 consolidated workspaces. */

export const resultsNav = [
  { label: "Overview", to: "/results", exact: true },
  { label: "Certification", to: "/results/certification", roles: ["super_admin"] },
  { label: "Publication", to: "/results/publication", roles: ["super_admin"] },
  { label: "Archive", to: "/results/archive", roles: ["super_admin"] },
];

export const reportsNav = [
  { label: "Overview", to: "/reports", exact: true },
  { label: "Participation", to: "/reports/participation" },
  { label: "Turnout & results", to: "/reports/turnout" },
  { label: "Historical trends", to: "/reports/historical" },
  { label: "Export", to: "/reports/export" },
];

export const reportsAdvancedNav = [
  { label: "By students", to: "/reports/explore/students" },
  { label: "By departments", to: "/reports/explore/departments" },
  { label: "By faculties", to: "/reports/explore/faculties" },
  { label: "By programmes", to: "/reports/explore/programmes" },
  { label: "Security", to: "/reports/explore/security" },
  { label: "Fraud", to: "/reports/explore/fraud" },
  { label: "Communications", to: "/reports/explore/communications" },
  { label: "USSD", to: "/reports/explore/ussd" },
];

export const strongRoomNav = [
  { label: "Overview", to: "/strongroom", exact: true },
  { label: "Certification", to: "/results/certification", roles: ["super_admin"] },
  { label: "Investigations", to: "/strongroom/investigations" },
  { label: "Election integrity", to: "/strongroom/integrity" },
];

export const strongRoomInvestigationsNav = [
  { label: "Fraud", to: "/strongroom/investigations/fraud", exact: true },
  { label: "Audit trail", to: "/strongroom/investigations/audit" },
  { label: "Security timeline", to: "/strongroom/investigations/security" },
  { label: "Identity investigations", to: "/strongroom/investigations/identity" },
  { label: "Trusted devices", to: "/strongroom/investigations/trusted-devices" },
];

export const strongRoomIntegrityNav = [
  { label: "Overview", to: "/strongroom/integrity", exact: true },
  { label: "Chain of custody", to: "/strongroom/integrity/custody" },
];

export const settingsNav = [
  { label: "Overview", to: "/settings", exact: true },
  { label: "Institution", to: "/settings/institution-hub" },
  { label: "Voting", to: "/settings/voting-hub" },
  { label: "Security", to: "/settings/security-hub" },
  { label: "Advanced", to: "/settings/advanced-hub" },
];

export const analyticsNav = reportsNav;
export const systemControlNav = settingsNav;

export const communicationsNav = [
  { label: "Overview", to: "/communications", exact: true },
  { label: "Templates", to: "/communications/templates" },
  { label: "Providers", to: "/communications/providers" },
];
export const ussdNav = [
  { label: "Dashboard", to: "/ussd", exact: true },
  { label: "Sessions", to: "/ussd/sessions" },
];
export const operationsNav = [
  { label: "Overview", to: "/operations", exact: true },
  { label: "Live activity", to: "/operations/activity" },
  { label: "Election monitor", to: "/operations/elections" },
  { label: "System health", to: "/operations/health" },
];

export function filterNavByRole(items, role) {
  return items.filter((item) => !item.roles || item.roles.includes(role));
}
