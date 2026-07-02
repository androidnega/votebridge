<script setup>
import { computed, onMounted, onUnmounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import ElectionStatusBadge from "@/components/voting/ElectionStatusBadge.vue";
import LiveTrendPanel from "@/components/elections/analytics/LiveTrendPanel.vue";
import { ConfirmDialog, FaIcon, VButton } from "@/components/ui";
import { toastMessages } from "@/config/toastMessages";
import { useToast } from "@/composables/useToast";
import { useDashboardRealtime } from "@/composables/useDashboardRealtime";
import { useElectionStore } from "@/stores/election";
import { useOperationsStore } from "@/stores/operations";

const route = useRoute();
const router = useRouter();
const electionStore = useElectionStore();
const operationsStore = useOperationsStore();
const toast = useToast();
const realtime = useDashboardRealtime("admin");

const pauseOpen = ref(false);
const closeOpen = ref(false);
const incidentOpen = ref(false);
const countdownLabel = ref("—");
let countdownTimer = null;

const electionUuid = computed(() => route.params.uuid);
const election = computed(() => electionStore.currentElection || {});

const monitorRow = computed(() =>
  (operationsStore.elections || []).find((row) => row.election_uuid === electionUuid.value)
);

const turnout = computed(() => Math.min(100, Math.max(0, Number(monitorRow.value?.turnout_percentage) || 0)));
const votesCast = computed(() => monitorRow.value?.voters_participated ?? 0);
const eligible = computed(() => monitorRow.value?.eligible_voters ?? 0);
const securityAlerts = computed(() => monitorRow.value?.open_alerts ?? 0);
const fraudFlags = computed(() => monitorRow.value?.open_fraud_cases ?? 0);
const webActive = computed(() => monitorRow.value?.voting_channels?.web !== false);
const ussdActive = computed(() => Boolean(monitorRow.value?.voting_channels?.ussd));

const feedItems = computed(() =>
  (realtime.activityFeed.value || [])
    .filter((item) => !item.election_uuid || item.election_uuid === electionUuid.value)
    .slice(0, 10)
);

const canControl = computed(() => ["open", "paused"].includes(election.value?.status));
const showLiveTrend = computed(() => ["open", "paused"].includes(election.value?.status));

const linkStatus = computed(() => {
  if (realtime.status.value === "connected") {
    return { label: "Live", dot: "bg-success-500", text: "text-success-700", ring: "ring-success-100" };
  }
  if (realtime.status.value === "connecting") {
    return { label: "Connecting", dot: "bg-warning-500", text: "text-warning-700", ring: "ring-warning-100" };
  }
  return { label: "Offline", dot: "bg-danger-500", text: "text-danger-700", ring: "ring-danger-100" };
});

const securityPosture = computed(() => {
  const total = securityAlerts.value + fraudFlags.value;
  if (total === 0) return { label: "Nominal", text: "text-success-700", bg: "bg-success-50" };
  if (total < 3) return { label: "Elevated", text: "text-warning-700", bg: "bg-warning-50" };
  return { label: "Critical", text: "text-danger-700", bg: "bg-danger-50" };
});

const metricTiles = computed(() => [
  {
    key: "web",
    label: "Web channel",
    value: monitorRow.value?.web_votes ?? 0,
    hint: webActive.value ? "Active" : "Off",
    icon: "fa-globe",
    ok: webActive.value,
  },
  {
    key: "ussd",
    label: "USSD channel",
    value: monitorRow.value?.ussd_votes ?? 0,
    hint: ussdActive.value ? "Active" : "Off",
    icon: "fa-mobile-screen-button",
    ok: ussdActive.value,
  },
  {
    key: "sessions",
    label: "USSD sessions",
    value: monitorRow.value?.active_sessions ?? 0,
    hint: `${monitorRow.value?.failed_sessions ?? 0} failed`,
    icon: "fa-signal",
    ok: !(monitorRow.value?.failed_sessions),
  },
  {
    key: "security",
    label: "Security alerts",
    value: securityAlerts.value,
    hint: "Open items",
    icon: "fa-shield-halved",
    ok: securityAlerts.value === 0,
  },
  {
    key: "fraud",
    label: "Fraud cases",
    value: fraudFlags.value,
    hint: "Under review",
    icon: "fa-triangle-exclamation",
    ok: fraudFlags.value === 0,
  },
  {
    key: "health",
    label: "System health",
    value: monitorRow.value?.system_health?.label || linkStatus.value.label,
    hint: "Infrastructure",
    icon: "fa-heart-pulse",
    ok: (monitorRow.value?.system_health?.status || "healthy") === "healthy",
    textValue: true,
  },
]);

function updateCountdown() {
  const end = election.value?.end_date;
  if (!end) {
    countdownLabel.value = "—";
    return;
  }
  const diff = new Date(end).getTime() - Date.now();
  if (diff <= 0) {
    countdownLabel.value = "Closed";
    return;
  }
  const hours = Math.floor(diff / 3_600_000);
  const mins = Math.floor((diff % 3_600_000) / 60_000);
  const secs = Math.floor((diff % 60_000) / 1000);
  if (hours >= 24) {
    const days = Math.floor(hours / 24);
    countdownLabel.value = `${days}d ${hours % 24}h ${mins}m`;
    return;
  }
  countdownLabel.value = `${hours}h ${mins}m ${secs}s`;
}

function formatEventTime(value) {
  if (!value) return "";
  return new Date(value).toLocaleTimeString(undefined, { hour: "2-digit", minute: "2-digit" });
}

async function runPause() {
  await electionStore.pauseElection(electionUuid.value);
  pauseOpen.value = false;
  toast.success(toastMessages.election.paused);
}

async function runClose() {
  await electionStore.closeElection(electionUuid.value);
  closeOpen.value = false;
  toast.success(toastMessages.election.closed);
  router.push("/dashboard/results");
}

function acknowledgeIncident() {
  incidentOpen.value = false;
  toast.success("Incident acknowledged. Document details in the fraud dashboard if required.");
}

onMounted(async () => {
  updateCountdown();
  countdownTimer = window.setInterval(updateCountdown, 1000);
  await electionStore.fetchElection(electionUuid.value).catch(() => {});
  await operationsStore.fetchElectionMonitor().catch(() => {});
  operationsStore.connectRealtime?.();
});

onUnmounted(() => {
  if (countdownTimer) window.clearInterval(countdownTimer);
  operationsStore.disconnectRealtime?.();
});
</script>

<template>
  <div class="vb-control-room">
    <header class="vb-control-room-header">
      <div class="min-w-0 flex-1">
        <p class="text-xs font-semibold uppercase tracking-[0.16em] text-brand-700">Control room</p>
        <div class="mt-2 flex flex-wrap items-center gap-3">
          <h1 class="text-2xl font-bold tracking-tight text-ink-primary sm:text-3xl">
            {{ election.title || "Election monitor" }}
          </h1>
          <ElectionStatusBadge :status="election.status" size="sm" />
        </div>
        <p class="mt-2 max-w-2xl text-sm text-ink-secondary">
          Live turnout, channel health, and private candidate performance for election officers.
        </p>
      </div>

      <div class="flex flex-wrap gap-2">
        <div
          class="inline-flex items-center gap-2 rounded-full bg-white px-3 py-1.5 text-xs font-semibold ring-1 ring-inset"
          :class="[linkStatus.text, linkStatus.ring]"
        >
          <span class="relative flex h-2 w-2">
            <span
              v-if="realtime.status.value === 'connected'"
              class="absolute inline-flex h-full w-full animate-ping rounded-full opacity-40"
              :class="linkStatus.dot"
            />
            <span class="relative inline-flex h-2 w-2 rounded-full" :class="linkStatus.dot" />
          </span>
          {{ linkStatus.label }}
        </div>
        <div
          class="inline-flex items-center rounded-full px-3 py-1.5 text-xs font-semibold"
          :class="[securityPosture.bg, securityPosture.text]"
        >
          Security · {{ securityPosture.label }}
        </div>
      </div>
    </header>

    <section class="vb-control-room-hero">
      <article class="vb-control-room-panel vb-control-room-turnout">
        <div class="flex items-start justify-between gap-4">
          <div>
            <p class="text-xs font-semibold uppercase tracking-wide text-ink-secondary">Live turnout</p>
            <p class="mt-2 text-5xl font-bold tabular-nums text-brand-700 sm:text-6xl">{{ turnout }}%</p>
            <p class="mt-2 text-sm text-ink-secondary">
              <span class="font-semibold text-ink-primary">{{ votesCast }}</span>
              of {{ eligible }} eligible voters
            </p>
          </div>
          <div class="rounded-xl bg-brand-50 p-3 text-brand-700" aria-hidden="true">
            <FaIcon icon="fa-chart-line" class="text-xl" />
          </div>
        </div>
        <div class="mt-6 h-2.5 overflow-hidden rounded-full bg-surface-muted">
          <div
            class="h-full rounded-full bg-brand-600 transition-all duration-700 ease-out"
            :style="{ width: `${turnout}%` }"
          />
        </div>
      </article>

      <article class="vb-control-room-panel vb-control-room-countdown">
        <p class="text-xs font-semibold uppercase tracking-wide text-ink-secondary">Time to close</p>
        <p class="mt-3 font-mono text-3xl font-semibold tabular-nums text-ink-primary sm:text-4xl">
          {{ countdownLabel }}
        </p>
        <p class="mt-3 flex items-center gap-2 text-xs text-ink-secondary">
          <FaIcon icon="fa-clock" class="text-brand-700" />
          Updates every second while this page is open
        </p>
      </article>
    </section>

    <section class="vb-control-room-metrics">
      <article
        v-for="tile in metricTiles"
        :key="tile.key"
        class="vb-control-room-metric"
        :class="tile.ok ? '' : 'vb-control-room-metric--warn'"
      >
        <div class="flex items-start justify-between gap-2">
          <div class="min-w-0">
            <p class="text-xs font-medium text-ink-secondary">{{ tile.label }}</p>
            <p
              class="mt-1 truncate text-xl font-bold tabular-nums text-ink-primary"
              :class="tile.textValue ? 'text-base font-semibold capitalize' : ''"
            >
              {{ tile.value }}
            </p>
            <p class="mt-0.5 text-[11px] text-ink-secondary">{{ tile.hint }}</p>
          </div>
          <FaIcon :icon="tile.icon" class="mt-0.5 shrink-0 text-brand-700/70" />
        </div>
      </article>
    </section>

    <LiveTrendPanel
      v-if="showLiveTrend"
      :election-uuid="electionUuid"
      class="mt-6"
    />

    <section v-if="canControl" class="vb-control-room-actions">
      <VButton
        variant="secondary"
        class="min-h-[44px]"
        :loading="electionStore.actionLoading"
        @click="pauseOpen = true"
      >
        <FaIcon icon="fa-pause" class="mr-2" />
        Pause election
      </VButton>
      <VButton
        variant="danger"
        class="min-h-[44px]"
        :loading="electionStore.actionLoading"
        @click="closeOpen = true"
      >
        <FaIcon icon="fa-stop" class="mr-2" />
        Close election
      </VButton>
      <VButton variant="secondary" class="min-h-[44px]" @click="incidentOpen = true">
        <FaIcon icon="fa-bolt" class="mr-2" />
        Emergency incident
      </VButton>
    </section>

    <section class="vb-control-room-panel">
      <div class="mb-4 flex items-center justify-between gap-3">
        <h2 class="text-sm font-semibold text-ink-primary">Operational feed</h2>
        <span class="text-xs text-ink-secondary">{{ feedItems.length }} events</span>
      </div>

      <div v-if="operationsStore.loading && !feedItems.length" class="space-y-2">
        <div v-for="n in 3" :key="n" class="h-12 animate-pulse rounded-lg bg-surface-muted" />
      </div>

      <div
        v-else-if="!feedItems.length"
        class="flex flex-col items-center rounded-xl border border-dashed border-border bg-surface-muted/60 px-6 py-10 text-center"
      >
        <FaIcon icon="fa-tower-broadcast" class="mb-3 text-2xl text-ink-secondary" />
        <p class="text-sm font-medium text-ink-primary">Awaiting operational events</p>
        <p class="mt-1 text-xs text-ink-secondary">Activity will appear here as voting progresses.</p>
      </div>

      <ul v-else class="max-h-72 space-y-2 overflow-y-auto">
        <li
          v-for="(item, index) in feedItems"
          :key="item.id || item.alert_id || index"
          class="flex items-start justify-between gap-3 rounded-lg border border-border bg-surface-muted/50 px-3 py-2.5"
        >
          <div class="min-w-0">
            <p class="truncate text-sm font-medium text-ink-primary">
              {{ item.title || item.alert_title || item.event_type || "Event" }}
            </p>
            <p v-if="item.description" class="mt-0.5 line-clamp-1 text-xs text-ink-secondary">
              {{ item.description }}
            </p>
          </div>
          <time class="shrink-0 text-[11px] tabular-nums text-ink-secondary">
            {{ formatEventTime(item.created_at || item.timestamp) }}
          </time>
        </li>
      </ul>
    </section>

    <ConfirmDialog
      v-model="pauseOpen"
      title="Pause election?"
      description="Voting will be suspended immediately. Students cannot submit ballots until you resume."
      variant="danger"
      icon="bolt"
      confirm-label="Pause election"
      :loading="electionStore.actionLoading"
      @confirm="runPause"
    />
    <ConfirmDialog
      v-model="closeOpen"
      title="Close election?"
      description="Voting will end and results processing will begin. This action cannot be undone."
      variant="danger"
      icon="strongroom"
      confirm-label="Close election"
      :loading="electionStore.actionLoading"
      @confirm="runClose"
    />
    <ConfirmDialog
      v-model="incidentOpen"
      title="Declare emergency incident?"
      description="Use this when an operational or security incident requires immediate attention."
      variant="danger"
      icon="fraud"
      confirm-label="Acknowledge incident"
      @confirm="acknowledgeIncident"
    />
  </div>
</template>
