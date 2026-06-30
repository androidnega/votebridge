<script setup>
import { onMounted, onUnmounted } from "vue";
import { ConnectionStatusIndicator } from "@/components/dashboard";
import ElectionStatusBadge from "@/components/voting/ElectionStatusBadge.vue";
import { operationsNav } from "@/config/moduleNav";
import { EmptyState, LoadingSkeleton, ModuleNav, PageHeader, VAlert, VCard } from "@/components/ui";
import { useOperationsStore } from "@/stores/operations";

const store = useOperationsStore();

onMounted(() => {
  store.fetchElectionMonitor().catch(() => {});
  store.connectRealtime();
});

onUnmounted(() => store.disconnectRealtime());
</script>

<template>
  <div class="vb-page">
    <PageHeader
      title="Election monitor"
      subtitle="Active elections with turnout and alert metrics — no candidate rankings while open."
      :breadcrumbs="[{ label: 'Dashboard', to: '/dashboard' }, { label: 'Operations', to: '/dashboard/operations' }, { label: 'Election Monitor' }]"
    >
      <template #actions>
        <ConnectionStatusIndicator :status="store.realtimeStatus" />
      </template>
    </PageHeader>

    <ModuleNav :items="operationsNav" />
    <VAlert v-if="store.error" variant="error">{{ store.error }}</VAlert>
    <LoadingSkeleton v-if="store.loading && !store.elections.length" variant="list" :rows="4" />

    <div v-else-if="store.elections.length" class="grid grid-cols-1 gap-4 lg:grid-cols-2">
      <VCard v-for="election in store.elections" :key="election.election_uuid" padding="none">
        <div class="border-b border-border p-card">
          <div class="flex flex-wrap items-center gap-2">
            <h3 class="font-semibold text-slate-800">{{ election.election_title }}</h3>
            <ElectionStatusBadge :status="election.election_status" />
          </div>
        </div>
        <dl class="grid grid-cols-2 gap-3 p-card text-sm">
          <div><dt class="text-slate-500">Turnout</dt><dd class="font-semibold">{{ election.turnout_percentage ?? 0 }}%</dd></div>
          <div><dt class="text-slate-500">Participated</dt><dd class="font-semibold">{{ election.voters_participated ?? 0 }}</dd></div>
          <div><dt class="text-slate-500">Fraud alerts</dt><dd class="font-semibold">{{ election.open_fraud_cases ?? 0 }}</dd></div>
          <div><dt class="text-slate-500">Security alerts</dt><dd class="font-semibold">{{ election.open_alerts ?? 0 }}</dd></div>
          <div class="col-span-2">
            <dt class="text-slate-500">Channels</dt>
            <dd class="mt-1">
              <span v-if="election.voting_channels?.web" class="mr-2 text-brand-600">Web</span>
              <span v-if="election.voting_channels?.ussd" class="text-brand-600">USSD</span>
            </dd>
          </div>
        </dl>
      </VCard>
    </div>

    <EmptyState v-else title="No active elections" description="Open or paused elections appear here." icon="elections" />
  </div>
</template>
