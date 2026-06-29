<script setup>
import { computed, onMounted, onUnmounted } from "vue";
import { useRoute } from "vue-router";
import { LiveTurnoutWidget } from "@/components/dashboard";
import ElectionStatusBadge from "@/components/voting/ElectionStatusBadge.vue";
import { VAlert, VCard } from "@/components/ui";
import { useDashboardRealtime } from "@/composables/useDashboardRealtime";
import { useElectionStore } from "@/stores/election";
import { useOperationsStore } from "@/stores/operations";

const route = useRoute();
const electionStore = useElectionStore();
const operationsStore = useOperationsStore();
const realtime = useDashboardRealtime("admin");

const electionUuid = computed(() => route.params.uuid);
const election = computed(() => electionStore.currentElection || {});

const monitorRow = computed(() =>
  (operationsStore.elections || []).find((row) => row.election_uuid === electionUuid.value)
);

onMounted(async () => {
  await electionStore.fetchElection(electionUuid.value).catch(() => {});
  await operationsStore.fetchElectionMonitor().catch(() => {});
});

onUnmounted(() => {
  operationsStore.disconnectRealtime?.();
});
</script>

<template>
  <div class="space-y-section">
    <VAlert v-if="electionStore.error" variant="error">{{ electionStore.error }}</VAlert>

    <div class="flex flex-wrap items-center gap-3">
      <h3 class="text-lg font-semibold text-slate-900">Live election monitor</h3>
      <ElectionStatusBadge :status="election.status" />
    </div>

    <section class="grid grid-cols-1 gap-4 lg:grid-cols-3">
      <LiveTurnoutWidget
        class="lg:col-span-1"
        :percentage="monitorRow?.turnout_percentage ?? 0"
        :votes-cast="monitorRow?.voters_participated ?? 0"
        :registered-voters="monitorRow?.eligible_voters ?? 0"
        :loading="operationsStore.loading"
        :live="realtime.isLive.value"
        :status="realtime.status.value"
      />

      <VCard title="Channel activity" class="lg:col-span-2">
        <dl class="grid grid-cols-2 gap-4 text-sm">
          <div>
            <dt class="text-slate-500">Security alerts</dt>
            <dd class="text-xl font-semibold">{{ monitorRow?.open_alerts ?? 0 }}</dd>
          </div>
          <div>
            <dt class="text-slate-500">Fraud flags</dt>
            <dd class="text-xl font-semibold">{{ monitorRow?.open_fraud_cases ?? 0 }}</dd>
          </div>
          <div>
            <dt class="text-slate-500">Web voting</dt>
            <dd class="font-medium">{{ monitorRow?.voting_channels?.web ? "Enabled" : "Off" }}</dd>
          </div>
          <div>
            <dt class="text-slate-500">USSD voting</dt>
            <dd class="font-medium">{{ monitorRow?.voting_channels?.ussd ? "Enabled" : "Off" }}</dd>
          </div>
        </dl>
        <p class="mt-4 text-xs text-slate-500">
          Candidate rankings and live results remain hidden while the election is open.
        </p>
      </VCard>
    </section>
  </div>
</template>
