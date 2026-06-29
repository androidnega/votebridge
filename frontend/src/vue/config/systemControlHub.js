/** System Control hub — grouped navigation and quick actions. */

export const systemControlSections = [
  {
    id: "institution",
    title: "Institution & branding",
    description: "Identity, contact details, and portal appearance.",
    icon: "profile",
    items: [
      { label: "Institution profile", to: "/settings/institution", description: "Name, campus, and election office contacts" },
      { label: "Branding", to: "/settings/branding", description: "Logos, colours, and login panel assets" },
    ],
  },
  {
    id: "elections",
    title: "Elections & policies",
    description: "Rules that govern how elections run on the platform.",
    icon: "elections",
    items: [
      { label: "Election policies", to: "/settings/election-policies", description: "Voting windows, eligibility, and result rules" },
      { label: "Feature flags", to: "/settings/feature-flags", description: "Toggle experimental or phased capabilities" },
    ],
  },
  {
    id: "security",
    title: "Security & access",
    description: "Authentication, identity assurance, and platform hardening.",
    icon: "security",
    items: [
      { label: "Authentication", to: "/settings/authentication", description: "OTP, sessions, and login policies" },
      { label: "Identity assurance", to: "/settings/identity-assurance", description: "Biometrics and step-up verification" },
      { label: "Security settings", to: "/settings/security", description: "Rate limits, lockouts, and alerts" },
      { label: "API management", to: "/settings/api", description: "Keys, webhooks, and integration limits" },
      { label: "Audit settings", to: "/settings/audit", description: "Retention and audit log policies" },
    ],
  },
  {
    id: "communications",
    title: "Communications",
    description: "SMS, email, USSD, and notification delivery.",
    icon: "communications",
    items: [
      { label: "All providers", to: "/settings/providers", description: "Manage communication integrations" },
      { label: "SMS", to: "/settings/sms", description: "Arkesel and SMS routing" },
      { label: "Email", to: "/settings/email", description: "SMTP and outbound mail" },
      { label: "Notifications", to: "/settings/notifications", description: "Templates and delivery rules" },
      { label: "USSD", to: "/settings/ussd", description: "USSD gateway and session settings" },
    ],
  },
  {
    id: "operations",
    title: "Operations & reliability",
    description: "Maintenance, backups, storage, and runtime.",
    icon: "operations",
    items: [
      { label: "Maintenance mode", to: "/settings/maintenance", description: "Schedule downtime and user messaging" },
      { label: "Backup & recovery", to: "/settings/backup", description: "Create and verify platform backups" },
      { label: "Storage", to: "/settings/storage", description: "Disk usage and cleanup" },
      { label: "Environment", to: "/settings/environment", description: "Deployment and runtime context" },
      { label: "Runtime config", to: "/settings/runtime", description: "Live tunable system parameters" },
    ],
  },
  {
    id: "about",
    title: "License & about",
    description: "Version information and support contacts.",
    icon: "help",
    items: [
      { label: "License", to: "/settings/license", description: "Edition and support entitlements" },
      { label: "About VoteBridge", to: "/settings/about", description: "Release notes and credits" },
    ],
  },
];

export const quickActionRoutes = {
  maintenance_enable: "/settings/maintenance",
  test_sms: "/settings/sms",
  create_backup: "/settings/backup",
  open_operations: "/operations",
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
