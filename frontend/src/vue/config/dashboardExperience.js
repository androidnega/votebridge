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

/** Phase 62 — trimmed admin quick actions; election-scoped tools live in the workspace. */
export const adminQuickActionsPhase51 = [
  { id: "create", label: "Create Election", icon: "elections", route: "/dashboard/elections/create" },
  { id: "elections", label: "Manage Elections", icon: "elections", route: "/dashboard/elections" },
  { id: "results", label: "Results", icon: "results", route: "/dashboard/results" },
  { id: "reports", label: "Reports", icon: "analytics", route: "/dashboard/reports" },
];

/** Phase 62 — governance-level destinations only; no duplicate provider or audit shortcuts. */
export const governanceQuickActionsPhase51 = [
  { id: "certifications", label: "Results / Certification", icon: "results", route: "/dashboard/results?filter=certification" },
  { id: "reports", label: "Reports", icon: "analytics", route: "/dashboard/reports" },
  { id: "settings", label: "Settings", icon: "settings", route: "/dashboard/settings" },
  { id: "operations", label: "Operations", icon: "operations", route: "/dashboard/operations" },
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
