import { resolveElectionCountdownTarget } from "@/composables/useElectionCountdown";

const PREVIEW_POSITIONS = 3;

export function formatElectionTypeLabel(typeDisplay = "", electionType = "") {
  const normalized = (typeDisplay || electionType || "").toLowerCase();
  if (normalized.includes("student") || normalized.includes("union")) return "SRC Election";
  if (normalized.includes("faculty")) return "Faculty Election";
  if (normalized.includes("department")) return "Department Election";
  if (normalized.includes("general")) return "General Election";
  if (typeDisplay) return typeDisplay;
  return "Campus Election";
}

export function formatClosingDateParts(value) {
  if (!value) {
    return { dateLine: "Date to be announced", timeLine: "" };
  }
  const date = new Date(value);
  return {
    dateLine: date.toLocaleDateString(undefined, {
      day: "numeric",
      month: "long",
      year: "numeric",
    }),
    timeLine: date.toLocaleTimeString(undefined, {
      hour: "numeric",
      minute: "2-digit",
    }),
  };
}

export function buildPositionPreview(positionTitles = [], positionCount = 0) {
  const titles = positionTitles.filter(Boolean);
  const total = positionCount || titles.length;
  const preview = titles.slice(0, PREVIEW_POSITIONS);
  const moreCount = Math.max(0, total - preview.length);
  return { preview, moreCount, total };
}

export function resolveVotingChannels(electionType = "") {
  const type = electionType.toLowerCase();
  const channels = ["Web"];
  if (["general", "student_union", "special", ""].includes(type)) {
    channels.push("USSD");
  }
  return channels;
}

export function resolveStudentVotingStatus(card) {
  if (card.status === "closed") {
    return { key: "closed", label: "Closed", tone: "red" };
  }
  if (card.hasVoted) {
    return { key: "submitted", label: "Vote Submitted", tone: "blue" };
  }
  if (card.confirmationStatus === "in_progress") {
    return { key: "in_progress", label: "Ballot In Progress", tone: "orange" };
  }
  if (card.confirmationStatus === "token_issued") {
    return { key: "ready", label: "Ready to Vote", tone: "green" };
  }
  if (card.confirmationStatus === "not_started") {
    return { key: "not_started", label: "Not Yet Started", tone: "green" };
  }
  return { key: "ready", label: "Ready to Vote", tone: "green" };
}

export function resolveElectionAction(card) {
  if (card.status === "closed") {
    return {
      label: "View Results",
      tone: "secondary",
      handler: "results",
      route: `/dashboard/results/${card.uuid}`,
    };
  }
  if (card.hasVoted) {
    return {
      label: "View Confirmation",
      tone: "outline",
      handler: "confirmation",
      route: `/dashboard/elections/${card.uuid}/confirmation`,
    };
  }
  if (card.confirmationStatus === "in_progress") {
    return {
      label: "Continue Ballot",
      tone: "blue",
      handler: "vote",
    };
  }
  return {
    label: "Vote Now",
    tone: "primary",
    handler: "vote",
  };
}

export function electionStatusBadge(status) {
  const map = {
    open: { label: "OPEN", variant: "open" },
    paused: { label: "PAUSED", variant: "paused" },
    scheduled: { label: "SCHEDULED", variant: "info" },
    closed: { label: "CLOSED", variant: "closed" },
  };
  return map[status] || { label: (status || "UNKNOWN").toUpperCase(), variant: "default" };
}

export function studentStatusToneClasses(tone) {
  const map = {
    green: "bg-success-50 text-success-800 ring-success-600/15",
    orange: "bg-warning-50 text-warning-800 ring-warning-600/15",
    blue: "bg-info-50 text-info-800 ring-info-600/15",
    red: "bg-danger-50 text-danger-800 ring-danger-600/15",
  };
  return map[tone] || map.green;
}

export function actionButtonClasses(tone) {
  const base =
    "inline-flex min-h-[44px] w-full items-center justify-center rounded-xl px-4 text-sm font-semibold transition focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 disabled:cursor-not-allowed disabled:opacity-50";
  const map = {
    primary: `${base} bg-brand-600 text-white shadow-sm hover:bg-brand-hover focus-visible:outline-brand-600`,
    blue: `${base} bg-blue-600 text-white shadow-sm hover:bg-blue-700 focus-visible:outline-blue-600`,
    outline: `${base} border border-border bg-white text-ink-primary shadow-sm hover:bg-surface-muted focus-visible:outline-brand-600`,
    secondary: `${base} border border-border bg-surface-muted text-ink-primary hover:bg-surface focus-visible:outline-brand-600`,
  };
  return map[tone] || map.primary;
}

export function formatCountdownPill(target) {
  if (!target) return { label: "Voting ends soon", expired: true };
  const diff = new Date(target).getTime() - Date.now();
  if (diff <= 0) return { label: "Voting closed", expired: true };

  const days = Math.floor(diff / 86_400_000);
  const hours = Math.floor((diff % 86_400_000) / 3_600_000);
  const minutes = Math.floor((diff % 3_600_000) / 60_000);

  if (days > 0) {
    return {
      label: `${days} ${days === 1 ? "Day" : "Days"} ${hours} ${hours === 1 ? "Hour" : "Hours"}`,
      expired: false,
    };
  }
  if (hours > 0) {
    return {
      label: `${hours} ${hours === 1 ? "Hour" : "Hours"} ${minutes} ${minutes === 1 ? "Minute" : "Minutes"}`,
      expired: false,
    };
  }
  return {
    label: `${minutes} ${minutes === 1 ? "Minute" : "Minutes"}`,
    expired: false,
  };
}

export function resolveCardCountdownTarget(card) {
  return resolveElectionCountdownTarget({
    status: card.status,
    election_status: card.status,
    start_date: card.startDate,
    end_date: card.endDate,
  });
}

export function relativeUpdatedLabel(value) {
  if (!value) return "Just now";
  const diff = Date.now() - new Date(value).getTime();
  if (diff < 60_000) return "Just now";
  const minutes = Math.floor(diff / 60_000);
  if (minutes < 60) return `${minutes} minute${minutes === 1 ? "" : "s"} ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours} hour${hours === 1 ? "" : "s"} ago`;
  const days = Math.floor(hours / 24);
  return `${days} day${days === 1 ? "" : "s"} ago`;
}
