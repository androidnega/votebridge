<script setup>
import { computed, onMounted, onUnmounted } from "vue";
import { useRouter } from "vue-router";
import {
  ActivityFeed,
  ConnectionStatusIndicator,
  ElectionCard,
  LiveSecurityFeed,
  LoadingSkeleton,
  PlatformHealthWidgets,
  StatCard,
} from "@/components/dashboard";
import { VAlert, VButton } from "@/components/ui";
import { useDashboardRealtime } from "@/composables/useDashboardRealtime";
import { useDashboardStore } from "@/stores/dashboard";
import { useOperationsStore } from "@/stores/operations";
import { useSecurityStore } from "@/stores/security";

const router = useRouter();
const dashboardStore = useDashboardStore();
const securityStore = useSecurityStore();
const operationsStore = useOperationsStore();
const realtime = useDashboardRealtime("super-admin");

const overview = computed(() => dashboardStore.adminOverview || {});
const alertSummary = computed(() => overview.value.security_alerts || {});

const securityFeedItems = computed(() => {
  if (securityStore.alertsFeed.length) return securityStore.alertsFeed.slice(0, 6);
  return dashboardStore.securityFeed?.alerts?.slice(0, 6) || [];
});

const activityItems = computed(() => {
  if (dashboardStore.activityFeed.length) return dashboardStore.activityFeed;
  const fallback = [];
  if (alertSummary.value.open) {
    fallback.push({
      id: "open-alerts",
      title: `${alertSummary.value.open} open security alerts`,
      description: "Review alerts in Strong room.",
      created_at: new Date().toISOString(),
    });
  }
  return fallback;
});

onMounted(() => {
  dashboardStore.fetchSuperAdminDashboard().catch(() => {});
  operationsStore.fetchOverview().catch(() => {});
  securityStore.fetchSecurityFeed().catch(() => {});
  securityStore.connectRealtime();
});

onUnmounted(() => {
  securityStore.disconnectRealtime();
});
</script>

<template>
  <div class="space-y-8">
    <div class="flex flex-wrap items-start justify-between gap-4">
      <div>
        <div class="flex flex-wrap items-center gap-3">
          <h2 class="text-2xl font-bold text-slate-900">Election command center</h2>
          <ConnectionStatusIndicator
            :status="realtime.status.value"
            :label="realtime.label.value"
          />
        </div>
        <p class="mt-1 text-sm text-slate-500">
          Election status, turnout, and platform health at a glance.
        </p>
      </div>
      <div class="flex flex-wrap gap-2">
        <VButton variant="secondary" size="sm" @click="router.push('/elections')">Elections</VButton>
        <VButton variant="secondary" size="sm" @click="router.push('/reports')">Reports</VButton>
        <VButton variant="secondary" size="sm" @click="router.push('/strongroom')">Strong room</VButton>
        <VButton variant="secondary" size="sm" @click="router.push('/settings')">Settings</VButton>
      </div>
    </div>

    <VAlert v-if="dashboardStore.error" variant="error">{{ dashboardStore.error }}</VAlert>

    <LoadingSkeleton
      v-if="dashboardStore.loading && !dashboardStore.adminOverview"
      variant="stats"
      :rows="4"
    />

    <section v-else class="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <StatCard
        label="Open elections"
        :value="operationsStore.overview?.elections?.open ?? overview.active_elections ?? 0"
        hint="Currently open or paused"
        accent="green"
      />
      <StatCard
        label="Turnout"
        :value="`${overview.turnout_percentage ?? 0}%`"
        :hint="`${overview.total_votes_cast ?? 0} votes cast`"
        accent="brand"
      />
      <StatCard
        label="Security alerts"
        :value="alertSummary.open ?? 0"
        hint="Require attention"
        accent="red"
      />
      <StatCard
        label="Total elections"
        :value="dashboardStore.totalElectionsCount"
        accent="slate"
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
        title="Recent activity"
        :items="activityItems"
        :loading="dashboardStore.loading"
        empty-title="All clear"
        empty-description="No recent platform activity to show."
      />
    </section>

    <LiveSecurityFeed
      title="Security alerts"
      :items="securityFeedItems"
      :loading="securityStore.loading && !securityFeedItems.length"
      :status="securityStore.realtimeStatus"
    />
  </div>
</template>
