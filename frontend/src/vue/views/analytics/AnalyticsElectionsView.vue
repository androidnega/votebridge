<script setup>
import { computed, onMounted } from "vue";
import BarChart from "@/components/charts/BarChart.vue";
import LineChart from "@/components/charts/LineChart.vue";
import { analyticsNav } from "@/config/moduleNav";
import { LoadingSkeleton, ModuleNav, PageHeader, VAlert, VCard, VTable } from "@/components/ui";
import { useAnalyticsStore } from "@/stores/analytics";

const store = useAnalyticsStore();
const trendLabels = computed(() => store.elections?.trend?.map((p) => p.label) || []);
const trendValues = computed(() => store.elections?.trend?.map((p) => p.value) || []);
const columns = [
  { key: "title", label: "Election" },
  { key: "status", label: "Status" },
  { key: "turnout_percent", label: "Turnout %" },
  { key: "eligible_voters", label: "Eligible" },
];

onMounted(() => store.fetchElections().catch(() => {}));
</script>

<template>
  <div class="vb-page">
    <PageHeader title="Election Analytics" subtitle="Turnout, channels, and election comparisons." :breadcrumbs="[{ label: 'Analytics', to: '/analytics' }, { label: 'Elections' }]" />
    <ModuleNav :items="analyticsNav" />
    <VAlert v-if="store.error" variant="error">{{ store.error }}</VAlert>
    <LoadingSkeleton v-if="store.loading && !store.elections" variant="list" :rows="6" />
    <template v-else-if="store.elections">
      <VCard title="30-day vote trend"><LineChart :labels="trendLabels" :series="[{ name: 'Votes', data: trendValues, area: true }]" /></VCard>
      <div class="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <VCard title="Most active elections">
          <BarChart :labels="store.elections.most_active?.map((e) => e.title)" :values="store.elections.most_active?.map((e) => e.turnout_percent)" horizontal />
        </VCard>
        <VCard title="Election comparison">
          <VTable :columns="columns" :rows="store.elections.comparison || []" empty-text="No elections." />
        </VCard>
      </div>
    </template>
  </div>
</template>
