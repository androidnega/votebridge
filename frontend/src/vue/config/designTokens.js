/**
 * VoteBridge enterprise design tokens (Phase 31).
 * Source of truth for Tailwind theme: frontend/tailwind.config.cjs
 * Utility classes: frontend/src/vue/assets/styles/main.css
 */

export const colors = {
  brand: {
    DEFAULT: "#1E5F46",
    hover: "#184C38",
    50: "#E8F3EF",
    100: "#C5E0D6",
    600: "#1E5F46",
    700: "#184C38",
    800: "#123A2A",
  },
  surface: {
    DEFAULT: "#FFFFFF",
    muted: "#F5F7F9",
  },
  border: "#E2E8F0",
  success: { 50: "#E8F5E9", 600: "#2E7D32", 700: "#256628" },
  warning: { 50: "#FEFCE8", 600: "#CA8A04", 700: "#A16207" },
  danger: { 50: "#FFEBEE", 600: "#C62828", 700: "#B71C1C" },
  info: { 50: "#F0FDFA", 600: "#0F766E", 700: "#0D6B64" },
};

export const typography = {
  fontFamily: "Inter Variable, Inter, system-ui, sans-serif",
  weights: [400, 500, 600, 700],
  scale: {
    pageTitle: "text-2xl font-semibold text-slate-800",
    sectionTitle: "text-lg font-semibold text-slate-900",
    cardTitle: "text-base font-semibold text-slate-800",
    body: "text-sm text-slate-600",
    caption: "text-xs text-slate-500",
    label: "text-sm font-medium text-slate-800",
  },
};

export const spacing = {
  page: "32px",
  section: "32px",
  card: "24px",
  inputGap: "16px",
  buttonGap: "16px",
};

export const radius = {
  input: "10px",
  card: "12px",
};

export const shadows = {
  card: "0 1px 3px 0 rgb(15 23 42 / 0.06), 0 1px 2px -1px rgb(15 23 42 / 0.06)",
};

export const statusVariants = {
  draft: "draft",
  scheduled: "scheduled",
  open: "open",
  paused: "paused",
  closed: "closed",
  archived: "archived",
};

export const electionHealth = {
  healthy: { label: "Healthy", class: "text-success-700 bg-success-50 ring-success-600/20" },
  attention: { label: "Needs attention", class: "text-warning-700 bg-warning-50 ring-warning-600/20" },
  critical: { label: "Critical", class: "text-danger-700 bg-danger-50 ring-danger-600/20" },
};

export default {
  colors,
  typography,
  spacing,
  radius,
  shadows,
  statusVariants,
  electionHealth,
};
