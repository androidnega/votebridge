/** In-page module navigation — Phase 25 consolidated workspaces. */

export const resultsNav = [
  { label: "Overview", to: "/dashboard/results", exact: true },
  { label: "Certification", to: "/dashboard/results/certification", roles: ["super_admin"] },
  { label: "Publication", to: "/dashboard/results/publication", roles: ["super_admin"] },
  { label: "Archive", to: "/dashboard/results/archive", roles: ["super_admin"] },
];

export const reportsNav = [
  { label: "Overview", to: "/dashboard/reports", exact: true },
  { label: "Participation", to: "/dashboard/reports/participation" },
  { label: "Turnout & results", to: "/dashboard/reports/turnout" },
  { label: "Historical trends", to: "/dashboard/reports/historical" },
  { label: "Export", to: "/dashboard/reports/export" },
];

export const reportsAdvancedNav = [
  { label: "By students", to: "/dashboard/reports/explore/students" },
  { label: "By departments", to: "/dashboard/reports/explore/departments" },
  { label: "By faculties", to: "/dashboard/reports/explore/faculties" },
  { label: "By programmes", to: "/dashboard/reports/explore/programmes" },
  { label: "Security", to: "/dashboard/reports/explore/security" },
  { label: "Fraud", to: "/dashboard/reports/explore/fraud" },
  { label: "Communications", to: "/dashboard/reports/explore/communications" },
  { label: "USSD", to: "/dashboard/reports/explore/ussd" },
];

export const strongRoomNav = [
  { label: "Overview", to: "/dashboard/strongroom", exact: true },
  { label: "Certification", to: "/dashboard/results/certification", roles: ["super_admin"] },
  { label: "Investigations", to: "/dashboard/strongroom/investigations" },
  { label: "Election integrity", to: "/dashboard/strongroom/integrity" },
];

export const strongRoomInvestigationsNav = [
  { label: "Fraud", to: "/dashboard/strongroom/investigations/fraud", exact: true },
  { label: "Audit trail", to: "/dashboard/strongroom/investigations/audit" },
  { label: "Security timeline", to: "/dashboard/strongroom/investigations/security" },
  { label: "Identity investigations", to: "/dashboard/strongroom/investigations/identity" },
  { label: "Trusted devices", to: "/dashboard/strongroom/investigations/trusted-devices" },
];

export const strongRoomIntegrityNav = [
  { label: "Overview", to: "/dashboard/strongroom/integrity", exact: true },
  { label: "Chain of custody", to: "/dashboard/strongroom/integrity/custody" },
];

export const settingsNav = [
  { label: "Overview", to: "/dashboard/settings", exact: true },
  { label: "Institution", to: "/dashboard/settings/institution-hub" },
  { label: "Voting", to: "/dashboard/settings/voting-hub" },
  { label: "Security", to: "/dashboard/settings/security-hub" },
  { label: "Advanced", to: "/dashboard/settings/advanced-hub" },
];

export const analyticsNav = reportsNav;
export const systemControlNav = settingsNav;

export const communicationsNav = [
  { label: "Overview", to: "/dashboard/communications", exact: true },
  { label: "Templates", to: "/dashboard/communications/templates" },
  { label: "Providers", to: "/dashboard/communications/providers" },
];
export const ussdNav = [
  { label: "Dashboard", to: "/dashboard/ussd", exact: true },
  { label: "Sessions", to: "/dashboard/ussd/sessions" },
];
export const operationsNav = [
  { label: "Overview", to: "/dashboard/operations", exact: true },
  { label: "Live activity", to: "/dashboard/operations/activity" },
  { label: "Election monitor", to: "/dashboard/operations/elections" },
  { label: "System health", to: "/dashboard/operations/health" },
];

export function filterNavByRole(items, role) {
  return items.filter((item) => !item.roles || item.roles.includes(role));
}
