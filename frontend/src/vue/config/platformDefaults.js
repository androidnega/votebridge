/** Platform-wide default settings exposed in Super Admin Settings (not per-election config). */

export const platformDefaultGroups = [
  {
    id: "scheduling",
    title: "Scheduling defaults",
    description: "Applied when Election Administrators create new elections.",
    category: "election_policies",
    keys: ["default_duration_hours", "default_timezone"],
  },
  {
    id: "authentication",
    title: "Authentication defaults",
    description: "System-wide login and session policies.",
    category: "authentication",
    keys: ["otp_expiry_minutes", "session_timeout_minutes", "max_login_attempts", "lockout_minutes"],
  },
  {
    id: "audit",
    title: "Retention defaults",
    description: "Platform audit and log retention.",
    category: "audit",
    keys: ["retention_days", "archive_after_days"],
  },
  {
    id: "monitoring",
    title: "Monitoring defaults",
    description: "Operational alert thresholds.",
    category: "election_policies",
    keys: ["turnout_alert_threshold_percent"],
  },
];

/** Keys hidden from Super Admin — managed in Election Administrator workflows. */
export const hiddenElectionPolicyKeys = new Set([
  "voting_hours_start",
  "voting_hours_end",
  "allow_web_voting",
  "allow_ussd_voting",
  "allow_sms_voting",
  "require_svt",
  "require_otp",
  "require_device_verification",
  "require_location_verification",
  "allow_reopening",
  "allow_extensions",
  "max_candidates_per_position",
]);
