/** Phase 40 — Super Admin governance dashboard tokens (flat colors only). */

import { settingsRoutes as r } from "@/config/settingsRoutes";

export const governanceColors = {
  primary: "#2563EB",
  success: "#16A34A",
  warning: "#D97706",
  danger: "#DC2626",
  info: "#0891B2",
  background: "#F8FAFC",
  surface: "#FFFFFF",
  border: "#E5E7EB",
  textPrimary: "#1F2937",
  textSecondary: "#64748B",
};

export const governanceChartColors = [
  governanceColors.primary,
  governanceColors.info,
  governanceColors.success,
  governanceColors.warning,
  "#64748B",
  "#94A3B8",
];

/** Flat soft tints for dashboard tiles — no gradients. */
export const governanceSoftPalettes = [
  { bg: "#ECFEFF", border: "#A5F3FC", iconBg: "#CFFAFE", icon: "#0891B2", hoverBg: "#DDF4FF", hoverBorder: "#67E8F9" },
  { bg: "#EFF6FF", border: "#BFDBFE", iconBg: "#DBEAFE", icon: "#2563EB", hoverBg: "#DBEAFE", hoverBorder: "#93C5FD" },
  { bg: "#F5F3FF", border: "#DDD6FE", iconBg: "#EDE9FE", icon: "#7C3AED", hoverBg: "#EDE9FE", hoverBorder: "#C4B5FD" },
  { bg: "#FFFBEB", border: "#FDE68A", iconBg: "#FEF3C7", icon: "#D97706", hoverBg: "#FEF3C7", hoverBorder: "#FCD34D" },
  { bg: "#F8FAFC", border: "#E2E8F0", iconBg: "#F1F5F9", icon: "#475569", hoverBg: "#F1F5F9", hoverBorder: "#CBD5E1" },
  { bg: "#F0FDF4", border: "#BBF7D0", iconBg: "#DCFCE7", icon: "#16A34A", hoverBg: "#DCFCE7", hoverBorder: "#86EFAC" },
  { bg: "#EEF2FF", border: "#C7D2FE", iconBg: "#E0E7FF", icon: "#4F46E5", hoverBg: "#E0E7FF", hoverBorder: "#A5B4FC" },
  { bg: "#E8F3EF", border: "#C5E0D6", iconBg: "#D1EAE0", icon: "#1E5F46", hoverBg: "#D1EAE0", hoverBorder: "#9CC9B8" },
  { bg: "#FFF1F2", border: "#FECDD3", iconBg: "#FFE4E6", icon: "#E11D48", hoverBg: "#FFE4E6", hoverBorder: "#FDA4AF" },
  { bg: "#F0FDFA", border: "#99F6E4", iconBg: "#CCFBF1", icon: "#0F766E", hoverBg: "#CCFBF1", hoverBorder: "#5EEAD4" },
];

export const governanceQuickActionPaletteIndex = {
  "validate-ussd": 9,
  "validate-sms": 1,
  "create-backup": 2,
  maintenance: 3,
  settings: 4,
  results: 5,
  operations: 6,
};

export function getGovernanceSoftPalette(indexOrActionId) {
  if (typeof indexOrActionId === "string" && governanceQuickActionPaletteIndex[indexOrActionId] != null) {
    return governanceSoftPalettes[governanceQuickActionPaletteIndex[indexOrActionId]];
  }
  const idx = Number(indexOrActionId);
  if (Number.isNaN(idx)) {
    return governanceSoftPalettes[0];
  }
  return governanceSoftPalettes[((idx % governanceSoftPalettes.length) + governanceSoftPalettes.length) % governanceSoftPalettes.length];
}

export const governanceQuickActions = [
  { id: "validate-ussd", label: "Validate USSD", route: `${r.integrations.hub}?focus=ussd` },
  { id: "validate-sms", label: "Validate SMS", route: r.integrations.sms },
  { id: "create-backup", label: "Create backup", route: r.advanced.backup },
  { id: "maintenance", label: "Maintenance mode", route: r.advanced.maintenance },
  { id: "settings", label: "Open settings", route: r.overview },
  { id: "results", label: "Open results queue", route: "/dashboard/results?filter=certification" },
  { id: "operations", label: "Open operations center", route: "/dashboard/operations" },
];

export const infrastructureLabels = [
  { key: "database", label: "Database" },
  { key: "redis", label: "Redis" },
  { key: "websockets", label: "WebSocket" },
  { key: "sms", label: "SMS" },
  { key: "email", label: "Email" },
  { key: "ussd", label: "USSD" },
  { key: "storage", label: "Storage" },
];

export function healthToVariant(status) {
  const value = String(status || "unknown").toLowerCase();
  if (["healthy", "ok", "connected", "active", "running"].includes(value)) return "healthy";
  if (["warning", "degraded", "slow"].includes(value)) return "warning";
  if (["critical", "error", "failed", "disconnected", "down"].includes(value)) return "critical";
  return "unknown";
}

export function healthLabel(variant) {
  return (
    {
      healthy: "Healthy",
      warning: "Warning",
      critical: "Critical",
      unknown: "Unknown",
    }[variant] || "Unknown"
  );
}

export function formatUptime(seconds) {
  if (seconds == null) return "—";
  const days = Math.floor(seconds / 86400);
  const hours = Math.floor((seconds % 86400) / 3600);
  if (days > 0) return `${days}d ${hours}h`;
  const mins = Math.floor((seconds % 3600) / 60);
  return hours > 0 ? `${hours}h ${mins}m` : `${mins}m`;
}
