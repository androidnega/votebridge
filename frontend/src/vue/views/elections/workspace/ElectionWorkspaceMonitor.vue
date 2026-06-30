<script setup>
import { computed, onMounted, onUnmounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ActivityFeed } from "@/components/dashboard";
import ElectionStatusBadge from "@/components/voting/ElectionStatusBadge.vue";
import { ConfirmDialog, VButton } from "@/components/ui";
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

const countdownLabel = computed(() => {
  const end = election.value?.end_date;
  if (!end) return "—";
  const diff = new Date(end).getTime() - Date.now();
  if (diff <= 0) return "Closing window elapsed";
  const hours = Math.floor(diff / 3_600_000);
  const mins = Math.floor((diff % 3_600_000) / 60_000);
  const secs = Math.floor((diff % 60_000) / 1000);
  return `${hours}h ${mins}m ${secs}s`;
});

const systemStatus = computed(() => {
  if (realtime.status.value === "connected") return { label: "Live", tone: "text-emerald-400" };
  if (realtime.status.value === "connecting") return { label: "Connecting", tone: "text-amber-400" };
  return { label: "Offline", tone: "text-red-400" };
});

const securityStatus = computed(() => {
  const total = securityAlerts.value + fraudFlags.value;
  if (total === 0) return { label: "Nominal", tone: "text-emerald-400" };
  if (total < 3) return { label: "Elevated", tone: "text-amber-400" };
  return { label: "Critical", tone: "text-red-400" };
});

const feedItems = computed(() =>
  (realtime.activityFeed.value || [])
    .filter((item) => !item.election_uuid || item.election_uuid === electionUuid.value)
    .slice(0, 8)
);

const canControl = computed(() => ["open", "paused"].includes(election.value?.status));

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
  await electionStore.fetchElection(electionUuid.value).catch(() => {});
  await operationsStore.fetchElectionMonitor().catch(() => {});
  operationsStore.connectRealtime?.();
});

onUnmounted(() => {
  operationsStore.disconnectRealtime?.();
});
</script>

