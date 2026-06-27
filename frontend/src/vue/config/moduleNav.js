/** Sub-navigation definitions for multi-page modules. */

export const resultsNav = [
  { label: "Overview", to: "/results", exact: true },
  { label: "Certification", to: "/results/certification", roles: ["super_admin"] },
  { label: "Publication", to: "/results/publication", roles: ["super_admin"] },
  { label: "Archive", to: "/results/archive", roles: ["super_admin"] },
];

export const communicationsNav = [
  { label: "Dashboard", to: "/communications", exact: true },
  { label: "Delivery logs", to: "/communications/logs" },
  { label: "Queue monitor", to: "/communications/queue" },
  { label: "Providers", to: "/communications/providers" },
  { label: "Templates", to: "/communications/templates" },
  { label: "Test center", to: "/communications/test" },
];

export const ussdNav = [
  { label: "Dashboard", to: "/ussd", exact: true },
  { label: "Sessions", to: "/ussd/sessions" },
  { label: "Activity logs", to: "/ussd/logs" },
];

export const operationsNav = [
  { label: "Overview", to: "/operations", exact: true },
  { label: "Live Activity", to: "/operations/activity" },
  { label: "System Health", to: "/operations/health" },
  { label: "Infrastructure", to: "/operations/infrastructure" },
  { label: "Election Monitor", to: "/operations/elections" },
  { label: "Communications", to: "/operations/communications" },
  { label: "Users & Sessions", to: "/operations/sessions" },
  { label: "Queues", to: "/operations/queues" },
  { label: "Performance", to: "/operations/performance" },
  { label: "Logs", to: "/operations/logs" },
];

export const systemControlNav = [
  { label: "Overview", to: "/system-control", exact: true },
  { label: "Institution", to: "/system-control/institution" },
  { label: "Election Policies", to: "/system-control/election-policies" },
  { label: "Authentication", to: "/system-control/authentication" },
  { label: "Providers", to: "/system-control/providers" },
  { label: "SMS", to: "/system-control/sms" },
  { label: "USSD", to: "/system-control/ussd" },
  { label: "Email", to: "/system-control/email" },
  { label: "Notifications", to: "/system-control/notifications" },
  { label: "Security", to: "/system-control/security" },
  { label: "Feature Flags", to: "/system-control/feature-flags" },
  { label: "Branding", to: "/system-control/branding" },
  { label: "API", to: "/system-control/api" },
  { label: "Maintenance", to: "/system-control/maintenance" },
  { label: "Storage", to: "/system-control/storage" },
  { label: "Backup", to: "/system-control/backup" },
  { label: "Audit", to: "/system-control/audit" },
  { label: "Environment", to: "/system-control/environment" },
  { label: "Runtime", to: "/system-control/runtime" },
  { label: "License", to: "/system-control/license" },
  { label: "About", to: "/system-control/about" },
];

export const analyticsNav = [
  { label: "Overview", to: "/analytics", exact: true },
  { label: "Elections", to: "/analytics/elections" },
  { label: "Participation", to: "/analytics/participation" },
  { label: "Students", to: "/analytics/students" },
  { label: "Departments", to: "/analytics/departments" },
  { label: "Faculties", to: "/analytics/faculties" },
  { label: "Programmes", to: "/analytics/programmes" },
  { label: "Security", to: "/analytics/security" },
  { label: "Fraud", to: "/analytics/fraud" },
  { label: "Operations", to: "/analytics/operations" },
  { label: "Communications", to: "/analytics/communications" },
  { label: "USSD", to: "/analytics/ussd" },
  { label: "Strongroom", to: "/analytics/strongroom" },
  { label: "Historical", to: "/analytics/historical" },
  { label: "Reports", to: "/analytics/reports" },
];

export function filterNavByRole(items, role) {
  return items.filter((item) => !item.roles || item.roles.includes(role));
}
