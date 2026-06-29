<script setup>
import { computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import {
  ConnectionStatusIndicator,
  ElectionCard,
  LiveSecurityFeed,
  LoadingSkeleton,
  StatCard,
} from "@/components/dashboard";
import OpsHealthBadge from "@/components/operations/OpsHealthBadge.vue";
import { VAlert, VButton, VCard } from "@/components/ui";
import { useDashboardRealtime } from "@/composables/useDashboardRealtime";
import { useDashboardStore } from "@/stores/dashboard";
import { useOperationsStore } from "@/stores/operations";
import { useResultsStore } from "@/stores/results";
import { useSecurityStore } from "@/stores/security";

const router = useRouter();
const dashboardStore = useDashboardStore();
const securityStore = useSecurityStore();
const operationsStore = useOperationsStore();
const resultsStore = useResultsStore();
const realtime = useDashboardRealtime("super-admin");

const overview = computed(() => dashboardStore.adminOverview || {});
const alertSummary = computed(() => overview.value.security_alerts || {});
const healthStatus = computed(() => operationsStore.overview?.system_health?.status || "unknown");

const securityFeedItems = computed(() => securityStore.alertsFeed.slice(0, 5));

onMounted(() => {
  dashboardStore.fetchSuperAdminDashboard().catch(() => {});
  operationsStore.fetchOverview().catch(() => {});
  resultsStore.fetchQueues().catch(() => {});
  securityStore.fetchSecurityFeed().catch(() => {});
});
</script>

<template>
  <div class="space-y-8">
    <div class="flex flex-wrap items-start justify-between gap-4">
      <div>
        <div class="flex flex-wrap items-center gap-3">
          <h2 class="text-2xl font-bold text-slate-900">Election command center</h2>
          <ConnectionStatusIndicator :status="realtime.status.value" :label="realtime.label.value" />
        </div>
        <p class="mt-1 text-sm text-slate-500">Active elections, certifications, and platform health.</p>
      </div>
      <div class="flex flex-wrap gap-2">
        <VButton variant="secondary" size="sm" @click="router.push('/elections')">Election workspace</VButton>
        <VButton variant="secondary" size="sm" @click="router.push('/results/certification')">Certification</VButton>
      </div>
    </div>

    <VAlert v-if="dashboardStore.error" variant="error">{{ dashboardStore.error }}</VAlert>
    <LoadingSkeleton v-if="dashboardStore.loading && !dashboardStore.adminOverview" variant="stats" :rows="4" />

    <section v-else class="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-5">
      <StatCard
        label="Open elections"
        :value="operationsStore.overview?.elections?.open ?? overview.active_elections ?? 0"
        accent="green"
      />
      <StatCard
        label="Students voted"
        :value="overview.total_votes_cast ?? 0"
        :hint="`${overview.turnout_percentage ?? 0}% turnout`"
        accent="brand"
      />
      <StatCard
        label="Certifications waiting"
        :value="resultsStore.certificationQueue?.length ?? 0"
        accent="amber"
      />
      <StatCard label="Security issues" :value="alertSummary.open ?? 0" accent="red" />
      <VCard title="Platform health" padding="compact">
        <OpsHealthBadge :status="healthStatus" />
        <VButton class="mt-3" size="sm" variant="secondary" @click="router.push('/operations/health')">
          View details
        </VButton>
      </VCard>
    </section>

    <section>
      <h3 class="mb-4 text-lg font-semibold text-slate-900">Open elections</h3>
      <div v-if="dashboardStore.openElectionsList.length" class="grid grid-cols-1 gap-4 md:grid-cols-2">
        <ElectionCard
          v-for="election in dashboardStore.openElectionsList"
          :key="election.uuid"
          :election="election"
        />
      </div>
      <p v-else class="text-sm text-slate-500">No elections are currently open.</p>
    </section>

    <LiveSecurityFeed
      v-if="securityFeedItems.length"
      title="Recent security alerts"
      :items="securityFeedItems"
      :loading="securityStore.loading"
      :status="securityStore.realtimeStatus"
    />
  </div>
</template>
