/** System Control hub — grouped navigation and quick actions. */

export const systemControlSections = [
  {
    id: "institution",
    title: "Institution & branding",
    description: "Identity, contact details, and portal appearance.",
    icon: "profile",
    items: [
      { label: "Institution profile", to: "/dashboard/settings/institution", description: "Name, campus, and election office contacts" },
      { label: "Branding", to: "/dashboard/settings/branding", description: "Logos, colours, and login panel assets" },
    ],
  },
  {
    id: "platform-defaults",
    title: "Platform defaults",
    description: "System-wide defaults for new elections and platform behaviour.",
    icon: "settings",
    items: [
      { label: "Platform defaults", to: "/dashboard/settings/platform-defaults", description: "Timezone, OTP expiry, session timeout, retention" },
      { label: "Feature flags", to: "/dashboard/settings/feature-flags", description: "Toggle experimental or phased capabilities" },
    ],
  },
  {
    id: "election-administration",
    title: "Election administration",
    description: "Manage Election Administrators — not individual elections.",
    icon: "profile",
    items: [
      { label: "Election administrators", to: "/dashboard/settings/election-administration", description: "List, create, and suspend platform election officers" },
      { label: "Administrator activity", to: "/dashboard/settings/election-administration#activity", description: "Sign-in and governance actions for election officers" },
    ],
  },
  {
    id: "integrations",
    title: "Integrations",
    description: "Communication providers, cache, and realtime infrastructure.",
    icon: "communications",
    items: [
      { label: "Integration health", to: "/dashboard/settings/integrations", description: "SMS, USSD, email, Redis, and WebSockets" },
      { label: "Notifications", to: "/dashboard/settings/notifications", description: "Templates and delivery rules" },
    ],
  },
  {
    id: "strongroom-config",
    title: "Strong room configuration",
    description: "Configure the secure vault before elections — vault access is separate.",
    icon: "strongroom",
    items: [
      { label: "Vault policies", to: "/dashboard/settings/strongroom-config", description: "Committee, credentials, rotation, and audit policies" },
    ],
  },
  {
    id: "security",
    title: "Security & access",
    description: "Authentication, identity assurance, and platform hardening.",
    icon: "security",
    items: [
      { label: "Authentication", to: "/dashboard/settings/authentication", description: "OTP, sessions, and login policies" },
      { label: "Identity assurance", to: "/dashboard/settings/identity-assurance", description: "Biometrics and step-up verification" },
      { label: "Security settings", to: "/dashboard/settings/security", description: "Rate limits, lockouts, and alerts" },
      { label: "API management", to: "/dashboard/settings/api", description: "Keys, webhooks, and integration limits" },
      { label: "Audit settings", to: "/dashboard/settings/audit", description: "Retention and audit log policies" },
    ],
  },
  {
    id: "operations",
    title: "Operations & reliability",
    description: "Maintenance, backups, storage, and runtime.",
    icon: "operations",
    items: [
      { label: "Maintenance mode", to: "/dashboard/settings/maintenance", description: "Schedule downtime and user messaging" },
      { label: "Backup & recovery", to: "/dashboard/settings/backup", description: "Create and verify platform backups" },
      { label: "Storage", to: "/dashboard/settings/storage", description: "Disk usage and cleanup" },
      { label: "Environment", to: "/dashboard/settings/environment", description: "Deployment and runtime context" },
      { label: "Runtime config", to: "/dashboard/settings/runtime", description: "Live tunable system parameters" },
    ],
  },
  {
    id: "about",
    title: "License & about",
    description: "Version information and support contacts.",
    icon: "help",
    items: [
      { label: "License", to: "/dashboard/settings/license", description: "Edition and support entitlements" },
      { label: "About VoteBridge", to: "/dashboard/settings/about", description: "Release notes and credits" },
    ],
  },
];

export const quickActionRoutes = {
  maintenance_enable: "/dashboard/settings/maintenance",
  validate_sms: "/dashboard/settings/integrations?focus=sms",
  validate_ussd: "/dashboard/settings/integrations?focus=ussd",
  create_backup: "/dashboard/settings/backup",
  restore_backup: "/dashboard/settings/backup",
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
