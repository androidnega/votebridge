/** System Control hub — grouped navigation and quick actions. */

import { settingsRoutes as r } from "@/config/settingsRoutes";

export const systemControlSections = [
  {
    id: "institution",
    title: "Institution & branding",
    description: "Identity, contact details, and portal appearance.",
    icon: "profile",
    items: [
      { label: "Institution profile", to: r.institution.profile, description: "Name, campus, and election office contacts" },
      { label: "Branding", to: r.institution.branding, description: "Logos, colours, and login panel assets" },
    ],
  },
  {
    id: "platform-defaults",
    title: "Platform defaults",
    description: "System-wide defaults for new elections and platform behaviour.",
    icon: "settings",
    items: [
      { label: "Platform defaults", to: r.advanced.platformDefaults, description: "Timezone, OTP expiry, session timeout, retention" },
      { label: "Feature flags", to: r.advanced.featureFlags, description: "Toggle experimental or phased capabilities" },
    ],
  },
  {
    id: "election-administration",
    title: "Election administration",
    description: "Manage Election Administrators — not individual elections.",
    icon: "profile",
    items: [
      { label: "Election administrators", to: r.security.electionAdministration, description: "List, create, and suspend platform election officers" },
      { label: "Administrator activity", to: `${r.security.electionAdministration}#activity`, description: "Sign-in and governance actions for election officers" },
    ],
  },
  {
    id: "integrations",
    title: "Integrations",
    description: "Communication providers, cache, and realtime infrastructure.",
    icon: "communications",
    items: [
      { label: "Integration health", to: r.integrations.hub, description: "SMS, USSD, email, Redis, and WebSockets" },
      { label: "Notifications", to: r.integrations.notifications, description: "Templates and delivery rules" },
    ],
  },
  {
    id: "strongroom-config",
    title: "Strong room configuration",
    description: "Configure the secure vault before elections — vault access is separate.",
    icon: "strongroom",
    items: [
      { label: "Vault policies", to: r.security.strongroom, description: "Committee, credentials, rotation, and audit policies" },
    ],
  },
  {
    id: "security",
    title: "Security & access",
    description: "Authentication, identity assurance, and platform hardening.",
    icon: "security",
    items: [
      { label: "Authentication", to: r.security.authentication, description: "OTP, sessions, and login policies" },
      { label: "Identity assurance", to: r.security.identityAssurance, description: "Biometrics and step-up verification" },
      { label: "Security settings", to: r.security.policies, description: "Rate limits, lockouts, and alerts" },
      { label: "API management", to: r.security.api, description: "Keys, webhooks, and integration limits" },
      { label: "Audit settings", to: r.security.audit, description: "Retention and audit log policies" },
    ],
  },
  {
    id: "operations",
    title: "Operations & reliability",
    description: "Maintenance, backups, storage, and runtime.",
    icon: "operations",
    items: [
      { label: "Maintenance mode", to: r.advanced.maintenance, description: "Schedule downtime and user messaging" },
      { label: "Backup & recovery", to: r.advanced.backup, description: "Create and verify platform backups" },
      { label: "Storage", to: r.advanced.storage, description: "Disk usage and cleanup" },
      { label: "Operational data reset", to: r.advanced.dataReset, description: "Clear elections, votes, and results (Super Admin)" },
      { label: "Environment", to: r.advanced.environment, description: "Deployment and runtime context" },
      { label: "Runtime config", to: r.advanced.runtime, description: "Live tunable system parameters" },
    ],
  },
  {
    id: "about",
    title: "License & about",
    description: "Version information and support contacts.",
    icon: "help",
    items: [
      { label: "License", to: r.advanced.license, description: "Edition and support entitlements" },
      { label: "About VoteBridge", to: r.advanced.about, description: "Release notes and credits" },
    ],
  },
];

