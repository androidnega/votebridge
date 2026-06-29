<script setup>
import { computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import {
  ActivityFeed,
  ConnectionStatusIndicator,
  ElectionCard,
  LiveTurnoutWidget,
  LoadingSkeleton,
  PlatformHealthWidgets,
  StatCard,
} from "@/components/dashboard";
import { VAlert, VButton } from "@/components/ui";
import { useDashboardRealtime } from "@/composables/useDashboardRealtime";
import { useDashboardStore } from "@/stores/dashboard";

const router = useRouter();
const dashboardStore = useDashboardStore();
const realtime = useDashboardRealtime("admin");

const overview = computed(() => dashboardStore.adminOverview || {});
const alertSummary = computed(() => overview.value.security_alerts || {});
const fraudSummary = computed(() => overview.value.fraud_cases || {});

const activityItems = computed(() => {
  if (dashboardStore.activityFeed.length) {
    return dashboardStore.activityFeed;
  }
  const fallback = [];
  if (alertSummary.value.open) {
    fallback.push({
      id: "open-alerts",
      title: `${alertSummary.value.open} open security alerts`,
      description: "Review and resolve pending alerts in Security Center.",
      created_at: new Date().toISOString(),
    });
  }
  if (fraudSummary.value.open_cases) {
    fallback.push({
      id: "open-fraud",
      title: `${fraudSummary.value.open_cases} open fraud cases`,
      description: "Investigate flagged activity in Fraud Dashboard.",
      created_at: new Date().toISOString(),
    });
  }
  return fallback;
});

onMounted(() => {
  dashboardStore.fetchAdminDashboard().catch(() => {});
});
</script>

<template>
  <div class="space-y-8">
    <div class="flex flex-wrap items-start justify-between gap-4">
      <div>
        <div class="flex flex-wrap items-center gap-3">
          <h2 class="text-2xl font-bold text-slate-900">Admin overview</h2>
          <ConnectionStatusIndicator
            :status="realtime.status.value"
            :label="realtime.label.value"
          />
        </div>
        <p class="mt-1 text-sm text-slate-500">Election operations and security at a glance.</p>
      </div>
      <div class="flex flex-wrap gap-2">
        <VButton variant="secondary" size="sm" @click="router.push('/elections')">Manage elections</VButton>
        <VButton variant="secondary" size="sm" @click="router.push('/reports')">Reports</VButton>
      </div>
    </div>

    <VAlert v-if="dashboardStore.error" variant="error">{{ dashboardStore.error }}</VAlert>

    <LoadingSkeleton v-if="dashboardStore.loading && !dashboardStore.adminOverview" variant="stats" :rows="4" />

    <section class="grid grid-cols-1 gap-4 lg:grid-cols-3">
      <div class="lg:col-span-2 grid grid-cols-1 gap-4 sm:grid-cols-2">
        <StatCard
          label="Total elections"
          :value="dashboardStore.totalElectionsCount"
          :loading="dashboardStore.loading"
          accent="slate"
        />
        <StatCard
          label="Open elections"
          :value="overview.active_elections ?? 0"
          hint="Currently open or paused"
          :loading="dashboardStore.loading"
          accent="green"
        />
        <StatCard
          label="Votes cast"
          :value="dashboardStore.totalVotesCast"
          :loading="dashboardStore.loading"
          accent="brand"
        />
        <StatCard
          label="Pending alerts"
          :value="alertSummary.open ?? 0"
          hint="Open security alerts"
          :loading="dashboardStore.loading"
          accent="red"
        />
      </div>

      <LiveTurnoutWidget
        :percentage="dashboardStore.turnoutPercentage"
        :votes-cast="dashboardStore.totalVotesCast"
        :registered-voters="dashboardStore.registeredVoters"
        :loading="dashboardStore.loading"
        :live="realtime.isLive.value"
        :status="realtime.status.value"
      />
    </section>

    <PlatformHealthWidgets />

    <section class="grid grid-cols-1 gap-6 lg:grid-cols-2">
      <div>
        <h3 class="mb-4 text-lg font-semibold text-slate-900">Open elections</h3>
        <div v-if="dashboardStore.openElectionsList.length" class="grid grid-cols-1 gap-4">
          <ElectionCard
            v-for="election in dashboardStore.openElectionsList"
            :key="election.uuid"
            :election="election"
          />
        </div>
        <p v-else class="text-sm text-slate-500">No elections are currently open.</p>
      </div>

      <ActivityFeed
        title="Live activity"
        :items="activityItems"
        :loading="dashboardStore.loading"
        empty-title="All clear"
        empty-description="No pending alerts or fraud cases require attention."
      />
    </section>
  </div>
</template>
