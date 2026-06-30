<script setup>
import { computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import {
  ActivityFeed,
  ConnectionStatusIndicator,
  ElectionCard,
  EmptyState,
  LiveTurnoutWidget,
  LoadingSkeleton,
  StatCard,
} from "@/components/dashboard";
import { ElectionContextBanner } from "@/components/elections";
import { VAlert, VButton, VCard, PageHeader } from "@/components/ui";
import { emptyStates } from "@/config/emptyStates";
import { useDashboardRealtime } from "@/composables/useDashboardRealtime";
import { useDashboardStore } from "@/stores/dashboard";
import { useResultsStore } from "@/stores/results";

const router = useRouter();
const dashboardStore = useDashboardStore();
const resultsStore = useResultsStore();
const realtime = useDashboardRealtime("admin");

const overview = computed(() => dashboardStore.adminOverview || {});
const alertSummary = computed(() => overview.value.security_alerts || {});

const primaryElection = computed(() => dashboardStore.openElectionsList[0] || null);

const electionHealthLevel = computed(() => {
  if (alertSummary.value.open > 0) return "critical";
  const status = primaryElection.value?.status || primaryElection.value?.election_status;
  if (status === "paused") return "attention";
  return "healthy";
});

const nextAction = computed(() => {
  const election = primaryElection.value;
  if (!election) return null;
  const uuid = election.uuid || election.election_uuid;
  const status = election.status || election.election_status;
  if (status === "open") {
    return { label: "Open control room", route: `/dashboard/elections/${uuid}/monitor` };
  }
  if (status === "paused") {
    return { label: "Review election", route: `/dashboard/elections/${uuid}` };
  }
  return { label: "Manage election", route: `/dashboard/elections/${uuid}` };
});

const taskItems = computed(() => {
  const items = [];
  if (alertSummary.value.open) {
    items.push({
      id: "alerts",
      title: `${alertSummary.value.open} security alerts`,
      description: "Review in Reports or contact the super admin.",
    });
  }
  if (primaryElection.value) {
    const status = primaryElection.value.status || primaryElection.value.election_status;
    if (status === "paused") {
      items.push({
        id: "paused",
        title: "Election is paused",
        description: "Resume voting when ready from the election workspace.",
      });
    }
  }
  return items;
});

onMounted(() => {
  dashboardStore.fetchAdminDashboard().catch(() => {});
  resultsStore.fetchQueues().catch(() => {});
});
</script>

<template>
  <div class="vb-page">
    <PageHeader title="Election officer dashboard" subtitle="Active election context and operational health.">
      <template #actions>
        <ConnectionStatusIndicator :status="realtime.status.value" :label="realtime.label.value" />
        <VButton @click="router.push('/dashboard/elections/create')">Create election</VButton>
        <VButton variant="secondary" size="sm" @click="router.push('/dashboard/elections')">All elections</VButton>
      </template>
    </PageHeader>

    <VAlert v-if="dashboardStore.error" variant="error">{{ dashboardStore.error }}</VAlert>
    <LoadingSkeleton v-if="dashboardStore.loading && !dashboardStore.adminOverview" variant="stats" :rows="3" />

    <template v-else>
      <ElectionContextBanner
        v-if="primaryElection"
        :election="primaryElection"
        :turnout-percentage="overview.turnout_percentage"
        :health-level="electionHealthLevel"
        :next-action="nextAction"
      />

      <section class="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <StatCard
          label="Open elections"
          :value="overview.active_elections ?? 0"
          hint="Currently open or paused"
          accent="green"
        />
        <LiveTurnoutWidget
          :percentage="dashboardStore.turnoutPercentage"
          :votes-cast="dashboardStore.totalVotesCast"
          :registered-voters="dashboardStore.registeredVoters"
          :loading="dashboardStore.loading"
          :live="realtime.isLive.value"
          :status="realtime.status.value"
        />
        <VCard title="Next required actions" padding="sm">
          <ul v-if="taskItems.length" class="space-y-3 text-sm text-slate-700">
            <li v-for="item in taskItems" :key="item.id">
              <p class="font-medium text-slate-900">{{ item.title }}</p>
              <p class="mt-0.5 text-slate-500">{{ item.description }}</p>
            </li>
          </ul>
          <p v-else class="text-sm text-slate-500">No urgent tasks — you're up to date.</p>
        </VCard>
      </section>

      <section>
        <h3 class="vb-section-title mb-4">Open elections</h3>
        <LoadingSkeleton v-if="dashboardStore.loading" variant="card" />
        <div v-else-if="dashboardStore.openElectionsList.length" class="grid grid-cols-1 gap-4 md:grid-cols-2">
          <ElectionCard
            v-for="election in dashboardStore.openElectionsList"
            :key="election.uuid"
            :election="election"
          />
        </div>
        <EmptyState v-else v-bind="emptyStates.openElections">
          <template #action>
            <VButton @click="router.push('/dashboard/elections/create')">Create election</VButton>
          </template>
        </EmptyState>
      </section>
    </template>
  </div>
</template>
