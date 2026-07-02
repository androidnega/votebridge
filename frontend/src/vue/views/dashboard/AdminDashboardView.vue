<script setup>
import { defineAsyncComponent, onMounted } from "vue";
import { useRouter } from "vue-router";
import {
  AdminCommandHero,
  AdminElectionCandidateSpotlight,
} from "@/components/dashboard/admin";
import {
  DashboardChartToolbar,
  DashboardKpiCard,
  DashboardSectionCard,
} from "@/components/dashboard/experience";
import { EmptyState, LoadingSkeleton, VAlert } from "@/components/ui";
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
  spotlightElection,
  spotlightCandidates,
  candidatesLoading,
  electionStatusItems,
  votingActivityLabels,
  votingActivitySeries,
  isWaitingForVotes,
  hasVotingActivity,
  loadCommandCenter,
} = useAdminCommandCenter();

onMounted(() => {
  loadCommandCenter().catch(() => {});
});

function navigate(route) {
  if (route) router.push(route);
}

function openElectionWorkspace(uuid) {
  if (uuid) router.push(`/dashboard/elections/${uuid}/candidates`);
}
</script>

<template>
  <div class="vb-page">
    <VAlert v-if="dashboardStore.error" variant="error">{{ dashboardStore.error }}</VAlert>
    <LoadingSkeleton v-if="dashboardStore.loading && !dashboardStore.adminOverview" variant="stats" :rows="6" />

    <template v-else>
      <section class="grid grid-cols-1 items-stretch gap-4 sm:gap-6 xl:grid-cols-12">
        <div class="flex xl:col-span-8">
          <AdminCommandHero
            class="w-full"
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
          <div class="flex flex-1 items-center justify-center p-4 sm:p-5">
            <PieChart
              v-if="electionStatusItems.length"
              :items="electionStatusItems"
              donut
              height="220px"
              class="w-full"
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

      <AdminElectionCandidateSpotlight
        :election="spotlightElection"
        :candidates="spotlightCandidates"
        :loading="candidatesLoading"
        @open-workspace="openElectionWorkspace"
      />

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
    </template>
  </div>
</template>
