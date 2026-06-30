<script setup>
import { onMounted } from "vue";
import { useRouter } from "vue-router";
import LineChart from "@/components/charts/LineChart.vue";
import DonutChart from "@/components/charts/DonutChart.vue";
import {
  GovernanceKpiCard,
  GovernanceSectionCard,
  InfrastructureStatusList,
} from "@/components/governance";
import { LoadingSkeleton, VAlert, VButton } from "@/components/ui";
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
  if (typeof route === "string") {
    router.push(route);
  } else {
    router.push(route);
  }
}
</script>

<template>
  <div class="space-y-8 bg-[#F8FAFC] pb-8">
    <header class="flex flex-col gap-4 border-b border-[#E5E7EB] bg-white px-page py-6 lg:flex-row lg:items-start lg:justify-between">
      <div class="min-w-0">
        <p class="text-sm font-medium text-[#64748B]">Dashboard</p>
        <h1 class="mt-1 text-2xl font-semibold tracking-tight text-[#1F2937]">Platform Governance Center</h1>
        <p class="mt-2 text-sm text-[#64748B]">{{ platformStatusLabel }}</p>
      </div>
      <div class="flex flex-wrap items-center gap-3">
        <div class="rounded-input border border-[#E5E7EB] bg-[#F8FAFC] px-4 py-2 text-sm text-[#64748B]">
          <span class="block text-xs uppercase tracking-wide">Current time</span>
          <span class="font-medium text-[#1F2937]">{{ currentTimeLabel }}</span>
          <span class="ml-2 hidden sm:inline">· {{ todayLabel }}</span>
        </div>
        <VButton variant="secondary" size="sm" :loading="loading" @click="refresh">Refresh</VButton>
        <span
          v-if="isLive"
          class="inline-flex items-center gap-1.5 rounded-full bg-[#16A34A]/10 px-3 py-1 text-xs font-medium text-[#16A34A]"
        >
          <span class="h-2 w-2 rounded-full bg-[#16A34A]" aria-hidden="true" />
          Live
        </span>
      </div>
    </header>

    <div class="space-y-section px-page">
      <VAlert v-if="error" variant="error">{{ error }}</VAlert>

      <LoadingSkeleton v-if="loading" variant="stats" :rows="10" />

      <template v-else>
        <section aria-label="Key governance indicators" class="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-5">
          <GovernanceKpiCard
            v-for="card in kpiCards"
            :key="card.id"
            :title="card.title"
            :value="card.value"
            :detail="card.detail"
            :hint="card.hint"
            :health-status="card.healthStatus"
            :clickable="card.clickable"
            @click="card.route && navigate(card.route)"
          />
        </section>

        <section class="grid grid-cols-1 gap-6 xl:grid-cols-2">
          <GovernanceSectionCard
            title="Election governance overview"
            subtitle="Lifecycle counts only — no vote totals or election management."
          >
            <div class="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-5">
              <div
                v-for="item in governanceSummary"
                :key="item.label"
                class="rounded-input border border-[#E5E7EB] bg-[#F8FAFC] px-4 py-4 text-center"
              >
                <p class="text-2xl font-semibold tabular-nums text-[#1F2937]">{{ item.value }}</p>
                <p class="mt-1 text-xs leading-snug text-[#64748B]">{{ item.label }}</p>
              </div>
            </div>
          </GovernanceSectionCard>

          <GovernanceSectionCard title="Infrastructure status" subtitle="Core platform services">
            <InfrastructureStatusList :items="infrastructureItems" />
          </GovernanceSectionCard>
        </section>

        <section class="grid grid-cols-1 gap-6 xl:grid-cols-2">
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
              height="260px"
            />
            <p v-else class="py-12 text-center text-sm text-[#64748B]">No activity trend data yet.</p>
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
              height="260px"
            />
            <p v-else class="py-12 text-center text-sm text-[#64748B]">No lifecycle data available.</p>
          </GovernanceSectionCard>
        </section>

        <section class="grid grid-cols-1 gap-6 xl:grid-cols-2">
          <GovernanceSectionCard
            title="Administrative activity"
            subtitle="Platform administration events only"
          >
            <ul v-if="adminActivity.length" class="divide-y divide-[#E5E7EB]">
              <li v-for="item in adminActivity" :key="item.id" class="py-3">
                <p class="text-sm font-medium text-[#1F2937]">{{ item.title }}</p>
                <p v-if="item.meta" class="mt-0.5 text-xs text-[#64748B]">{{ item.meta }}</p>
              </li>
            </ul>
            <p v-else class="py-8 text-center text-sm text-[#64748B]">No recent platform administration events.</p>
          </GovernanceSectionCard>

          <GovernanceSectionCard title="Pending governance actions" subtitle="Actionable items requiring attention">
            <ul v-if="pendingActions.length" class="space-y-3">
              <li v-for="action in pendingActions" :key="action.id">
                <button
                  type="button"
                  class="flex w-full min-h-touch items-center justify-between gap-3 rounded-input border border-[#E5E7EB] px-4 py-3 text-left transition hover:border-[#2563EB]/30 hover:bg-[#2563EB]/5"
                  @click="navigate(action.route)"
                >
                  <span class="text-sm font-medium text-[#1F2937]">{{ action.title }}</span>
                  <span class="text-xs font-medium text-[#2563EB]">Review</span>
                </button>
              </li>
            </ul>
            <p v-else class="py-8 text-center text-sm text-[#64748B]">No pending governance actions.</p>
          </GovernanceSectionCard>
        </section>

        <GovernanceSectionCard title="Quick actions" subtitle="Super Admin platform operations">
          <div class="flex flex-wrap gap-2">
            <VButton
              v-for="action in quickActions"
              :key="action.id"
              variant="secondary"
              size="sm"
              @click="navigate(action.route)"
            >
              {{ action.label }}
            </VButton>
          </div>
        </GovernanceSectionCard>

        <GovernanceSectionCard title="Platform information" subtitle="Runtime and deployment context">
          <dl class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5">
            <div v-for="item in platformInfo" :key="item.label">
              <dt class="text-xs font-semibold uppercase tracking-wide text-[#64748B]">{{ item.label }}</dt>
              <dd class="mt-1 text-sm font-medium text-[#1F2937]">{{ item.value }}</dd>
            </div>
          </dl>
        </GovernanceSectionCard>
      </template>
    </div>
  </div>
</template>
