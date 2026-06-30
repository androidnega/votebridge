/** Phase 42 — Election Administrator Command Center tokens (flat colors only). */

export const commandCenterColors = {
  primary: "#2563EB",
  success: "#16A34A",
  warning: "#D97706",
  danger: "#DC2626",
  background: "#F8FAFC",
  surface: "#FFFFFF",
  border: "#E5E7EB",
  textPrimary: "#1F2937",
  textSecondary: "#64748B",
};

export const commandChartColors = [commandCenterColors.primary, commandCenterColors.success];

export const electionLifecycleStages = [
  { id: "draft", label: "Draft" },
  { id: "scheduled", label: "Scheduled" },
  { id: "open", label: "Open" },
  { id: "closed", label: "Closed" },
  { id: "certified", label: "Certified" },
  { id: "published", label: "Published" },
];

export const commandQuickActions = [
  { id: "create", label: "Create Election", route: "/dashboard/elections/create" },
  { id: "candidates", label: "Manage Candidates", routeKey: "candidates" },
  { id: "eligibility", label: "Manage Eligibility", routeKey: "eligibility" },
  { id: "export", label: "Export Voter List", routeKey: "eligibility" },
  { id: "reports", label: "Open Reports", route: "/dashboard/reports" },
];

export const adminSidebarNav = [
  { name: "Dashboard", to: "/dashboard", icon: "home" },
  {
    name: "Election Management",
    to: "/dashboard/elections",
    icon: "elections",
    key: "election-management",
    children: [
      { name: "Elections", to: "/dashboard/elections", exact: true },
      { name: "Candidates", to: "/dashboard/election-management/candidates" },
      { name: "Positions", to: "/dashboard/election-management/positions" },
      { name: "Voter Eligibility", to: "/dashboard/election-management/eligibility" },
    ],
  },
  { name: "Control Room", to: "/dashboard/control-room", icon: "operations", key: "control-room" },
  { name: "Results", to: "/dashboard/results", icon: "results" },
  { name: "Reports", to: "/dashboard/reports", icon: "analytics" },
  { name: "Profile", to: "/dashboard/profile", icon: "profile" },
];

const ELECTION_ACTIVITY_EVENTS = new Set([
  "ballot_submitted",
  "election_opened",
  "election_closed",
  "election_paused",
  "fraud_case_created",
  "fraud_case_resolved",
  "fraud_case_escalated",
]);

export function isElectionActivityItem(item) {
  if (!item) return false;
  if (item.event_type && ELECTION_ACTIVITY_EVENTS.has(item.event_type)) return true;
  const text = `${item.title || ""} ${item.description || ""}`.toLowerCase();
  return /election|ballot|vote|turnout|candidate nomination|eligibility/.test(text);
}

export function resolveLifecycleStage(election, resultRow) {
  if (!election) return "draft";
  const status = election.status || election.election_status;
  if (status === "open" || status === "paused") return "open";
  if (status === "scheduled") return "scheduled";
  if (status === "draft") return "draft";
  if (status === "closed" || status === "archived") {
    if (resultRow?.result_status === "published") return "published";
    if (resultRow?.result_status === "certified") return "certified";
    return "closed";
  }
  return "draft";
}

export function resolveWorkspaceRoute(electionUuid, section) {
  if (!electionUuid) return "/dashboard/elections";
  return `/dashboard/elections/${electionUuid}/${section}`;
}
