<script setup>
import { computed, onMounted } from "vue";
import BarChart from "@/components/charts/BarChart.vue";
import HeatmapChart from "@/components/charts/HeatmapChart.vue";
import { analyticsNav } from "@/config/moduleNav";
import { LoadingSkeleton, ModuleNav, PageHeader, VAlert, VCard } from "@/components/ui";
import { useAnalyticsStore } from "@/stores/analytics";

const store = useAnalyticsStore();
const programmeLabels = computed(() => store.participation?.programmes?.map((p) => p.label) || []);
const programmeTurnout = computed(() => store.participation?.programmes?.map((p) => p.turnout_percent) || []);

onMounted(() => store.fetchParticipation().catch(() => {}));
</script>

<template>
  <div class="vb-page">
    <PageHeader title="Participation Analytics" subtitle="Faculty, programme, and turnout breakdowns." :breadcrumbs="[{ label: 'Analytics', to: '/dashboard/analytics' }, { label: 'Participation' }]" />
    <ModuleNav :items="analyticsNav" />
    <VAlert v-if="store.error" variant="error">{{ store.error }}</VAlert>
    <LoadingSkeleton v-if="store.loading && !store.participation" variant="list" :rows="5" />
    <template v-else-if="store.participation">
      <div class="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <VCard title="Programme turnout"><BarChart :labels="programmeLabels" :values="programmeTurnout" /></VCard>
        <VCard title="Participation heatmap"><HeatmapChart :points="store.participation.heatmap || []" /></VCard>
      </div>
    </template>
  </div>
</template>
