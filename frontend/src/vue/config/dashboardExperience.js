/** Phase 51 — Modern election dashboard design tokens (flat, light, institutional). */

export const dashboardColors = {
  background: "#F9FAFB",
  surface: "#FFFFFF",
  border: "#E5E7EB",
  primaryGreen: "#166534",
  blueAccent: "#2563EB",
  amber: "#D97706",
  red: "#DC2626",
  textPrimary: "#1F2937",
  textSecondary: "#6B7280",
};

export const dashboardChartColors = [
  dashboardColors.blueAccent,
  dashboardColors.primaryGreen,
  dashboardColors.amber,
  "#64748B",
  dashboardColors.red,
  "#0891B2",
];

export const chartTimeRanges = [
  { id: "today", label: "Today" },
  { id: "7d", label: "7 Days" },
  { id: "30d", label: "30 Days" },
  { id: "period", label: "Election Period" },
];

export const adminQuickActionsPhase51 = [
  { id: "create", label: "Create Election", icon: "elections", route: "/dashboard/elections/create" },
  { id: "candidates", label: "Manage Candidates", icon: "profile", routeKey: "candidates" },
  { id: "positions", label: "Manage Positions", icon: "tasks", routeKey: "positions" },
  { id: "eligibility", label: "Manage Eligibility", icon: "profile", routeKey: "eligibility" },
  { id: "reports", label: "Open Reports", icon: "analytics", route: "/dashboard/reports" },
  { id: "import", label: "Import Students", icon: "profile", route: "/dashboard/election-management/eligibility" },
];

export const governanceQuickActionsPhase51 = [
  { id: "settings", label: "Settings", icon: "settings", route: "/dashboard/settings" },
  { id: "certifications", label: "Review Certifications", icon: "results", route: "/dashboard/results?filter=certification" },
  { id: "audit", label: "Audit Logs", icon: "analytics", route: "/dashboard/platform-logs" },
  { id: "health", label: "System Health", icon: "operations", route: "/dashboard/operations" },
  { id: "providers", label: "Communication Providers", icon: "communications", route: "/dashboard/settings/integrations/sms" },
  { id: "users", label: "Platform Users", icon: "profile", route: "/dashboard/settings/security/election-administration" },
];

export function greetingForHour(hour = new Date().getHours()) {
  if (hour < 12) return "Good morning";
  if (hour < 17) return "Good afternoon";
  return "Good evening";
}

export function isSameCalendarDay(a, b = new Date()) {
  const left = a instanceof Date ? a : new Date(a);
  if (Number.isNaN(left.getTime())) return false;
  return (
    left.getFullYear() === b.getFullYear()
    && left.getMonth() === b.getMonth()
    && left.getDate() === b.getDate()
  );
}

export function sliceTrendByRange(points = [], rangeId) {
  if (!points.length) return points;
  if (rangeId === "today") return points.slice(-24);
  if (rangeId === "7d") return points.slice(-168);
  if (rangeId === "30d") return points.slice(-720);
  return points;
}
