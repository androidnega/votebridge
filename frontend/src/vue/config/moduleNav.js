/** In-page module navigation — Phase 23 consolidated workspaces. */

export const resultsNav = [
  { label: "Overview", to: "/results", exact: true },
  { label: "Certification", to: "/results/certification", roles: ["super_admin"] },
  { label: "Publication", to: "/results/publication", roles: ["super_admin"] },
  { label: "Archive", to: "/results/archive", roles: ["super_admin"] },
];

export const electionManagementNav = [
  { label: "Elections", to: "/elections", exact: true },
  { label: "Candidates", to: "/election-management/candidates" },
  { label: "Positions", to: "/election-management/positions" },
  { label: "Voter eligibility", to: "/election-management/eligibility" },
];

export const reportsNav = [
  { label: "Overview", to: "/reports", exact: true },
  { label: "Participation", to: "/reports/participation" },
  { label: "Turnout", to: "/reports/turnout" },
  { label: "Results", to: "/reports/results" },
  { label: "Historical trends", to: "/reports/historical" },
  { label: "Export reports", to: "/reports/export" },
];

/** Advanced analytics — drill-down from Reports overview. */
export const reportsAdvancedNav = [
  { label: "Students", to: "/analytics/students" },
  { label: "Departments", to: "/analytics/departments" },
  { label: "Faculties", to: "/analytics/faculties" },
  { label: "Programmes", to: "/analytics/programmes" },
  { label: "Security", to: "/analytics/security" },
  { label: "Fraud", to: "/analytics/fraud" },
  { label: "Operations", to: "/analytics/operations" },
  { label: "Communications", to: "/analytics/communications" },
  { label: "USSD", to: "/analytics/ussd" },
  { label: "Strong room", to: "/analytics/strongroom" },
];

export const strongRoomNav = [
  { label: "Vote integrity", to: "/strongroom", exact: true },
  { label: "Certification", to: "/strongroom/certification", roles: ["super_admin"] },
  { label: "Audit trail", to: "/strongroom/audit" },
  { label: "Fraud investigation", to: "/strongroom/fraud" },
  { label: "Chain of custody", to: "/strongroom/custody" },
  { label: "Identity assurance", to: "/strongroom/identity" },
  { label: "Trusted devices", to: "/strongroom/trusted-devices" },
  { label: "Security timeline", to: "/strongroom/security" },
  { label: "Evidence export", to: "/strongroom/export" },
];

export const settingsNav = [
  { label: "Overview", to: "/settings", exact: true },
  { label: "Institution", to: "/settings/institution" },
  { label: "Authentication", to: "/settings/authentication" },
  { label: "Communication providers", to: "/settings/providers" },
  { label: "Voting channels", to: "/settings/voting-channels" },
  { label: "Maintenance", to: "/settings/maintenance" },
  { label: "Feature flags", to: "/settings/feature-flags" },
  { label: "Backup", to: "/settings/backup" },
  { label: "System configuration", to: "/settings/system" },
  { label: "Identity assurance", to: "/settings/identity-assurance" },
  { label: "Security policies", to: "/settings/security" },
  { label: "API & integrations", to: "/settings/api" },
];

/** Legacy nav exports — kept for backward-compatible deep links. */
export const analyticsNav = reportsNav;
export const systemControlNav = settingsNav;
export const communicationsNav = [
  { label: "Overview", to: "/communications", exact: true },
  { label: "Templates", to: "/communications/templates" },
  { label: "Providers", to: "/communications/providers" },
  { label: "Platform logs", to: "/platform/logs?tab=communications" },
];
export const ussdNav = [
  { label: "Dashboard", to: "/ussd", exact: true },
  { label: "Sessions", to: "/ussd/sessions" },
  { label: "Platform logs", to: "/platform/logs?tab=ussd" },
];
export const operationsNav = [
  { label: "Overview", to: "/operations", exact: true },
  { label: "Live activity", to: "/operations/activity" },
  { label: "Election monitor", to: "/operations/elections" },
  { label: "System health", to: "/operations/health" },
  { label: "Platform logs", to: "/platform/logs?tab=operations" },
];
export const platformLogsNav = [
  { label: "All logs", to: "/platform/logs", exact: true },
  { label: "Operations", to: "/platform/logs?tab=operations" },
  { label: "Communications", to: "/platform/logs?tab=communications" },
  { label: "USSD", to: "/platform/logs?tab=ussd" },
];

export function filterNavByRole(items, role) {
  return items.filter((item) => !item.roles || item.roles.includes(role));
}