<template>
  <div class="control-room -mx-4 -mt-page rounded-none bg-slate-950 px-4 py-6 text-slate-100 sm:-mx-page sm:px-page sm:py-8">
    <header class="mb-6 flex flex-wrap items-start justify-between gap-4 border-b border-slate-800 pb-6">
      <div>
        <p class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Election control room</p>
        <h2 class="mt-2 text-2xl font-bold text-white sm:text-3xl">{{ election.title || "Live operations" }}</h2>
        <div class="mt-3 flex flex-wrap items-center gap-3">
          <ElectionStatusBadge :status="election.status" />
          <span class="text-sm text-slate-400">Mission-critical monitoring — aggregate data only</span>
        </div>
      </div>
      <div class="flex flex-wrap gap-2 text-right text-sm">
        <div>
          <p class="text-slate-500">System link</p>
          <p class="font-semibold" :class="systemStatus.tone">{{ systemStatus.label }}</p>
        </div>
        <div class="ml-4">
          <p class="text-slate-500">Security posture</p>
          <p class="font-semibold" :class="securityStatus.tone">{{ securityStatus.label }}</p>
        </div>
      </div>
    </header>

    <section class="grid grid-cols-1 gap-4 lg:grid-cols-12">
      <!-- Status + turnout -->
      <div class="rounded-xl border border-slate-800 bg-slate-900 p-6 lg:col-span-5">
        <p class="text-xs uppercase tracking-wide text-slate-500">Live turnout</p>
        <p class="mt-2 text-6xl font-bold tabular-nums text-white">{{ turnout }}%</p>
        <p class="mt-2 text-sm text-slate-400">{{ votesCast }} of {{ eligible }} eligible voters</p>
        <div class="mt-6 h-3 overflow-hidden rounded-full bg-slate-800">
          <div
            class="h-full rounded-full bg-emerald-500 transition-all duration-700"
            :style="{ width: `${turnout}%` }"
          />
        </div>
        <p class="mt-6 text-xs uppercase tracking-wide text-slate-500">Time to close</p>
        <p class="mt-1 text-3xl font-semibold tabular-nums text-amber-300">{{ countdownLabel }}</p>
      </div>

      <!-- Metrics grid -->
      <div class="grid grid-cols-2 gap-4 lg:col-span-7">
        <div class="rounded-xl border border-slate-800 bg-slate-900 p-5">
          <p class="text-xs text-slate-500">Security alerts</p>
          <p class="mt-2 text-4xl font-bold tabular-nums" :class="securityAlerts ? 'text-amber-400' : 'text-white'">
            {{ securityAlerts }}
          </p>
        </div>
        <div class="rounded-xl border border-slate-800 bg-slate-900 p-5">
          <p class="text-xs text-slate-500">Fraud flags</p>
          <p class="mt-2 text-4xl font-bold tabular-nums" :class="fraudFlags ? 'text-red-400' : 'text-white'">
            {{ fraudFlags }}
          </p>
        </div>
        <div class="rounded-xl border border-slate-800 bg-slate-900 p-5">
          <p class="text-xs text-slate-500">Web channel</p>
          <p class="mt-2 text-xl font-semibold">{{ monitorRow?.voting_channels?.web ? "Active" : "Off" }}</p>
        </div>
        <div class="rounded-xl border border-slate-800 bg-slate-900 p-5">
          <p class="text-xs text-slate-500">USSD channel</p>
          <p class="mt-2 text-xl font-semibold">{{ monitorRow?.voting_channels?.ussd ? "Active" : "Off" }}</p>
        </div>
      </div>
    </section>

    <!-- Critical actions -->
    <section v-if="canControl" class="mt-6 flex flex-wrap gap-3">
      <VButton
        variant="secondary"
        class="min-h-touch !border-amber-600 !bg-amber-950 !text-amber-200 hover:!bg-amber-900"
        :loading="electionStore.actionLoading"
        @click="pauseOpen = true"
      >
        Pause election
      </VButton>
      <VButton
        variant="danger"
        class="min-h-touch"
        :loading="electionStore.actionLoading"
        @click="closeOpen = true"
      >
        Close election
      </VButton>
      <VButton
        variant="secondary"
        class="min-h-touch !border-red-700 !bg-red-950 !text-red-200 hover:!bg-red-900"
        @click="incidentOpen = true"
      >
        Emergency incident
      </VButton>
    </section>

    <section class="mt-6 grid grid-cols-1 gap-4 lg:grid-cols-2">
      <!-- Incident panel -->
      <div class="rounded-xl border border-slate-800 bg-slate-900 p-5">
        <h3 class="text-sm font-semibold uppercase tracking-wide text-slate-400">Incident panel</h3>
        <ul class="mt-4 space-y-3 text-sm">
          <li class="flex justify-between border-b border-slate-800 pb-2">
            <span class="text-slate-400">Open security alerts</span>
            <span class="font-mono text-white">{{ securityAlerts }}</span>
          </li>
          <li class="flex justify-between border-b border-slate-800 pb-2">
            <span class="text-slate-400">Open fraud cases</span>
            <span class="font-mono text-white">{{ fraudFlags }}</span>
          </li>
          <li class="flex justify-between">
            <span class="text-slate-400">Election status</span>
            <span class="font-medium capitalize text-white">{{ election.status || "—" }}</span>
          </li>
        </ul>
        <p class="mt-4 text-xs text-slate-500">
          Candidate rankings and live results remain sealed while the election is open.
        </p>
      </div>

      <!-- Events feed -->
      <div class="rounded-xl border border-slate-800 bg-slate-900 p-5">
        <ActivityFeed
          title="Recent events"
          :items="feedItems"
          :loading="operationsStore.loading && !feedItems.length"
          empty-title="Awaiting events"
          empty-description="Operational activity will stream here."
          class="!bg-transparent !shadow-none !ring-0 [&_h3]:!text-slate-400 [&_li]:!border-slate-800 [&_p]:!text-slate-300"
        />
      </div>
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
      description="Use this when an operational or security incident requires immediate attention. Election officers should coordinate with the Electoral Commission."
      variant="danger"
      icon="fraud"
      confirm-label="Acknowledge incident"
      @confirm="acknowledgeIncident"
    />
  </div>
</template>

<style scoped>
.control-room :deep(.rounded-xl.bg-white) {
  background-color: rgb(15 23 42);
}
</style>
