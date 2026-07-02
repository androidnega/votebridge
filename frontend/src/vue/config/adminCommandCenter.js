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

/** Soft flat palettes for command center KPI cards. */
export const commandKpiPalettes = {
  "active-elections": {
    bg: "#EFF6FF",
    border: "#BFDBFE",
    iconBg: "#DBEAFE",
    icon: "#2563EB",
    valueColor: "#1E40AF",
  },
  turnout: {
    bg: "#F0FDF4",
    border: "#BBF7D0",
    iconBg: "#DCFCE7",
    icon: "#16A34A",
    valueColor: "#15803D",
  },
  "votes-eligible": {
    bg: "#F5F3FF",
    border: "#DDD6FE",
    iconBg: "#EDE9FE",
    icon: "#7C3AED",
    valueColor: "#5B21B6",
  },
  "pending-tasks": {
    bg: "#FFFBEB",
    border: "#FDE68A",
    iconBg: "#FEF3C7",
    icon: "#D97706",
    valueColor: "#B45309",
  },
  "pending-tasks-clear": {
    bg: "#F0FDF4",
    border: "#BBF7D0",
    iconBg: "#DCFCE7",
    icon: "#16A34A",
    valueColor: "#15803D",
  },
  "election-status": {
    bg: "#F8FAFC",
    border: "#E2E8F0",
    iconBg: "#F1F5F9",
    icon: "#64748B",
    valueColor: "#1F2937",
  },
  "election-status-open": {
    bg: "#F0FDF4",
    border: "#BBF7D0",
    iconBg: "#DCFCE7",
    icon: "#16A34A",
    valueColor: "#15803D",
  },
  "election-status-paused": {
    bg: "#FFFBEB",
    border: "#FDE68A",
    iconBg: "#FEF3C7",
    icon: "#D97706",
    valueColor: "#B45309",
  },
};

export const commandKpiHealthAccents = {
  healthy: "#16A34A",
  attention: "#D97706",
  critical: "#DC2626",
  unknown: "#94A3B8",
};

export function getCommandKpiPalette(id, healthStatus = "unknown") {
  if (id === "pending-tasks" && healthStatus === "healthy") {
    return commandKpiPalettes["pending-tasks-clear"];
  }
  if (id === "election-status") {
    if (healthStatus === "healthy") return commandKpiPalettes["election-status-open"];
    if (healthStatus === "attention") return commandKpiPalettes["election-status-paused"];
  }
  return commandKpiPalettes[id] || commandKpiPalettes["election-status"];
}

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
  { id: "elections", label: "Manage Elections", route: "/dashboard/elections" },
  { id: "results", label: "Results", route: "/dashboard/results" },
  { id: "reports", label: "Reports", route: "/dashboard/reports" },
];

/** @deprecated Phase 62 — use getSidebarNav from sidebarNav.js instead. */
export const adminSidebarNav = [
  { name: "Dashboard", to: "/dashboard", icon: "home" },
  { name: "Elections", to: "/dashboard/elections", icon: "elections", key: "elections" },
  { name: "Results", to: "/dashboard/results", icon: "results" },
  { name: "Reports", to: "/dashboard/reports", icon: "analytics" },
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
