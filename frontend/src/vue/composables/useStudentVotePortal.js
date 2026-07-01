import { computed, onMounted, onUnmounted, ref, unref } from "vue";
import { electionsApi, notificationsApi } from "@/api";
import { greetingForHour } from "@/config/dashboardExperience";
import { useAuthStore } from "@/stores/auth";
import { useDashboardStore } from "@/stores/dashboard";
import { groupCandidatesByPosition } from "@/utils/candidateDisplay";
import {
  resolveCountdownLabel,
  resolveElectionCountdownTarget,
} from "@/composables/useElectionCountdown";

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

function formatDateTime(value) {
  if (!value) return "—";
  return new Date(value).toLocaleString(undefined, {
    weekday: "short",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function useStudentVotePortal() {
  const authStore = useAuthStore();
  const dashboardStore = useDashboardStore();

  const electionDetails = ref(null);
  const candidateGroups = ref([]);
  const notifications = ref([]);
  const portalLoading = ref(false);
  const portalError = ref(null);
  const countdown = ref(countdownParts(null));
  let countdownTimer = null;

  const greeting = computed(() => greetingForHour(new Date().getHours()));

  const studentName = computed(
    () => authStore.user?.first_name || authStore.fullName?.split(" ")[0] || "Student"
  );

  const activeElections = computed(
    () => dashboardStore.studentOverview?.active_elections || []
  );

  const primaryElection = computed(() => {
    const open = activeElections.value.find((row) => row.election_status === "open");
    if (open) return open;
    return activeElections.value.find((row) => row.election_status === "paused") || null;
  });

  const hasActiveElection = computed(() => Boolean(primaryElection.value));

  const electionTitle = computed(
    () =>
      electionDetails.value?.title ||
      primaryElection.value?.election_title ||
      "Campus election"
  );

  const electionStatus = computed(
    () =>
      electionDetails.value?.status ||
      primaryElection.value?.election_status ||
      "draft"
  );

  const electionUuid = computed(
    () => primaryElection.value?.election_uuid || electionDetails.value?.uuid || null
  );

  const countdownTarget = computed(() => {
    const details = electionDetails.value;
    const row = primaryElection.value;
    if (!details && !row) return null;
    return resolveElectionCountdownTarget({
      status: details?.status || row?.election_status,
      election_status: row?.election_status || details?.status,
      start_date: details?.start_date,
      end_date: details?.end_date,
    });
  });

  const countdownLabel = computed(() =>
    resolveCountdownLabel({
      status: electionDetails.value?.status || primaryElection.value?.election_status,
      election_status: primaryElection.value?.election_status || electionDetails.value?.status,
    })
  );

  const hasVoted = computed(
    () =>
      primaryElection.value?.ballot_submitted === true ||
      primaryElection.value?.confirmation_status === "recorded"
  );

  const votingStatusLabel = computed(() => (hasVoted.value ? "Vote Recorded" : "Not Yet Voted"));

  const voteRoute = computed(() =>
    electionUuid.value ? `/dashboard/elections/${electionUuid.value}/vote` : null
  );

  const canVoteNow = computed(
    () => hasActiveElection.value && electionStatus.value === "open" && !hasVoted.value
  );

  function updateCountdown() {
    countdown.value = countdownParts(countdownTarget.value);
  }

  async function loadPortalExtras() {
    portalLoading.value = true;
    portalError.value = null;
    candidateGroups.value = [];
    electionDetails.value = null;
    notifications.value = [];

    try {
      const tasks = [
        notificationsApi
          .getNotificationCenter({ limit: 3 })
          .then((data) => {
            notifications.value = data?.items || [];
          })
          .catch(() => {
            notifications.value = [];
          }),
      ];

      if (primaryElection.value?.election_uuid) {
        const uuid = primaryElection.value.election_uuid;
        tasks.push(
          electionsApi.get(uuid).then((election) => {
            electionDetails.value = election;
          }),
          electionsApi
            .listCandidates(uuid, { status: "approved", page_size: 100 })
            .then((result) => {
              candidateGroups.value = groupCandidatesByPosition(result.items || []);
            })
            .catch(() => {
              candidateGroups.value = [];
            })
        );
      }

      await Promise.allSettled(tasks);
    } catch (error) {
      portalError.value = error.message || "Unable to load election details.";
    } finally {
      portalLoading.value = false;
      updateCountdown();
    }
  }

  async function loadDashboard() {
    await dashboardStore.fetchStudentDashboard();
    await loadPortalExtras();
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
    hasActiveElection,
    primaryElection,
    electionTitle,
    electionStatus,
    electionUuid,
    electionDetails,
    candidateGroups,
    notifications,
    countdown,
    countdownLabel,
    countdownTarget,
    hasVoted,
    votingStatusLabel,
    voteRoute,
    canVoteNow,
    portalLoading,
    portalError,
    formatDateTime,
    loadDashboard,
    refresh: loadDashboard,
  };
}
