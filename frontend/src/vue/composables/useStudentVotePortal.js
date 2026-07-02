import { computed, onMounted, onUnmounted, ref } from "vue";
import { dashboardApi } from "@/api";
import { greetingForHour } from "@/config/dashboardExperience";
import { useAuthStore } from "@/stores/auth";
import { useDashboardStore } from "@/stores/dashboard";
import {
  resolveElectionCountdownTarget,
} from "@/composables/useElectionCountdown";
import {
  buildPositionPreview,
  formatElectionTypeLabel,
  resolveVotingChannels,
} from "@/utils/studentActiveElectionDisplay";

function countdownParts(target) {
  if (!target) {
    return { days: 0, hours: 0, minutes: 0, seconds: 0, expired: true };
  }
  const diff = new Date(target).getTime() - Date.now();
  if (diff <= 0) {
    return { days: 0, hours: 0, minutes: 0, seconds: 0, expired: true };
  }
  return {
    days: Math.floor(diff / 86_400_000),
    hours: Math.floor((diff % 86_400_000) / 3_600_000),
    minutes: Math.floor((diff % 3_600_000) / 60_000),
    seconds: Math.floor((diff % 60_000) / 1000),
    expired: false,
  };
}

function formatCloseDate(value) {
  if (!value) return "Closing date to be announced";
  return new Date(value).toLocaleString(undefined, {
    day: "numeric",
    month: "long",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

function formatPositionPreview(titles = []) {
  if (!titles.length) return "Multiple positions";
  const preview = titles.slice(0, 3).join(", ");
  if (titles.length > 3) return `${preview}…`;
  return preview;
}

function electionInitials(title = "") {
  const words = title.split(/\s+/).filter(Boolean);
  if (words.length >= 2) return `${words[0][0]}${words[1][0]}`.toUpperCase();
  return title.slice(0, 2).toUpperCase();
}

function relativeTime(value) {
  if (!value) return "";
  const diff = Date.now() - new Date(value).getTime();
  const days = Math.floor(diff / 86_400_000);
  if (days > 0) return `${days} day${days === 1 ? "" : "s"} ago`;
  const hours = Math.floor(diff / 3_600_000);
  if (hours > 0) return `${hours} hour${hours === 1 ? "" : "s"} ago`;
  return "Just now";
}

export function useStudentVotePortal() {
  const authStore = useAuthStore();
  const dashboardStore = useDashboardStore();

  const electionDetailsMap = ref({});
  const detailsLoadedAt = ref(null);
  const portalError = ref(null);
  const portalLoading = ref(false);
  const countdown = ref(countdownParts(null));
  let countdownTimer = null;

  const greeting = computed(() => greetingForHour(new Date().getHours()));

  const studentName = computed(
    () => authStore.user?.first_name || authStore.fullName?.split(" ")[0] || "Student"
  );

  const activeElectionRows = computed(
    () => dashboardStore.studentOverview?.active_elections || []
  );

  const openElectionRows = computed(() =>
    activeElectionRows.value.filter((row) => row.election_status === "open")
  );

  function hasRecordedVote(row) {
    return row.ballot_complete || row.confirmation_status === "recorded";
  }

  function hasPartialOrActiveVote(row) {
    return ["in_progress", "token_issued"].includes(row.confirmation_status);
  }

  const actionableElectionRows = computed(() =>
    openElectionRows.value.filter((row) => !hasRecordedVote(row))
  );

  const primaryElection = computed(() => {
    const match2026 = actionableElectionRows.value.find((row) =>
      /2026/i.test(row.election_title || "")
    );
    return (
      match2026 ||
      actionableElectionRows.value[0] ||
      openElectionRows.value[0] ||
      activeElectionRows.value[0] ||
      null
    );
  });

  const hasActiveElection = computed(() => actionableElectionRows.value.length > 0);

  const electionTitle = computed(() => primaryElection.value?.election_title || "Campus elections");

  const portalSubtitle = computed(() => {
    const title = primaryElection.value?.election_title;
    if (!title) return "Sign in to vote when elections open";
    if (/2026/.test(title)) return `${title} — 2025/2026 Academic Year`;
    return title;
  });

  const votesCastCount = computed(
    () => activeElectionRows.value.filter((row) => hasRecordedVote(row)).length
  );

  const activeElectionCount = computed(() => actionableElectionRows.value.length);

  const countdownText = computed(() => {
    const { days, hours, minutes, expired } = countdown.value;
    if (expired) return "Closed";
    if (days > 0) return `${days}d ${hours}h`;
    return `${hours}h ${minutes}m`;
  });

  function buildElectionCard(row) {
    const details = electionDetailsMap.value[row.election_uuid] || {};
    const positionTitles = details.position_titles || [];
    const positionCount = details.position_count || positionTitles.length;
    const { preview, moreCount } = buildPositionPreview(positionTitles, positionCount);
    const voted = hasRecordedVote(row);
    const partial = hasPartialOrActiveVote(row);
    return {
      uuid: row.election_uuid,
      title: row.election_title || details.title || "Election",
      electionTypeLabel: formatElectionTypeLabel(
        details.election_type_display,
        details.election_type
      ),
      status: row.election_status,
      confirmationStatus: row.confirmation_status,
      positionPreview: preview,
      moreCount,
      positionCount,
      startDate: details.start_date,
      endDate: details.end_date,
      channels: resolveVotingChannels(details.election_type),
      canVote: row.election_status === "open" && !voted,
      hasVoted: voted,
      hasPartialVote: partial,
      confirmationReference: row.confirmation_reference || null,
      lastUpdatedAt: row.submitted_at || detailsLoadedAt.value,
      voteRoute: `/dashboard/elections/${row.election_uuid}/vote`,
      closesLabel: `Closes ${formatCloseDate(details.end_date)}`,
      positionsLabel: preview.length
        ? `${preview.join(", ")}${moreCount ? ` +${moreCount} more` : ""}`
        : positionCount
          ? `${positionCount} positions`
          : "Multiple positions",
      initials: electionInitials(row.election_title || details.title || "EL"),
    };
  }

  const portalElectionCards = computed(() =>
    actionableElectionRows.value.map(buildElectionCard)
  );

  const electionCards = computed(() => openElectionRows.value.map(buildElectionCard));

  const activeElectionCards = computed(() => electionCards.value.filter((card) => card.canVote));

  const historyElectionCards = computed(() => electionCards.value.filter((card) => card.hasVoted));

  const recentActivity = computed(() =>
    activeElectionRows.value
      .filter((row) => hasRecordedVote(row))
      .map((row) => ({
        id: row.election_uuid,
        title: `Vote recorded — ${row.election_title}`,
        timestamp: electionDetailsMap.value[row.election_uuid]?.updated_at || null,
        relative:
          relativeTime(electionDetailsMap.value[row.election_uuid]?.updated_at) || "Recently",
      }))
  );

  function updateCountdown() {
    const primary = primaryElection.value;
    const details = primary ? electionDetailsMap.value[primary.election_uuid] : null;
    const target = resolveElectionCountdownTarget({
      status: primary?.election_status,
      election_status: primary?.election_status,
      start_date: details?.start_date,
      end_date: details?.end_date,
    });
    countdown.value = countdownParts(target);
  }

  async function loadElectionDetails() {
    portalLoading.value = true;
    portalError.value = null;

    const uuids = [...new Set(activeElectionRows.value.map((row) => row.election_uuid).filter(Boolean))];
    if (!uuids.length) {
      electionDetailsMap.value = {};
      updateCountdown();
      portalLoading.value = false;
      return;
    }

    try {
      const results = await Promise.allSettled(
        uuids.map(async (uuid) => {
          const detail = await dashboardApi.getStudentElectionDetail(uuid);
          const positionTitles = (detail.positions || []).map((position) => position.title).filter(Boolean);
          return {
            ...detail,
            title: detail.election_title,
            status: detail.election_status,
            position_count: detail.positions_count,
            position_titles: positionTitles,
          };
        })
      );
      const map = {};
      results.forEach((result, index) => {
        if (result.status === "fulfilled") {
          map[uuids[index]] = result.value;
        }
      });
      electionDetailsMap.value = map;
      detailsLoadedAt.value = new Date().toISOString();
    } catch (error) {
      portalError.value = error.message || "Unable to load election details.";
    } finally {
      portalLoading.value = false;
      updateCountdown();
    }
  }

  async function loadDashboard() {
    await dashboardStore.fetchStudentDashboard();
    await loadElectionDetails();
  }

  onMounted(() => {
    updateCountdown();
    countdownTimer = window.setInterval(updateCountdown, 1000);
  });

  onUnmounted(() => {
    if (countdownTimer) window.clearInterval(countdownTimer);
  });

  return {
    dashboardStore,
    greeting,
    studentName,
    portalSubtitle,
    hasActiveElection,
    primaryElection,
    electionTitle,
    activeElectionCount,
    votesCastCount,
    countdownText,
    electionCards,
    portalElectionCards,
    activeElectionCards,
    historyElectionCards,
    recentActivity,
    portalLoading,
    portalError,
    loadDashboard,
    refresh: loadDashboard,
    formatCloseDate,
  };
}
