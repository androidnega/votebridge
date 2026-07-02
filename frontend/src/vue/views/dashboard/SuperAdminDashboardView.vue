<script setup>
import { onMounted } from "vue";
import { useRouter } from "vue-router";
import LineChart from "@/components/charts/LineChart.vue";
import {
  DashboardKpiCard,
  DashboardQuickActions,
  DashboardSectionCard,
  DashboardWelcomeBanner,
} from "@/components/dashboard/experience";
import { EmptyState, LoadingSkeleton, VAlert, VButton } from "@/components/ui";
import { useDashboardRealtime } from "@/composables/useDashboardRealtime";
import { useGovernanceDashboard } from "@/composables/useGovernanceDashboard";

const router = useRouter();
const { isLive } = useDashboardRealtime("super-admin");

const {
  loading,
  error,
  welcomeBanner,
  kpiCards,
  participationLabels,
  participationSeries,
  hasParticipationTrend,
  quickActions,
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
          subtitle="Platform governance — certification and institutional settings."
        >
          <template #actions>
            <VButton variant="secondary" size="sm" :loading="loading" @click="refresh">Refresh</VButton>
          </template>
        </DashboardWelcomeBanner>

        <section aria-label="Platform summary">
          <div class="grid grid-cols-1 gap-6 sm:grid-cols-2 xl:grid-cols-3">
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
            class="xl:col-span-12"
            title="Platform Activity"
            subtitle="Votes processed across active elections."
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
        </section>

        <DashboardSectionCard title="Quick Actions" subtitle="Certification and platform configuration for the demo.">
          <DashboardQuickActions :actions="quickActions" @select="navigate" />
        </DashboardSectionCard>
      </template>
    </div>
  </div>
</template>
