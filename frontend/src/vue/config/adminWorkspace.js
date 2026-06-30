/** Election officer workspace — flat soft palettes and quick actions. */

export const adminSoftPalettes = {
  elections: { bg: "#EFF6FF", border: "#BFDBFE", iconBg: "#DBEAFE", icon: "#1E3A6E", hoverBg: "#DBEAFE", hoverBorder: "#93C5FD" },
  turnout: { bg: "#F0FDF4", border: "#BBF7D0", iconBg: "#DCFCE7", icon: "#15803D", hoverBg: "#DCFCE7", hoverBorder: "#86EFAC" },
  positions: { bg: "#EEF2FF", border: "#C7D2FE", iconBg: "#E0E7FF", icon: "#4F46E5", hoverBg: "#E0E7FF", hoverBorder: "#A5B4FC" },
  candidates: { bg: "#FFFBEB", border: "#FDE68A", iconBg: "#FEF3C7", icon: "#B45309", hoverBg: "#FEF3C7", hoverBorder: "#FCD34D" },
  eligibility: { bg: "#ECFEFF", border: "#A5F3FC", iconBg: "#CFFAFE", icon: "#0F766E", hoverBg: "#CFFAFE", hoverBorder: "#67E8F9" },
  readiness: { bg: "#F5F3FF", border: "#DDD6FE", iconBg: "#EDE9FE", icon: "#7C3AED", hoverBg: "#EDE9FE", hoverBorder: "#C4B5FD" },
  results: { bg: "#FFF1F2", border: "#FECDD3", iconBg: "#FFE4E6", icon: "#BE123C", hoverBg: "#FFE4E6", hoverBorder: "#FDA4AF" },
  monitor: { bg: "#F8FAFC", border: "#E2E8F0", iconBg: "#F1F5F9", icon: "#475569", hoverBg: "#F1F5F9", hoverBorder: "#CBD5E1" },
  reports: { bg: "#E8F3EF", border: "#C5E0D6", iconBg: "#D1EAE0", icon: "#1E5F46", hoverBg: "#D1EAE0", hoverBorder: "#9CC9B8" },
  tasks: { bg: "#FFFBEB", border: "#FDE68A", iconBg: "#FEF3C7", icon: "#D97706", hoverBg: "#FEF3C7", hoverBorder: "#FCD34D" },
  neutral: { bg: "#F8FAFC", border: "#E2E8F0", iconBg: "#F1F5F9", icon: "#475569", hoverBg: "#F1F5F9", hoverBorder: "#CBD5E1" },
};

export const adminQuickActionPaletteKeys = {
  create: "elections",
  elections: "elections",
  monitor: "monitor",
  results: "results",
  reports: "reports",
  readiness: "readiness",
  candidates: "candidates",
  eligibility: "eligibility",
  export: "eligibility",
};

export function getAdminSoftPalette(key) {
  return adminSoftPalettes[key] || adminSoftPalettes.neutral;
}

export const adminWorkspaceTiles = [
  { id: "positions", title: "Positions", description: "Define offices and vote limits.", routeSuffix: "positions", paletteKey: "positions", icon: "elections" },
  { id: "candidates", title: "Candidates", description: "Nominate and approve candidates.", routeSuffix: "candidates", paletteKey: "candidates", icon: "profile" },
  { id: "eligibility", title: "Eligibility", description: "Voter roll and programme filters.", routeSuffix: "eligibility", paletteKey: "eligibility", icon: "profile" },
  { id: "readiness", title: "Readiness", description: "Pre-open validation checklist.", routeSuffix: "readiness", paletteKey: "readiness", icon: "security" },
  { id: "results", title: "Results", description: "Hand over after closing.", routeSuffix: null, paletteKey: "results", icon: "results", externalRoute: "/dashboard/results" },
];

export const adminChartColors = ["#1E3A6E", "#0F766E", "#2E7D32", "#CA8A04", "#64748B"];

export const adminKpiHealthStripe = {
  healthy: "bg-[#CBD5E1]",
  attention: "bg-[#D6D3D1]",
  critical: "bg-[#D4A4A4]",
  unknown: "bg-[#E2E8F0]",
};
