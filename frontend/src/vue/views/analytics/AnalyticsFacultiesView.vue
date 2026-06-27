<script setup>
import { computed, onMounted } from "vue";
import BarChart from "@/components/charts/BarChart.vue";
import { analyticsNav } from "@/config/moduleNav";
import { LoadingSkeleton, ModuleNav, PageHeader, VAlert, VCard } from "@/components/ui";
import { useAnalyticsStore } from "@/stores/analytics";

const store = useAnalyticsStore();
const rows = computed(() => store.faculties || []);

onMounted(() => store.fetchFaculties().catch(() => {}));
</script>

<template>
  <div class="vb-page">
    <PageHeader title="Faculty Analytics" :breadcrumbs="[{ label: 'Analytics', to: '/analytics' }, { label: 'Faculties' }]" />
    <ModuleNav :items="analyticsNav" />
    <VAlert v-if="store.error" variant="error">{{ store.error }}</VAlert>
    <LoadingSkeleton v-if="!rows.length && store.loading" variant="list" :rows="4" />
    <VCard v-else title="Faculty participation">
      <BarChart :labels="rows.map((r) => r.faculty)" :values="rows.map((r) => r.turnout_percent)" horizontal />
    </VCard>
  </div>
</template>
