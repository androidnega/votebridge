<script setup>
import { computed, onMounted } from "vue";
import BarChart from "@/components/charts/BarChart.vue";
import PieChart from "@/components/charts/PieChart.vue";
import { analyticsNav } from "@/config/moduleNav";
import { LoadingSkeleton, ModuleNav, PageHeader, VAlert, VCard } from "@/components/ui";
import { useAnalyticsStore } from "@/stores/analytics";

const store = useAnalyticsStore();
const byType = computed(() => store.fraud?.cases_by_type || []);

onMounted(() => store.fetchFraud().catch(() => {}));
</script>

<template>
  <div class="vb-page">
    <PageHeader title="Fraud Analytics" :breadcrumbs="[{ label: 'Analytics', to: '/dashboard/analytics' }, { label: 'Fraud' }]" />
    <ModuleNav :items="analyticsNav" />
    <VAlert v-if="store.error" variant="error">{{ store.error }}</VAlert>
    <LoadingSkeleton v-if="store.loading && !store.fraud" variant="list" :rows="4" />
    <div v-else class="grid grid-cols-1 gap-4 lg:grid-cols-2">
      <VCard title="Cases by severity"><PieChart :items="byType.map((t) => ({ name: t.type, value: t.count }))" donut /></VCard>
      <VCard title="Cases by election"><BarChart :labels="(store.fraud?.cases_by_election || []).map((e) => e.election)" :values="(store.fraud?.cases_by_election || []).map((e) => e.count)" horizontal /></VCard>
    </div>
  </div>
</template>
