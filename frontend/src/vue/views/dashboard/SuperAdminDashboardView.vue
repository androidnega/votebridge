<script setup>
import { onMounted } from "vue";
import { useRouter } from "vue-router";
import LineChart from "@/components/charts/LineChart.vue";
import DonutChart from "@/components/charts/DonutChart.vue";
import {
  DashboardActivityTimeline,
  DashboardKpiCard,
  DashboardQuickActions,
  DashboardSectionCard,
  DashboardSecurityPanel,
  DashboardWelcomeBanner,
} from "@/components/dashboard/experience";
import { EmptyState, LoadingSkeleton, VAlert, VButton, VIcon } from "@/components/ui";
import { useDashboardRealtime } from "@/composables/useDashboardRealtime";
import { useGovernanceDashboard } from "@/composables/useGovernanceDashboard";

const router = useRouter();
const { isLive } = useDashboardRealtime("super-admin");

const {
  loading,
  error,
  welcomeBanner,
  kpiCards,
  platformServicesChart,
  participationLabels,
  participationSeries,
  hasParticipationTrend,
  adminActivity,
  securityItems,
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
  <div class="min-h-full bg-surface-muted pb-10">
    <div class="mx-auto max-w-[1440px] space-y-6 px-page pt-6">
      <VAlert v-if="error" variant="error">{{ error }}</VAlert>
      <LoadingSkeleton v-if="loading" variant="stats" :rows="10" />

      <template v-else>
        <DashboardWelcomeBanner
          v-bind="welcomeBanner"
          :is-live="isLive"
          subtitle="Platform governance, security, and operational oversight."
        >
          <template #actions>
            <VButton variant="secondary" size="sm" :loading="loading" @click="refresh">Refresh</VButton>
          </template>
        </DashboardWelcomeBanner>

        <section aria-label="Platform summary">
          <div class="grid grid-cols-1 gap-6 sm:grid-cols-2 xl:grid-cols-4 2xl:grid-cols-8">
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
            title="Platform Activity"
            subtitle="Votes processed across active elections — aggregate operational view."
          >
            <LineChart
              v-if="hasParticipationTrend"
              :labels="participationLabels"
              :series="participationSeries"
              :animated="isLive"
              height="320px"
            />
            <EmptyState
              v-else
              icon="analytics"
              title="No platform activity yet"
              description="Vote processing trends appear when elections are active."
            />
          </DashboardSectionCard>

          <DashboardSectionCard
            class="xl:col-span-4"
            title="Platform Services"
            subtitle="Healthy, warning, and offline service counts."
          >
            <DonutChart
              v-if="platformServicesChart.length"
              :items="platformServicesChart"
              :colors="['#166534', '#D97706', '#DC2626']"
              donut
              height="320px"
            />
            <EmptyState
              v-else
              icon="operations"
              title="Service status unavailable"
              description="Infrastructure health will display once services are checked."
            />
          </DashboardSectionCard>
        </section>

        <section class="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <DashboardSectionCard title="Recent Platform Activity" subtitle="Administrative and governance events.">
            <DashboardActivityTimeline v-if="adminActivity.length" :items="adminActivity" />
            <EmptyState
              v-else
              icon="inbox"
              title="No recent activity"
              description="Backup, maintenance, and integration events will appear here."
            />
            <div v-if="adminActivity.length" class="mt-4 border-t border-border pt-4">
              <button
                type="button"
                class="inline-flex items-center gap-1 text-sm font-medium text-[#2563EB] hover:underline"
                @click="navigate({ name: 'platform-logs' })"
              >
                View full audit log
                <VIcon name="chevronRight" size="sm" />
              </button>
            </div>
          </DashboardSectionCard>

          <DashboardSectionCard title="Recent Security" subtitle="Authentication, fraud, and vault access signals.">
            <DashboardSecurityPanel :items="securityItems" />
          </DashboardSectionCard>
        </section>

        <DashboardSectionCard title="Quick Actions" subtitle="Super Admin platform operations — no election management.">
          <DashboardQuickActions :actions="quickActions" @select="navigate" />
        </DashboardSectionCard>
      </template>
    </div>
  </div>
</template>
