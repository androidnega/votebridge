import { computed, onMounted, onUnmounted, ref } from "vue";
import { publicApi } from "@/api/public";

const phaseLabels = {
  before_election: { badge: "Standby", class: "bg-slate-100 text-slate-700 ring-slate-200" },
  election_scheduled: { badge: "Scheduled", class: "bg-info-50 text-info-700 ring-info-200" },
  election_open: { badge: "Voting open", class: "bg-success-50 text-success-700 ring-success-200" },
  awaiting_certification: { badge: "Awaiting certification", class: "bg-warning-50 text-warning-700 ring-warning-200" },
  results_published: { badge: "Results published", class: "bg-brand-50 text-brand-700 ring-brand-200" },
};

export function formatElectionDate(value) {
  if (!value) return "—";
  return new Date(value).toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" });
}

export function useElectionPortal() {
  const loading = ref(true);
  const portal = ref({
    phase: "before_election",
    election: null,
    countdown: null,
    turnout: null,
    timeline: [],
    candidates: [],
    announcements: [],
    operational_status: "standby",
  });

  const countdownText = ref("—");
  const countdownParts = ref(null);
  let countdownTimer = null;

  const phaseMeta = computed(() => phaseLabels[portal.value.phase] || phaseLabels.before_election);

  const latestAnnouncement = computed(() => portal.value.announcements[0] ?? null);

  function updateCountdown() {
    const target = portal.value.countdown?.target_at;
    if (!target) {
      countdownText.value = "—";
      countdownParts.value = null;
      return;
    }
    const diff = new Date(target).getTime() - Date.now();
    if (diff <= 0) {
      countdownText.value = "Now";
      countdownParts.value = { hours: 0, mins: 0, secs: 0, expired: true };
      return;
    }
    const hours = Math.floor(diff / 3_600_000);
    const mins = Math.floor((diff % 3_600_000) / 60_000);
    const secs = Math.floor((diff % 60_000) / 1000);
    countdownText.value = `${hours}h ${mins}m ${secs}s`;
    countdownParts.value = { hours, mins, secs, expired: false };
  }

  onMounted(async () => {
    try {
      portal.value = await publicApi.getElectionPortal();
    } catch {
      /* defaults */
    } finally {
      loading.value = false;
      updateCountdown();
      countdownTimer = setInterval(updateCountdown, 1000);
    }
  });

  onUnmounted(() => {
    if (countdownTimer) clearInterval(countdownTimer);
  });

  return {
    loading,
    portal,
    phaseMeta,
    countdownText,
    countdownParts,
    latestAnnouncement,
    formatDate: formatElectionDate,
  };
}
