<script setup>
import { onMounted } from "vue";
import { useRouter } from "vue-router";
import {
  AdminActiveElectionCard,
  AdminCommandSectionCard,
  AdminElectionLifecycle,
  AdminKpiCard,
  AdminLiveMonitoringList,
  AdminQuickActionGrid,
} from "@/components/admin";
import LineChart from "@/components/charts/LineChart.vue";
import DonutChart from "@/components/charts/DonutChart.vue";
import { ElectionReadinessPanel } from "@/components/elections";
import { GovernanceActivityFeed } from "@/components/governance";
import { EmptyState, LoadingSkeleton, VAlert, VButton } from "@/components/ui";
import { useAdminCommandCenter } from "@/composables/useAdminCommandCenter";
import { useDashboardRealtime } from "@/composables/useDashboardRealtime";

const router = useRouter();
const realtime = useDashboardRealtime("admin");

const {
  dashboardStore,
  electionStore,
  isLive,
  kpiCards,
  activeElectionCards,
  showReadiness,
  turnoutLabels,
  turnoutSeries,
  hasTurnoutTrend,
  channelDistribution,
  liveMonitoringItems,
  lifecycleStages,
  lifecycleStage,
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
  <div class="min-h-full bg-[#F8FAFC] pb-10">
    <header class="border-b border-[#E5E7EB] bg-white">
      <div class="flex flex-col gap-5 px-page py-6 lg:flex-row lg:items-center lg:justify-between">
        <div class="min-w-0">
          <p class="text-xs font-semibold uppercase tracking-wider text-[#64748B]">Dashboard</p>
          <h1 class="mt-1 text-2xl font-semibold tracking-tight text-[#1F2937] lg:text-[1.75rem]">
            Election Command Center
          </h1>
          <p class="mt-2 text-sm text-[#64748B]">
            Manage, monitor and supervise election operations.
          </p>
        </div>

        <div class="flex flex-wrap items-stretch gap-3">
          <span
            v-if="isLive"
            class="inline-flex min-h-touch items-center gap-1.5 self-stretch rounded-input border border-[#16A34A]/20 bg-[#16A34A]/10 px-3 text-xs font-semibold text-[#16A34A]"
          >
            <span class="h-2 w-2 animate-pulse rounded-full bg-[#16A34A]" aria-hidden="true" />
            Live
          </span>
          <VButton
            variant="secondary"
            size="sm"
            class="min-h-touch self-stretch"
            :loading="dashboardStore.loading"
            @click="refresh"
          >
            Refresh
          </VButton>
          <VButton class="min-h-touch self-stretch" @click="navigate('/dashboard/elections/create')">
            Create Election
          </VButton>
        </div>
      </div>
    </header>

    <div class="space-y-8 px-page pt-8">
      <VAlert v-if="dashboardStore.error" variant="error">{{ dashboardStore.error }}</VAlert>
      <LoadingSkeleton v-if="dashboardStore.loading && !dashboardStore.adminOverview" variant="stats" :rows="8" />

      <template v-else>
        <!-- Row 1: KPIs -->
        <section aria-label="Key indicators">
          <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-5">
            <AdminKpiCard v-for="card in kpiCards" :key="card.id" v-bind="card" />
          </div>
        </section>

        <!-- Row 2: Active elections + Readiness -->
        <section class="grid grid-cols-1 gap-6 xl:grid-cols-12">
          <AdminCommandSectionCard
            class="xl:col-span-8"
            title="Active Elections"
            subtitle="Open and paused elections with live turnout and control room access."
          >
            <div v-if="activeElectionCards.length" class="grid grid-cols-1 gap-4 md:grid-cols-2">
              <AdminActiveElectionCard
                v-for="item in activeElectionCards"
                :key="item.uuid"
                :election="item.election"
                :turnout="item.turnout"
                :monitor-route="item.monitorRoute"
              />
            </div>
            <EmptyState
              v-else
              icon="elections"
              title="No active elections"
              description="When an election is open or paused, it will appear here for operational monitoring."
            />
          </AdminCommandSectionCard>

          <AdminCommandSectionCard
            v-if="showReadiness"
            class="xl:col-span-4"
            title="Readiness Checklist"
            subtitle="Complete all checks before opening the election."
          >
            <ElectionReadinessPanel
              :report="electionStore.readinessReport"
              :loading="electionStore.readinessLoading"
            />
          </AdminCommandSectionCard>
        </section>

        <!-- Row 3: Turnout trend + Channel distribution -->
        <section class="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <AdminCommandSectionCard title="Live Turnout Trend" subtitle="Aggregate turnout over time — no candidate standings.">
            <LineChart
              v-if="hasTurnoutTrend"
              :labels="turnoutLabels"
              :series="turnoutSeries"
              :animated="isLive"
              height="280px"
            />
            <EmptyState
              v-else
              icon="analytics"
              title="No turnout data yet"
              description="Turnout trends appear once voters begin casting ballots."
            />
          </AdminCommandSectionCard>

          <AdminCommandSectionCard
            title="Voting Channel Distribution"
            subtitle="Web vs USSD voter participation."
          >
            <DonutChart
              v-if="channelDistribution.length"
              :items="channelDistribution"
              :colors="chartColors"
              donut
              :animated="isLive"
              height="280px"
            />
            <EmptyState
              v-else
              icon="analytics"
              title="No channel data yet"
              description="Channel distribution appears once votes are recorded."
            />
          </AdminCommandSectionCard>
        </section>

        <!-- Row 4: Live monitoring + Lifecycle -->
        <section class="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <AdminCommandSectionCard title="Live Monitoring" subtitle="Sessions, channels, and election integrity signals.">
            <AdminLiveMonitoringList :items="liveMonitoringItems" />
          </AdminCommandSectionCard>

          <AdminCommandSectionCard title="Election Lifecycle" subtitle="Current stage in the election operations pipeline.">
            <AdminElectionLifecycle :stages="lifecycleStages" :current-stage="lifecycleStage" />
          </AdminCommandSectionCard>
        </section>

        <!-- Row 5: Activity + Upcoming -->
        <section class="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <AdminCommandSectionCard title="Election Activity Feed" subtitle="Election-related actions as they happen.">
            <GovernanceActivityFeed v-if="electionActivity.length" :items="electionActivity" />
            <EmptyState
              v-else
              icon="notifications"
              title="No election activity yet"
              description="Ballots, openings, and election events will stream here."
            />
          </AdminCommandSectionCard>

          <AdminCommandSectionCard title="Upcoming Elections" subtitle="Scheduled elections approaching their opening window.">
            <ul v-if="upcomingElections.length" class="space-y-3">
              <li
                v-for="item in upcomingElections"
                :key="item.id"
                class="flex items-center justify-between gap-4 rounded-input border border-[#E5E7EB] bg-[#F8FAFC] px-4 py-3"
              >
                <div class="min-w-0">
                  <p class="truncate text-sm font-medium text-[#1F2937]">{{ item.title }}</p>
                  <p class="mt-0.5 text-xs text-[#64748B]">
                    Opens {{ item.startDate ? new Date(item.startDate).toLocaleString() : "—" }}
                  </p>
                </div>
                <VButton variant="secondary" size="sm" @click="navigate(item.route)">View</VButton>
              </li>
            </ul>
            <EmptyState
              v-else
              icon="elections"
              title="No upcoming elections"
              description="Scheduled elections will appear here before they open."
            />
          </AdminCommandSectionCard>
        </section>

        <!-- Bottom: Quick actions -->
        <section>
          <AdminCommandSectionCard title="Quick Actions" subtitle="Common election officer workflows.">
            <AdminQuickActionGrid :actions="quickActions" @select="navigate" />
          </AdminCommandSectionCard>
        </section>
      </template>
    </div>
  </div>
</template>
