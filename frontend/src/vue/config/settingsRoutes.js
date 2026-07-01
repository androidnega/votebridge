/** Settings workspace URL slugs — single source of truth for Super Admin routes. */

const BASE = "/dashboard/settings";

export const settingsRoutes = {
  overview: BASE,
  institution: {
    hub: `${BASE}/institution`,
    profile: `${BASE}/institution/profile`,
    branding: `${BASE}/institution/branding`,
  },
  integrations: {
    hub: `${BASE}/integrations`,
    providers: `${BASE}/integrations/providers`,
    ussd: `${BASE}/integrations/ussd`,
    notifications: `${BASE}/integrations/notifications`,
    channels: `${BASE}/integrations/channels`,
    sms: `${BASE}/integrations/sms`,
    email: `${BASE}/integrations/email`,
  },
  security: {
    hub: `${BASE}/security`,
    authentication: `${BASE}/security/authentication`,
    identityAssurance: `${BASE}/security/identity-assurance`,
    policies: `${BASE}/security/policies`,
    electionAdministration: `${BASE}/security/election-administration`,
    strongroom: `${BASE}/security/strongroom`,
    api: `${BASE}/security/api`,
    audit: `${BASE}/security/audit`,
  },
  advanced: {
    hub: `${BASE}/advanced`,
    platformDefaults: `${BASE}/advanced/platform-defaults`,
    featureFlags: `${BASE}/advanced/feature-flags`,
    maintenance: `${BASE}/advanced/maintenance`,
    backup: `${BASE}/advanced/backup`,
    system: `${BASE}/advanced/system`,
    runtime: `${BASE}/advanced/runtime`,
    environment: `${BASE}/advanced/environment`,
    storage: `${BASE}/advanced/storage`,
    license: `${BASE}/advanced/license`,
    about: `${BASE}/advanced/about`,
  },
};

/** Prefixes for settings tab active state in ModuleNav. */
export const settingsNavPrefixes = {
  overview: settingsRoutes.overview,
  institution: settingsRoutes.institution.hub,
  integrations: settingsRoutes.integrations.hub,
  security: settingsRoutes.security.hub,
  advanced: settingsRoutes.advanced.hub,
};

export function settingsPath(...segments) {
  return [BASE, ...segments.filter(Boolean)].join("/");
}

export function isSettingsSectionActive(routePath, sectionPrefix, { exact = false } = {}) {
  if (exact) {
    return routePath === sectionPrefix;
  }
  return routePath === sectionPrefix || routePath.startsWith(`${sectionPrefix}/`);
}
