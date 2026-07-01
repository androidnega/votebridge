<script setup>
import { onMounted } from "vue";
import { useRouter } from "vue-router";
import LineChart from "@/components/charts/LineChart.vue";
import DonutChart from "@/components/charts/DonutChart.vue";
import {
  GovernanceActionList,
  GovernanceActivityFeed,
  GovernanceKpiCard,
  GovernanceQuickActionGrid,
  GovernanceSectionCard,
  GovernanceStatTile,
  InfrastructureStatusList,
  PlatformInfoGrid,
} from "@/components/governance";
import { EmptyState, LoadingSkeleton, VAlert, VButton, VIcon } from "@/components/ui";
import { useDashboardRealtime } from "@/composables/useDashboardRealtime";
import { useGovernanceDashboard } from "@/composables/useGovernanceDashboard";

const router = useRouter();
const { isLive } = useDashboardRealtime("super-admin");

const {
  loading,
  error,
  todayLabel,
  currentTimeLabel,
  platformStatusLabel,
  kpiCards,
  governanceSummary,
  infrastructureItems,
  participationLabels,
  participationSeries,
  lifecycleItems,
  adminActivity,
  pendingActions,
  platformInfo,
  quickActions,
  chartColors,
  loadDashboard,
} = useGovernanceDashboard();

onMounted(() => {
  loadDashboard().catch(() => {});
});

function refresh() {
  loadDashboard().catch(() => {});
}

function navigate(route) {
  router.push(route);
}
</script>

