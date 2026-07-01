/** Redirect legacy settings and system-control paths to slug-based routes. */

import { settingsRoutes as r } from "@/config/settingsRoutes";

export const settingsLegacyRedirects = [
  // Hub renames (-hub suffix)
  { path: "settings/institution-hub", redirect: r.institution.hub },
  { path: "settings/security-hub", redirect: r.security.hub },
  { path: "settings/advanced-hub", redirect: r.advanced.hub },
  { path: "settings/voting-hub", redirect: r.integrations.hub },

  // Institution (profile moved under /institution/profile)
  { path: "settings/branding", redirect: r.institution.branding },

  // Integrations
  { path: "settings/providers", redirect: r.integrations.providers },
  { path: "settings/ussd", redirect: r.integrations.ussd },
  { path: "settings/notifications", redirect: r.integrations.notifications },
  { path: "settings/voting-channels", redirect: r.integrations.channels },
  { path: "settings/sms", redirect: r.integrations.sms },
  { path: "settings/email", redirect: r.integrations.email },

  // Security (hub now lives at /settings/security)
  { path: "settings/authentication", redirect: r.security.authentication },
  { path: "settings/identity-assurance", redirect: r.security.identityAssurance },
  { path: "settings/election-administration", redirect: r.security.electionAdministration },
  { path: "settings/strongroom-config", redirect: r.security.strongroom },
  { path: "settings/api", redirect: r.security.api },
  { path: "settings/audit", redirect: r.security.audit },

  // Advanced
  { path: "settings/platform-defaults", redirect: r.advanced.platformDefaults },
  { path: "settings/election-policies", redirect: r.advanced.platformDefaults },
  { path: "settings/feature-flags", redirect: r.advanced.featureFlags },
  { path: "settings/maintenance", redirect: r.advanced.maintenance },
  { path: "settings/backup", redirect: r.advanced.backup },
  { path: "settings/system", redirect: r.advanced.system },
  { path: "settings/runtime", redirect: r.advanced.runtime },
  { path: "settings/environment", redirect: r.advanced.environment },
  { path: "settings/storage", redirect: r.advanced.storage },
  { path: "settings/license", redirect: r.advanced.license },
  { path: "settings/about", redirect: r.advanced.about },

  // Legacy flat paths that shared a slug with a new hub page
  { path: "settings/institution-profile", redirect: r.institution.profile },
  { path: "settings/security-policies", redirect: r.security.policies },

  // Legacy system-control mirror
  { path: "system-control/institution", redirect: r.institution.profile },
  { path: "system-control/branding", redirect: r.institution.branding },
  { path: "system-control/election-policies", redirect: r.advanced.platformDefaults },
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
  { path: "system-control/maintenance", redirect: r.advanced.maintenance },
  { path: "system-control/storage", redirect: r.advanced.storage },
  { path: "system-control/backup", redirect: r.advanced.backup },
  { path: "system-control/environment", redirect: r.advanced.environment },
  { path: "system-control/runtime", redirect: r.advanced.runtime },
  { path: "system-control/license", redirect: r.advanced.license },
  { path: "system-control/about", redirect: r.advanced.about },
];
