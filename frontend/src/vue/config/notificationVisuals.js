/** Category styling for in-app notification rows. */

const categoryMap = {
  welcome: { icon: "notifications", tone: "brand" },
  security: { icon: "security", tone: "warning" },
  security_alert: { icon: "security", tone: "warning" },
  fraud: { icon: "fraud", tone: "danger" },
  election: { icon: "elections", tone: "brand" },
  elections: { icon: "elections", tone: "brand" },
  results: { icon: "results", tone: "info" },
  strongroom: { icon: "strongroom", tone: "brand" },
  communications: { icon: "communications", tone: "info" },
  ussd: { icon: "ussd", tone: "info" },
  system: { icon: "settings", tone: "neutral" },
};

const toneStyles = {
  brand: { bg: "#EEF2FF", color: "#1E3A6E", border: "#C7D2FE" },
  info: { bg: "#ECFEFF", color: "#0F766E", border: "#A5F3FC" },
  warning: { bg: "#FFFBEB", color: "#B45309", border: "#FDE68A" },
  danger: { bg: "#FEF2F2", color: "#C62828", border: "#FECACA" },
  neutral: { bg: "#F8FAFC", color: "#475569", border: "#E2E8F0" },
};

export function getNotificationVisual(category = "") {
  const key = String(category || "").toLowerCase();
  const match =
    categoryMap[key] ||
    Object.entries(categoryMap).find(([prefix]) => key.startsWith(prefix))?.[1] ||
    categoryMap.system;

  const tone = toneStyles[match.tone] || toneStyles.neutral;
  return {
    icon: match.icon,
    style: {
      backgroundColor: tone.bg,
      color: tone.color,
      borderColor: tone.border,
    },
  };
}

export function formatNotificationCategory(category = "") {
  if (!category) return "";
  return category.replace(/_/g, " ");
}