<template>
  <div class="min-h-full bg-[#F8FAFC] pb-10">
    <!-- Header -->
    <header class="border-b border-[#E5E7EB]">
      <div class="mx-auto flex max-w-[1400px] flex-col gap-5 px-page py-6 lg:flex-row lg:items-center lg:justify-between">
        <div class="min-w-0">
          <p class="text-xs font-semibold uppercase tracking-wider text-[#64748B]">Dashboard</p>
          <h1 class="mt-1 text-2xl font-semibold tracking-tight text-[#1F2937] lg:text-[1.75rem]">
            Platform Governance Center
          </h1>
          <p class="mt-2 inline-flex items-center gap-2 text-sm text-[#64748B]">
            <span class="inline-flex h-2 w-2 rounded-full bg-[#2563EB]" aria-hidden="true" />
            {{ platformStatusLabel }}
          </p>
        </div>

        <div class="flex flex-wrap items-stretch gap-3">
          <div
            class="flex min-h-touch min-w-[11rem] flex-col justify-center rounded-input border border-[#E5E7EB] bg-white px-4 py-2"
          >
            <p class="text-[0.6875rem] font-semibold uppercase tracking-wide text-[#64748B]">Current time</p>
            <p class="mt-0.5 text-sm font-medium text-[#1F2937]">
              {{ currentTimeLabel }}
              <span class="font-normal text-[#64748B]"> · {{ todayLabel }}</span>
            </p>
          </div>
          <VButton variant="secondary" size="sm" class="min-h-touch self-stretch" :loading="loading" @click="refresh">
            Refresh
          </VButton>
          <span
            v-if="isLive"
            class="inline-flex min-h-touch items-center gap-1.5 self-stretch rounded-input border border-[#16A34A]/20 bg-[#16A34A]/10 px-3 text-xs font-semibold text-[#16A34A]"
          >
            <span class="h-2 w-2 animate-pulse rounded-full bg-[#16A34A]" aria-hidden="true" />
            Live
          </span>
        </div>
      </div>
    </header>

    <div class="mx-auto max-w-[1400px] space-y-8 px-page pt-8">
      <VAlert v-if="error" variant="error">{{ error }}</VAlert>

      <LoadingSkeleton v-if="loading" variant="stats" :rows="10" />

      <template v-else>
        <!-- KPI row -->
        <section aria-label="Key governance indicators">
          <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-5">
            <GovernanceKpiCard
              v-for="card in kpiCards"
              :key="card.id"
              :id="card.id"
              :title="card.title"
              :value="card.value"
              :detail="card.detail"
              :hint="card.hint"
              :health-status="card.healthStatus"
              :clickable="card.clickable"
              @click="card.route && navigate(card.route)"
            />
          </div>
        </section>

        <!-- Governance + Infrastructure -->
        <section class="grid grid-cols-1 gap-6 lg:grid-cols-5">
          <GovernanceSectionCard
            class="lg:col-span-3"
            title="Election governance overview"
            subtitle="Lifecycle counts only — no vote totals or election management."
          >
            <div class="grid grid-cols-2 gap-3 sm:grid-cols-3 xl:grid-cols-5">
              <GovernanceStatTile
                v-for="item in governanceSummary"
                :key="item.label"
                :label="item.label"
                :value="item.value"
              />
            </div>
          </GovernanceSectionCard>

          <GovernanceSectionCard
            class="lg:col-span-2"
            title="Infrastructure status"
            subtitle="Core platform services"
          >
            <InfrastructureStatusList :items="infrastructureItems" />
          </GovernanceSectionCard>
        </section>

        <!-- Charts -->
        <section class="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <GovernanceSectionCard
            title="Election activity trend"
            subtitle="Votes processed over the last 24 hours"
          >
            <LineChart
              v-if="participationLabels.length"
              :labels="participationLabels"
              :series="participationSeries"
              :smooth="false"
              :animated="false"
              height="280px"
            />
            <EmptyState
              v-else
              icon="analytics"
              title="No activity trend yet"
              description="Vote processing data will appear here when elections are active."
            />
          </GovernanceSectionCard>

          <GovernanceSectionCard
            title="Election lifecycle distribution"
            subtitle="Current election and results pipeline mix"
          >
            <DonutChart
              v-if="lifecycleItems.length"
              :items="lifecycleItems"
              :colors="chartColors"
              donut
              :animated="false"
              height="280px"
            />
            <EmptyState
              v-else
              icon="elections"
              title="No lifecycle data"
              description="Election status counts will display once elections exist on the platform."
            />
          </GovernanceSectionCard>
        </section>

        <!-- Activity + Actions -->
        <section class="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <GovernanceSectionCard
            title="Administrative activity"
            subtitle="Platform administration events only"
          >
            <GovernanceActivityFeed v-if="adminActivity.length" :items="adminActivity" />
            <EmptyState
              v-else
              icon="inbox"
              title="No recent activity"
              description="Backup, maintenance, and integration events will appear here."
            />
            <div v-if="adminActivity.length" class="mt-4 border-t border-[#E5E7EB] pt-4">
              <button
                type="button"
                class="inline-flex items-center gap-1 text-sm font-medium text-[#2563EB] hover:underline"
                @click="navigate({ name: 'platform-logs' })"
              >
                View full audit log
                <VIcon name="chevronRight" size="sm" />
              </button>
            </div>
          </GovernanceSectionCard>

          <GovernanceSectionCard
            title="Pending governance actions"
            subtitle="Actionable items requiring attention"
          >
            <GovernanceActionList
              v-if="pendingActions.length"
              :actions="pendingActions"
              @select="navigate"
            />
            <EmptyState
              v-else
              icon="help"
              title="All clear"
              description="No pending governance actions right now."
            />
          </GovernanceSectionCard>
        </section>

        <!-- Quick actions + Platform info (two sections per row) -->
        <section class="grid grid-cols-1 items-stretch gap-6 md:grid-cols-2 md:items-stretch">
          <GovernanceSectionCard
            class="flex h-full min-h-0 flex-col"
            title="Quick actions"
            subtitle="Super Admin platform operations"
          >
            <GovernanceQuickActionGrid class="h-full" :actions="quickActions" @select="navigate" />
          </GovernanceSectionCard>

          <GovernanceSectionCard
            class="flex h-full min-h-0 flex-col"
            title="Platform information"
            subtitle="Runtime and deployment context"
          >
            <PlatformInfoGrid :items="platformInfo" />
          </GovernanceSectionCard>
        </section>
      </template>
    </div>
  </div>
</template>
