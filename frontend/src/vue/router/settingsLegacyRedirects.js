/** Redirect legacy settings and system-control paths to slug-based routes. */

import { settingsRoutes as r } from "@/config/settingsRoutes";

export const settingsLegacyRedirects = [
  // Hub renames (-hub suffix)
  { path: "settings/institution-hub", redirect: r.institution.hub },
  { path: "settings/security-hub", redirect: r.security.hub },
  { path: "settings/advanced-hub", redirect: r.advanced.hub },
  { path: "settings/governance-hub", redirect: r.governance.hub },
  { path: "settings/operations-hub", redirect: r.operations.hub },
  { path: "settings/voting-hub", redirect: r.integrations.hub },

  // Institution
  { path: "settings/branding", redirect: r.institution.branding },

  // Integrations
  { path: "settings/providers", redirect: r.integrations.providers },
  { path: "settings/ussd", redirect: r.integrations.ussd },
  { path: "settings/notifications", redirect: r.integrations.notifications },
  { path: "settings/voting-channels", redirect: r.integrations.channels },
  { path: "settings/sms", redirect: r.integrations.sms },
  { path: "settings/email", redirect: r.integrations.email },

  // Security
  { path: "settings/authentication", redirect: r.security.authentication },
  { path: "settings/identity-assurance", redirect: r.security.identityAssurance },
  { path: "settings/api", redirect: r.security.api },
  { path: "settings/audit", redirect: r.security.audit },
  { path: "settings/security-policies", redirect: r.security.policies },

  // Phase 63 — moved under Election Governance
  { path: "settings/election-administration", redirect: r.governance.electionAdministration },
  { path: "settings/strongroom-config", redirect: r.governance.strongroom },
  { path: "settings/security/election-administration", redirect: r.governance.electionAdministration },
  { path: "settings/security/strongroom", redirect: r.governance.strongroom },

  // Phase 63 — moved under Operations
  { path: "settings/maintenance", redirect: r.operations.maintenance },
  { path: "settings/backup", redirect: r.operations.backup },
  { path: "settings/storage", redirect: r.operations.storage },
  { path: "settings/advanced/maintenance", redirect: r.operations.maintenance },
  { path: "settings/advanced/backup", redirect: r.operations.backup },
  { path: "settings/advanced/storage", redirect: r.operations.storage },
  { path: "settings/advanced/data-reset", redirect: r.operations.dataReset },

  // Phase 63 — moved under Election Governance
  { path: "settings/platform-defaults", redirect: r.governance.platformDefaults },
  { path: "settings/election-policies", redirect: r.governance.platformDefaults },
  { path: "settings/advanced/platform-defaults", redirect: r.governance.platformDefaults },

  // Advanced (unchanged slugs)
  { path: "settings/feature-flags", redirect: r.advanced.featureFlags },
  { path: "settings/system", redirect: r.advanced.hub },
  { path: "settings/advanced/system", redirect: r.advanced.hub },
  { path: "settings/runtime", redirect: r.advanced.runtime },
  { path: "settings/environment", redirect: r.advanced.environment },
  { path: "settings/license", redirect: r.advanced.license },
  { path: "settings/about", redirect: r.advanced.about },
  { path: "settings/institution-profile", redirect: r.institution.profile },

  // Legacy system-control mirror
  { path: "system-control/institution", redirect: r.institution.profile },
  { path: "system-control/branding", redirect: r.institution.branding },
  { path: "system-control/election-policies", redirect: r.governance.platformDefaults },
  { path: "system-control/authentication", redirect: r.security.authentication },
  { path: "system-control/identity-assurance", redirect: r.security.identityAssurance },
  { path: "system-control/security", redirect: r.security.policies },
  { path: "system-control/api", redirect: r.security.api },
  { path: "system-control/audit", redirect: r.security.audit },
  { path: "system-control/notifications", redirect: r.integrations.notifications },
  { path: "system-control/ussd", redirect: r.integrations.ussd },
  { path: "system-control/providers", redirect: r.integrations.providers },
  { path: "system-control/sms", redirect: r.integrations.sms },
  { path: "system-control/email", redirect: r.integrations.email },
  { path: "system-control/feature-flags", redirect: r.advanced.featureFlags },
  { path: "system-control/maintenance", redirect: r.operations.maintenance },
  { path: "system-control/storage", redirect: r.operations.storage },
  { path: "system-control/backup", redirect: r.operations.backup },
  { path: "system-control/environment", redirect: r.advanced.environment },
  { path: "system-control/runtime", redirect: r.advanced.runtime },
  { path: "system-control/license", redirect: r.advanced.license },
  { path: "system-control/about", redirect: r.advanced.about },
];
