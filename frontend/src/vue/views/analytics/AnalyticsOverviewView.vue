<script setup>
import { computed, defineAsyncComponent, onMounted, onUnmounted } from "vue";
import { StatCard, ConnectionStatusIndicator } from "@/components/dashboard";
import { analyticsNav } from "@/config/moduleNav";
import { LoadingSkeleton, ModuleNav, PageHeader, VAlert, VCard } from "@/components/ui";
import { useAnalyticsStore } from "@/stores/analytics";

const GaugeChart = defineAsyncComponent(() => import("@/components/charts/GaugeChart.vue"));
const LineChart = defineAsyncComponent(() => import("@/components/charts/LineChart.vue"));

const store = useAnalyticsStore();

const voteLabels = computed(() => store.overview?.trends?.votes_hourly?.map((p) => p.label) || []);
const voteSeries = computed(() => [
  { name: "Votes", data: store.overview?.trends?.votes_hourly?.map((p) => p.value) || [], area: true },
]);

onMounted(() => {
  store.fetchOverview().catch(() => {});
  // Defer WS until KPIs render — avoids competing with the overview API on first paint.
  requestAnimationFrame(() => store.connectRealtime());
});
onUnmounted(() => store.disconnectRealtime());
</script>

<template>
  <div class="vb-page">
    <PageHeader
      title="Reports"
      subtitle="Election participation, turnout, and institutional reporting."
      :breadcrumbs="[{ label: 'Overview', to: '/' }, { label: 'Reports' }]"
    >
      <template #actions>
        <ConnectionStatusIndicator :status="store.realtimeStatus" />
      </template>
    </PageHeader>
    <ModuleNav :items="analyticsNav" />
    <VAlert v-if="store.error" variant="error">{{ store.error }}</VAlert>
    <LoadingSkeleton v-if="store.loading && !store.overview" variant="stats" :rows="8" />

    <template v-else-if="store.overview">
      <section class="grid grid-cols-1 gap-4 xs:grid-cols-2 lg:grid-cols-4 2xl:grid-cols-5">
        <StatCard label="Overall turnout" :value="`${store.overview.overall_turnout_percent}%`" accent="green" />
        <StatCard label="Total votes" :value="store.overview.total_votes" accent="brand" />
        <StatCard label="Active voters" :value="store.overview.total_active_voters" accent="slate" />
        <StatCard label="Completed elections" :value="store.overview.completed_elections" accent="brand" />
        <StatCard label="Avg turnout" :value="`${store.overview.average_turnout_percent}%`" accent="green" />
        <StatCard label="Fraud cases" :value="store.overview.total_fraud_cases" accent="red" />
        <StatCard label="Security alerts" :value="store.overview.total_security_alerts" accent="amber" />
        <StatCard label="SMS success" :value="`${store.overview.average_sms_delivery_success_percent}%`" accent="green" />
      </section>

      <div class="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <VCard title="Participation gauge" class="lg:col-span-1">
          <GaugeChart :value="store.overview.overall_participation_percent" />
        </VCard>
        <VCard title="Vote throughput (24h)" class="lg:col-span-2">
          <LineChart :labels="voteLabels" :series="voteSeries" />
        </VCard>
      </div>

      <VCard title="System utilization">
        <div class="grid grid-cols-1 gap-4 md:grid-cols-3">
          <GaugeChart title="CPU" :value="store.overview.system_utilization?.cpu_percent || 0" />
          <GaugeChart title="Memory" :value="store.overview.system_utilization?.memory_percent || 0" />
          <GaugeChart title="Disk" :value="store.overview.system_utilization?.disk_percent || 0" />
        </div>
      </VCard>
    </template>
  </div>
</template>
