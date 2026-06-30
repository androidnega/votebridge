/**
 * VoteBridge enterprise design tokens — Phase 33.1
 * Source of truth mirrored in: frontend/tailwind.config.cjs
 * Utility classes: frontend/src/vue/assets/styles/main.css
 */

export const colors = {
  primary: "#1E5F46",
  primaryHover: "#184C38",
  navy: "#1E293B",
  navyBorder: "#334155",
  background: "#F8FAFC",
  surface: "#FFFFFF",
  border: "#E2E8F0",
  textPrimary: "#0F172A",
  textSecondary: "#64748B",
  success: "#16A34A",
  warning: "#D97706",
  danger: "#DC2626",
  info: "#2563EB",
  brand: {
    DEFAULT: "#1E5F46",
    hover: "#184C38",
    50: "#E8F3EF",
    600: "#1E5F46",
    700: "#184C38",
  },
  surfaceToken: {
    DEFAULT: "#FFFFFF",
    muted: "#F8FAFC",
  },
};

export const chartColors = [
  colors.primary,
  "#64748B",
  "#334155",
  "#94A3B8",
  "#CBD5E1",
];

export const typography = {
  fontFamily: "Inter Variable, Inter, system-ui, sans-serif",
  weights: [400, 500, 600, 700],
  scale: {
    pageTitle: "text-2xl font-semibold text-ink-primary",
    sectionTitle: "text-lg font-semibold text-ink-primary",
    cardTitle: "text-base font-semibold text-ink-primary",
    body: "text-sm text-ink-secondary",
    caption: "text-xs text-ink-secondary",
    label: "text-sm font-medium text-ink-primary",
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
  chartColors,
  typography,
  spacing,
  radius,
  shadows,
  statusVariants,
  electionHealth,
};
