/** In-page module navigation — Phase 25 consolidated workspaces. */

import { settingsRoutes } from "@/config/settingsRoutes";

export const resultsNav = [
  { label: "Command center", to: "/dashboard/results", exact: true },
];

export const reportsNav = [];

/** @deprecated Phase 36 — explore pages consolidated into Reports workspace filters. */
export const reportsAdvancedNav = [];

export const strongRoomNav = [
  { label: "Overview", to: "/dashboard/strongroom", exact: true },
  { label: "Certification", to: "/dashboard/results/certification", roles: ["super_admin"] },
  { label: "Investigations", to: "/dashboard/strongroom/investigations" },
  { label: "Election integrity", to: "/dashboard/strongroom/integrity" },
];

export const strongRoomInvestigationsNav = [
  { label: "Fraud", to: "/dashboard/strongroom/investigations/fraud", exact: true },
  { label: "Audit trail", to: "/dashboard/strongroom/investigations/audit" },
  { label: "Security timeline", to: "/dashboard/strongroom/investigations/security" },
  { label: "Identity investigations", to: "/dashboard/strongroom/investigations/identity" },
  { label: "Trusted devices", to: "/dashboard/strongroom/investigations/trusted-devices" },
];

export const strongRoomIntegrityNav = [
  { label: "Overview", to: "/dashboard/strongroom/integrity", exact: true },
  { label: "Chain of custody", to: "/dashboard/strongroom/integrity/custody" },
];

export const settingsNav = [
  {
    label: "Overview",
    to: settingsRoutes.overview,
    exact: true,
    activePathPrefix: settingsRoutes.overview,
  },
  {
    label: "Institution",
    to: settingsRoutes.institution.hub,
    activePathPrefix: settingsRoutes.institution.hub,
  },
  {
    label: "Integrations",
    to: settingsRoutes.integrations.hub,
    activePathPrefix: settingsRoutes.integrations.hub,
  },
  {
    label: "Security",
    to: settingsRoutes.security.hub,
    activePathPrefix: settingsRoutes.security.hub,
  },
  {
    label: "Advanced",
    to: settingsRoutes.advanced.hub,
    activePathPrefix: settingsRoutes.advanced.hub,
  },
];

export const analyticsNav = reportsNav;
export const systemControlNav = settingsNav;

export const communicationsNav = [
  { label: "Overview", to: "/dashboard/communications", exact: true },
  { label: "Templates", to: "/dashboard/communications/templates" },
  { label: "Providers", to: "/dashboard/communications/providers" },
];
export const ussdNav = [
  { label: "Dashboard", to: "/dashboard/ussd", exact: true },
  { label: "Sessions", to: "/dashboard/ussd/sessions" },
];
export const operationsNav = [
  { label: "Overview", to: "/dashboard/operations", exact: true },
  { label: "Live activity", to: "/dashboard/operations/activity" },
  { label: "Election monitor", to: "/dashboard/operations/elections" },
  { label: "System health", to: "/dashboard/operations/health" },
];

export function filterNavByRole(items, role) {
  return items.filter((item) => !item.roles || item.roles.includes(role));
}
