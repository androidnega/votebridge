/** Settings workspace URL slugs — Phase 63 governance IA. */

const BASE = "/dashboard/settings";

export const settingsRoutes = {
  overview: BASE,
  institution: {
    hub: `${BASE}/institution`,
    profile: `${BASE}/institution/profile`,
    branding: `${BASE}/institution/branding`,
  },
  security: {
    hub: `${BASE}/security`,
    authentication: `${BASE}/security/authentication`,
    identityAssurance: `${BASE}/security/identity-assurance`,
    policies: `${BASE}/security/policies`,
    api: `${BASE}/security/api`,
    audit: `${BASE}/security/audit`,
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
  governance: {
    hub: `${BASE}/governance`,
    electionAdministration: `${BASE}/governance/election-administration`,
    strongroom: `${BASE}/governance/strongroom`,
    platformDefaults: `${BASE}/governance/platform-defaults`,
  },
  operations: {
    hub: `${BASE}/operations`,
    maintenance: `${BASE}/operations/maintenance`,
    backup: `${BASE}/operations/backup`,
    storage: `${BASE}/operations/storage`,
    dataReset: `${BASE}/operations/data-reset`,
  },
  advanced: {
    hub: `${BASE}/advanced`,
    featureFlags: `${BASE}/advanced/feature-flags`,
    runtime: `${BASE}/advanced/runtime`,
    environment: `${BASE}/advanced/environment`,
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
  governance: settingsRoutes.governance.hub,
  operations: settingsRoutes.operations.hub,
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
