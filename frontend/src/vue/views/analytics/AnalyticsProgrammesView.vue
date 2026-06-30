<script setup>
import { computed, onMounted } from "vue";
import BarChart from "@/components/charts/BarChart.vue";
import { analyticsNav } from "@/config/moduleNav";
import { ModuleNav, PageHeader, VCard } from "@/components/ui";
import { useAnalyticsStore } from "@/stores/analytics";

const store = useAnalyticsStore();
const rows = computed(() => store.programmes || []);

onMounted(() => store.fetchProgrammes().catch(() => {}));
</script>

<template>
  <div class="vb-page">
    <PageHeader title="Programme Analytics" :breadcrumbs="[{ label: 'Analytics', to: '/dashboard/analytics' }, { label: 'Programmes' }]" />
    <ModuleNav :items="analyticsNav" />
    <VCard title="Programme turnout">
      <BarChart :labels="rows.map((r) => r.label)" :values="rows.map((r) => r.turnout_percent)" />
    </VCard>
  </div>
</template>