/** Flat soft tints for settings overview cards — no gradients. */
export const settingsSoftPalettes = {
  institution: {
    bg: "#E8F3EF",
    border: "#C5E0D6",
    iconBg: "#D1EAE0",
    icon: "#1E5F46",
    hoverBg: "#D1EAE0",
    accent: "#1E5F46",
  },
  "platform-defaults": {
    bg: "#EFF6FF",
    border: "#BFDBFE",
    iconBg: "#DBEAFE",
    icon: "#2563EB",
    hoverBg: "#DBEAFE",
    accent: "#2563EB",
  },
  "election-administration": {
    bg: "#EEF2FF",
    border: "#C7D2FE",
    iconBg: "#E0E7FF",
    icon: "#4F46E5",
    hoverBg: "#E0E7FF",
    accent: "#4F46E5",
  },
  integrations: {
    bg: "#ECFEFF",
    border: "#A5F3FC",
    iconBg: "#CFFAFE",
    icon: "#0891B2",
    hoverBg: "#CFFAFE",
    accent: "#0891B2",
  },
  "strongroom-config": {
    bg: "#FFF1F2",
    border: "#FECDD3",
    iconBg: "#FFE4E6",
    icon: "#BE123C",
    hoverBg: "#FFE4E6",
    accent: "#BE123C",
  },
  security: {
    bg: "#FFFBEB",
    border: "#FDE68A",
    iconBg: "#FEF3C7",
    icon: "#B45309",
    hoverBg: "#FEF3C7",
    accent: "#B45309",
  },
  operations: {
    bg: "#F0FDF4",
    border: "#BBF7D0",
    iconBg: "#DCFCE7",
    icon: "#15803D",
    hoverBg: "#DCFCE7",
    accent: "#15803D",
  },
  about: {
    bg: "#F5F3FF",
    border: "#DDD6FE",
    iconBg: "#EDE9FE",
    icon: "#7C3AED",
    hoverBg: "#EDE9FE",
    accent: "#7C3AED",
  },
  "quick-actions": {
    bg: "#F8FAFC",
    border: "#E2E8F0",
    iconBg: "#F1F5F9",
    icon: "#475569",
    hoverBg: "#F1F5F9",
    accent: "#475569",
  },
  maintenance: {
    bg: "#FFFBEB",
    border: "#FDE68A",
    iconBg: "#FEF3C7",
    icon: "#D97706",
    hoverBg: "#FEF3C7",
    accent: "#D97706",
  },
  activity: {
    bg: "#EFF6FF",
    border: "#BFDBFE",
    iconBg: "#DBEAFE",
    icon: "#2563EB",
    hoverBg: "#DBEAFE",
    accent: "#2563EB",
  },
};

export const settingsQuickActionPaletteKeys = {
  maintenance_enable: "maintenance",
  validate_sms: "integrations",
  validate_ussd: "integrations",
  create_backup: "operations",
  restore_backup: "operations",
  export_audit: "activity",
  open_operations: "operations",
};

export function getSettingsSectionPalette(sectionId) {
  return settingsSoftPalettes[sectionId] || settingsSoftPalettes["platform-defaults"];
}

export function getSettingsQuickActionPalette(action) {
  const key = settingsQuickActionPaletteKeys[action] || "quick-actions";
  return settingsSoftPalettes[key] || settingsSoftPalettes["quick-actions"];
}

export const quickActionRoutes = {
  maintenance_enable: r.advanced.maintenance,
  validate_sms: r.integrations.sms,
  validate_ussd: `${r.integrations.hub}?focus=ussd`,
  create_backup: r.advanced.backup,
  restore_backup: r.advanced.backup,
  export_audit: "/dashboard/platform/logs",
  open_operations: "/dashboard/operations",
};

export const infrastructureServices = [
  { key: "database_status", label: "Database", icon: "strongroom" },
  { key: "redis_status", label: "Redis", icon: "bolt" },
  { key: "websocket_status", label: "WebSockets", icon: "operations" },
  { key: "sms_provider", label: "SMS", icon: "communications" },
  { key: "email_provider", label: "Email", icon: "inbox" },
  { key: "ussd_provider", label: "USSD", icon: "ussd" },
];

/** Map provider connection strings to health badge variants. */
export function normalizeHealthStatus(status) {
  if (!status) return "unknown";
  const value = String(status).toLowerCase();
  if (["healthy", "ok", "connected", "active", "running"].includes(value)) return "healthy";
  if (["warning", "degraded", "slow"].includes(value)) return "warning";
  if (["critical", "error", "failed", "disconnected", "down"].includes(value)) return "critical";
  return "unknown";
}

export function systemStatusLabel(status) {
  const map = {
    healthy: "All systems operational",
    warning: "Attention required",
    critical: "Service disruption",
    unknown: "Status unavailable",
  };
  return map[normalizeHealthStatus(status)] || map.unknown;
}
