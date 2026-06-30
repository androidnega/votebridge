<script setup>
import { computed, defineAsyncComponent, onMounted, onUnmounted } from "vue";
import { useRouter } from "vue-router";
import { StatCard, ConnectionStatusIndicator } from "@/components/dashboard";
import { analyticsNav, reportsAdvancedNav } from "@/config/moduleNav";
import { LoadingSkeleton, ModuleNav, PageHeader, VAlert, VCard, VButton } from "@/components/ui";
import { useAnalyticsStore } from "@/stores/analytics";
import { useAuthStore } from "@/stores/auth";

const GaugeChart = defineAsyncComponent(() => import("@/components/charts/GaugeChart.vue"));
const LineChart = defineAsyncComponent(() => import("@/components/charts/LineChart.vue"));

const router = useRouter();
const store = useAnalyticsStore();
const authStore = useAuthStore();

const voteLabels = computed(() => store.overview?.trends?.votes_hourly?.map((p) => p.label) || []);
const voteSeries = computed(() => [
  { name: "Votes", data: store.overview?.trends?.votes_hourly?.map((p) => p.value) || [], area: true },
]);

const advancedLinks = computed(() =>
  reportsAdvancedNav.filter((item) => {
    if (authStore.isSuperAdmin) return true;
    return (
      !item.to.includes("security") &&
      !item.to.includes("fraud") &&
      !item.to.includes("ussd")
    );
  })
);

onMounted(() => {
  store.fetchOverview().catch(() => {});
  requestAnimationFrame(() => store.connectRealtime());
});
onUnmounted(() => store.disconnectRealtime());
</script>

<template>
  <div class="vb-page">
    <PageHeader
      title="Reports"
      subtitle="Election participation, turnout, and institutional reporting."
      :breadcrumbs="[{ label: 'Dashboard', to: '/dashboard' }, { label: 'Reports' }]"
    >
      <template #actions>
        <ConnectionStatusIndicator :status="store.realtimeStatus" />
      </template>
    </PageHeader>
    <ModuleNav :items="analyticsNav" />
    <VAlert v-if="store.error" variant="error">{{ store.error }}</VAlert>
    <LoadingSkeleton v-if="store.loading && !store.overview" variant="stats" :rows="4" />

    <template v-else-if="store.overview">
      <section class="grid grid-cols-1 gap-4 xs:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Overall turnout" :value="`${store.overview.overall_turnout_percent}%`" accent="green" />
        <StatCard label="Total votes" :value="store.overview.total_votes" accent="brand" />
        <StatCard label="Active voters" :value="store.overview.total_active_voters" accent="slate" />
        <StatCard label="Completed elections" :value="store.overview.completed_elections" accent="brand" />
      </section>

      <div class="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <VCard title="Participation gauge" class="lg:col-span-1">
          <GaugeChart :value="store.overview.overall_participation_percent" />
        </VCard>
        <VCard title="Vote throughput (24h)" class="lg:col-span-2">
          <LineChart :labels="voteLabels" :series="voteSeries" />
        </VCard>
      </div>

      <VCard title="Explore by dimension">
        <p class="mb-4 text-sm text-slate-600">Drill down into faculty, programme, and department reporting.</p>
        <div class="flex flex-wrap gap-2">
          <VButton
            v-for="link in advancedLinks"
            :key="link.to"
            size="sm"
            variant="secondary"
            @click="router.push(link.to)"
          >
            {{ link.label }}
          </VButton>
        </div>
      </VCard>
    </template>
  </div>
</template>
