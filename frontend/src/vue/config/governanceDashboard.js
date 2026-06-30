/** Phase 40 — Super Admin governance dashboard tokens (flat colors only). */

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

export const governanceQuickActions = [
  { id: "validate-ussd", label: "Validate USSD", route: "/dashboard/settings/integrations?focus=ussd" },
  { id: "validate-sms", label: "Validate SMS", route: "/dashboard/settings/integrations?focus=sms" },
  { id: "create-backup", label: "Create backup", route: "/dashboard/settings/backup" },
  { id: "maintenance", label: "Maintenance mode", route: "/dashboard/settings/maintenance" },
  { id: "settings", label: "Open settings", route: "/dashboard/settings" },
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
