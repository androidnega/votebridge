<script setup>
import { computed, onMounted } from "vue";
import BarChart from "@/components/charts/BarChart.vue";
import PieChart from "@/components/charts/PieChart.vue";
import { analyticsNav } from "@/config/moduleNav";
import { LoadingSkeleton, ModuleNav, PageHeader, VAlert, VCard } from "@/components/ui";
import { useAnalyticsStore } from "@/stores/analytics";

const store = useAnalyticsStore();
const rows = computed(() => store.departments || []);
const labels = computed(() => rows.value.map((r) => r.label));
const values = computed(() => rows.value.map((r) => r.turnout_percent));

onMounted(() => store.fetchDepartments().catch(() => {}));
</script>

<template>
  <div class="vb-page">
    <PageHeader title="Department Analytics" :breadcrumbs="[{ label: 'Analytics', to: '/dashboard/analytics' }, { label: 'Departments' }]" />
    <ModuleNav :items="analyticsNav" />
    <VAlert v-if="store.error" variant="error">{{ store.error }}</VAlert>
    <LoadingSkeleton v-if="!rows.length && store.loading" variant="list" :rows="4" />
    <div v-else class="grid grid-cols-1 gap-4 lg:grid-cols-2">
      <VCard title="Department turnout"><BarChart :labels="labels" :values="values" /></VCard>
      <VCard title="Distribution"><PieChart :items="rows.map((r) => ({ name: r.label, value: r.participated }))" donut /></VCard>
    </div>
  </div>
</template>
