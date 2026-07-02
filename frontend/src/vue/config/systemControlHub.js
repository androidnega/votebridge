/** Phase 63 — Settings control center: six governance groups. */

import { settingsRoutes as r } from "@/config/settingsRoutes";

export const systemControlSections = [
  {
    id: "institution",
    title: "Institution",
    description: "University identity, branding, and portal-facing defaults.",
    icon: "profile",
    hubTo: r.institution.hub,
    items: [
      { label: "Institution profile", to: r.institution.profile, description: "Name, campus, and election office contacts" },
      { label: "Branding", to: r.institution.branding, description: "Logos, colours, and login panel assets" },
    ],
  },
  {
    id: "security",
    title: "Security",
    description: "Authentication, identity assurance, and platform protection policies.",
    icon: "security",
    hubTo: r.security.hub,
    items: [
      { label: "Authentication", to: r.security.authentication, description: "OTP, sessions, and login policies" },
      { label: "Identity assurance", to: r.security.identityAssurance, description: "Biometrics and step-up verification" },
      { label: "Security policies", to: r.security.policies, description: "Rate limits, lockouts, and alert thresholds" },
      { label: "API management", to: r.security.api, description: "Keys, webhooks, and integration limits" },
      { label: "Audit settings", to: r.security.audit, description: "Retention and audit log policies" },
    ],
  },
  {
    id: "integrations",
    title: "Integrations",
    description: "SMS, email, USSD, and delivery provider configuration.",
    icon: "communications",
    hubTo: r.integrations.hub,
    items: [
      { label: "Integration health", to: r.integrations.hub, description: "Connectivity status and validation" },
      { label: "SMS providers", to: r.integrations.sms, description: "Arkesel and Moolre SMS credentials" },
      { label: "Email providers", to: r.integrations.email, description: "SMTP delivery configuration" },
      { label: "USSD gateway", to: r.integrations.ussd, description: "Callback URL and session limits" },
      { label: "Notifications", to: r.integrations.notifications, description: "Templates and delivery rules" },
    ],
  },
  {
    id: "governance",
    title: "Election Governance",
    description: "Super-admin election governance — not day-to-day election operations.",
    icon: "elections",
    hubTo: r.governance.hub,
    items: [
      { label: "Election administrators", to: r.governance.electionAdministration, description: "Create and manage election officers" },
      { label: "Strong room policies", to: r.governance.strongroom, description: "Vault committee, access, and session rules" },
      { label: "Platform defaults", to: r.governance.platformDefaults, description: "Defaults applied to new elections" },
    ],
  },
  {
    id: "operations",
    title: "Operations",
    description: "Reliability, maintenance, backups, and recoverability.",
    icon: "operations",
    hubTo: r.operations.hub,
    items: [
      { label: "Maintenance mode", to: r.operations.maintenance, description: "Schedule downtime and user messaging" },
      { label: "Backup & recovery", to: r.operations.backup, description: "Create and verify platform backups" },
      { label: "Storage", to: r.operations.storage, description: "Disk usage and cleanup" },
      { label: "Operational data reset", to: r.operations.dataReset, description: "Clear elections, votes, and results" },
    ],
  },
  {
    id: "advanced",
    title: "Advanced",
    description: "Low-frequency technical and deployment settings.",
    icon: "settings",
    hubTo: r.advanced.hub,
    items: [
      { label: "Feature flags", to: r.advanced.featureFlags, description: "Enable or disable platform capabilities" },
      { label: "Environment", to: r.advanced.environment, description: "Deployment context and service endpoints" },
      { label: "Runtime config", to: r.advanced.runtime, description: "Live tunable system parameters" },
      { label: "License", to: r.advanced.license, description: "Edition and support entitlements" },
      { label: "About VoteBridge", to: r.advanced.about, description: "Version, release notes, and credits" },
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
  governance: {
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
  advanced: {
    bg: "#F5F3FF",
    border: "#DDD6FE",
    iconBg: "#EDE9FE",
    icon: "#7C3AED",
    hoverBg: "#EDE9FE",
    accent: "#7C3AED",
  },
  maintenance: {
    bg: "#FFFBEB",
    border: "#FDE68A",
    iconBg: "#FEF3C7",
    icon: "#D97706",
    hoverBg: "#FEF3C7",
    accent: "#D97706",
  },
};

export const settingsQuickActionPaletteKeys = {
  maintenance_enable: "maintenance",
  validate_sms: "integrations",
  validate_ussd: "integrations",
  create_backup: "operations",
  restore_backup: "operations",
};

export function getSettingsSectionPalette(sectionId) {
  return settingsSoftPalettes[sectionId] || settingsSoftPalettes.advanced;
}

export function getSettingsQuickActionPalette(action) {
  const key = settingsQuickActionPaletteKeys[action] || "advanced";
  return settingsSoftPalettes[key] || settingsSoftPalettes.advanced;
}

export const quickActionRoutes = {
  maintenance_enable: r.operations.maintenance,
  validate_sms: r.integrations.sms,
  validate_ussd: `${r.integrations.hub}?focus=ussd`,
  create_backup: r.operations.backup,
  restore_backup: r.operations.backup,
};

export const infrastructureServices = [
  { key: "database_status", label: "Database", icon: "strongroom" },
  { key: "redis_status", label: "Redis", icon: "bolt" },
  { key: "websocket_status", label: "WebSockets", icon: "operations" },
  { key: "sms_provider", label: "SMS", icon: "communications" },
  { key: "email_provider", label: "Email", icon: "inbox" },
  { key: "ussd_provider", label: "USSD", icon: "ussd" },
];

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
