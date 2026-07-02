<script setup>
import { defineAsyncComponent, onMounted } from "vue";
import { useRouter } from "vue-router";
import {
  AdminCommandHero,
  AdminElectionPulseCard,
  AdminElectionsTable,
} from "@/components/dashboard/admin";
import {
  DashboardChartToolbar,
  DashboardKpiCard,
  DashboardQuickActions,
  DashboardSectionCard,
} from "@/components/dashboard/experience";
import { EmptyState, LoadingSkeleton, VAlert, VButton } from "@/components/ui";
import { useAdminCommandCenter } from "@/composables/useAdminCommandCenter";
import { useDashboardRealtime } from "@/composables/useDashboardRealtime";

const LineChart = defineAsyncComponent(() => import("@/components/charts/LineChart.vue"));
const PieChart = defineAsyncComponent(() => import("@/components/charts/PieChart.vue"));

const router = useRouter();
useDashboardRealtime("admin");

const {
  dashboardStore,
  isLive,
  chartRange,
  chartTimeRanges,
  heroConfig,
  kpiCards,
  pulseElections,
  electionTableRows,
  electionStatusItems,
  votingActivityLabels,
  votingActivitySeries,
  isWaitingForVotes,
  hasVotingActivity,
  quickActions,
  loadCommandCenter,
} = useAdminCommandCenter();

onMounted(() => {
  loadCommandCenter().catch(() => {});
});

function refresh() {
  loadCommandCenter().catch(() => {});
}

function navigate(route) {
  if (route) router.push(route);
}

function openElection(uuid) {
  if (uuid) router.push(`/dashboard/elections/${uuid}`);
}
</script>

<template>
  <div class="min-h-full bg-surface-muted pb-12">
    <div class="mx-auto max-w-[1440px] space-y-6 px-page pt-6">
      <VAlert v-if="dashboardStore.error" variant="error">{{ dashboardStore.error }}</VAlert>
      <LoadingSkeleton v-if="dashboardStore.loading && !dashboardStore.adminOverview" variant="stats" :rows="6" />

      <template v-else>
        <div class="flex flex-wrap items-center justify-end gap-2">
          <span
            v-if="isLive"
            class="inline-flex items-center gap-1.5 rounded-full bg-success-50 px-3 py-1 text-xs font-semibold text-success-700"
          >
            <span class="h-2 w-2 animate-pulse rounded-full bg-success-600" aria-hidden="true" />
            Live feed connected
          </span>
          <VButton variant="secondary" size="sm" :loading="dashboardStore.loading" @click="refresh">
            Refresh
          </VButton>
        </div>

        <section class="grid grid-cols-1 gap-6 xl:grid-cols-12">
          <div class="xl:col-span-8">
            <AdminCommandHero
              v-bind="heroConfig"
              @primary="navigate(heroConfig.monitorRoute)"
              @secondary="navigate('/dashboard/elections')"
            />
          </div>

          <DashboardSectionCard
            class="xl:col-span-4"
            title="Election pipeline"
            subtitle="Lifecycle distribution across your institution."
            no-padding
          >
            <div class="p-6 pt-2">
              <PieChart
                v-if="electionStatusItems.length"
                :items="electionStatusItems"
                donut
                height="300px"
              />
              <EmptyState
                v-else
                icon="elections"
                title="No elections yet"
                description="Create your first election to see pipeline distribution."
              />
            </div>
          </DashboardSectionCard>
        </section>

        <section aria-label="Summary metrics" class="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <DashboardKpiCard
            v-for="card in kpiCards"
            :key="card.id"
            v-bind="card"
            :clickable="Boolean(card.clickable && card.route)"
            @click="card.route && navigate(card.route)"
          />
        </section>

        <section v-if="pulseElections.length" aria-label="Election spotlight">
          <div class="mb-4 flex items-end justify-between gap-3">
            <div>
              <h2 class="text-lg font-semibold text-ink-primary">Election spotlight</h2>
              <p class="mt-1 text-sm text-ink-secondary">
                Ballot readiness and live turnout — aggregate only, no candidate rankings.
              </p>
            </div>
          </div>
          <div class="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
            <AdminElectionPulseCard
              v-for="election in pulseElections"
              :key="election.uuid"
              :election="election"
              :turnout-metric-label="election.turnoutMetricLabel"
              @open="openElection"
            />
          </div>
        </section>

        <DashboardSectionCard
          title="Voting activity"
          subtitle="Hourly ballots cast — sanitized live feed while elections are open."
        >
          <template #actions>
            <DashboardChartToolbar v-model="chartRange" :ranges="chartTimeRanges" />
          </template>
          <p
            v-if="isWaitingForVotes"
            class="mb-4 rounded-input border border-border bg-brand-50/60 px-4 py-3 text-sm text-ink-secondary"
          >
            Voting is open but no ballots have been cast yet. This chart updates automatically as students vote.
          </p>
          <LineChart
            v-if="hasVotingActivity"
            :labels="votingActivityLabels"
            :series="votingActivitySeries"
            :smooth="0.42"
            :animated="isLive"
            height="320px"
          />
        </DashboardSectionCard>

        <AdminElectionsTable :rows="electionTableRows" @select="openElection" />

        <DashboardSectionCard title="Quick actions" subtitle="Jump to common election officer workflows.">
          <DashboardQuickActions :actions="quickActions" @select="navigate" />
        </DashboardSectionCard>
      </template>
    </div>
  </div>
</template>
