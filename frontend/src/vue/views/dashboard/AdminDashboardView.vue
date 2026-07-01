<script setup>
import { onMounted } from "vue";
import { useRouter } from "vue-router";
import LineChart from "@/components/charts/LineChart.vue";
import DonutChart from "@/components/charts/DonutChart.vue";
import {
  DashboardActivityTimeline,
  DashboardChartToolbar,
  DashboardKpiCard,
  DashboardQuickActions,
  DashboardSectionCard,
  DashboardUpcomingList,
  DashboardWelcomeBanner,
} from "@/components/dashboard/experience";
import { EmptyState, LoadingSkeleton, VAlert, VButton } from "@/components/ui";
import { useAdminCommandCenter } from "@/composables/useAdminCommandCenter";
import { useDashboardRealtime } from "@/composables/useDashboardRealtime";

const router = useRouter();
useDashboardRealtime("admin");

const {
  dashboardStore,
  isLive,
  chartRange,
  chartTimeRanges,
  welcomeBanner,
  kpiCards,
  votingActivityLabels,
  votingActivitySeries,
  hasVotingActivity,
  electionStatusItems,
  electionActivity,
  upcomingElections,
  quickActions,
  chartColors,
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
</script>

<template>
  <div class="min-h-full bg-surface-muted pb-10">
    <div class="space-y-6 px-page pt-6">
      <VAlert v-if="dashboardStore.error" variant="error">{{ dashboardStore.error }}</VAlert>
      <LoadingSkeleton v-if="dashboardStore.loading && !dashboardStore.adminOverview" variant="stats" :rows="8" />

      <template v-else>
        <DashboardWelcomeBanner
          v-bind="welcomeBanner"
          :is-live="isLive"
          subtitle="Here's the current status of the election platform."
        >
          <template #actions>
            <div class="flex flex-wrap gap-2">
              <VButton variant="secondary" size="sm" :loading="dashboardStore.loading" @click="refresh">
                Refresh
              </VButton>
              <VButton size="sm" @click="navigate('/dashboard/elections/create')">Create Election</VButton>
            </div>
          </template>
        </DashboardWelcomeBanner>

        <section aria-label="Election summary">
          <div class="grid grid-cols-1 gap-6 sm:grid-cols-2 xl:grid-cols-4 2xl:grid-cols-7">
            <DashboardKpiCard
              v-for="card in kpiCards"
              :key="card.id"
              v-bind="card"
              :clickable="Boolean(card.clickable && card.route)"
              @click="card.route && navigate(card.route)"
            />
          </div>
        </section>

        <section class="grid grid-cols-1 gap-6 xl:grid-cols-12">
          <DashboardSectionCard
            class="xl:col-span-8"
            title="Voting Activity"
            subtitle="Votes cast and turnout percentage — aggregate only, no candidate standings."
          >
            <template #actions>
              <DashboardChartToolbar v-model="chartRange" :ranges="chartTimeRanges" />
            </template>
            <LineChart
              v-if="hasVotingActivity"
              :labels="votingActivityLabels"
              :series="votingActivitySeries"
              :animated="isLive"
              height="320px"
            />
            <EmptyState
              v-else
              icon="analytics"
              title="No voting activity yet"
              description="Turnout and vote trends appear once voters begin casting ballots."
            />
          </DashboardSectionCard>

          <DashboardSectionCard
            class="xl:col-span-4"
            title="Election Status"
            subtitle="Distribution across the election lifecycle."
          >
            <DonutChart
              v-if="electionStatusItems.length"
              :items="electionStatusItems"
              :colors="chartColors"
              donut
              :animated="isLive"
              height="320px"
            />
            <EmptyState
              v-else
              icon="elections"
              title="No elections configured"
              description="Create an election to see lifecycle distribution."
            >
              <template #action>
                <VButton size="sm" @click="navigate('/dashboard/elections/create')">Create Election</VButton>
              </template>
            </EmptyState>
          </DashboardSectionCard>
        </section>

        <section class="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <DashboardSectionCard title="Recent Election Activity" subtitle="Operational events as they happen.">
            <DashboardActivityTimeline v-if="electionActivity.length" :items="electionActivity" />
            <EmptyState
              v-else
              icon="notifications"
              title="No election activity yet"
              description="Openings, approvals, and ballot events will stream here."
            />
          </DashboardSectionCard>

          <DashboardSectionCard title="Upcoming Elections" subtitle="Scheduled elections approaching their opening window.">
            <DashboardUpcomingList
              v-if="upcomingElections.length"
              :items="upcomingElections"
              @select="navigate"
            />
            <EmptyState
              v-else
              icon="elections"
              title="No upcoming elections"
              description="Scheduled elections will appear here before they open."
            >
              <template #action>
                <VButton variant="secondary" size="sm" @click="navigate('/dashboard/elections')">
                  View all elections
                </VButton>
              </template>
            </EmptyState>
          </DashboardSectionCard>
        </section>

        <DashboardSectionCard title="Quick Actions" subtitle="Common election officer workflows.">
          <DashboardQuickActions :actions="quickActions" @select="navigate" />
        </DashboardSectionCard>
      </template>
    </div>
  </div>
</template>
