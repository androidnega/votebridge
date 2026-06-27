<script setup>
import { ref, watch } from "vue";
import LineChart from "@/components/charts/LineChart.vue";
import { analyticsNav } from "@/config/moduleNav";
import { LoadingSkeleton, ModuleNav, PageHeader, VAlert, VButton, VCard } from "@/components/ui";
import { useAnalyticsStore } from "@/stores/analytics";

const store = useAnalyticsStore();
const period = ref("daily");
const periods = ["daily", "weekly", "monthly", "semester", "academic_year"];

function load() {
  store.fetchHistorical(period.value).catch(() => {});
}

watch(period, load, { immediate: true });
</script>

<template>
  <div class="vb-page">
    <PageHeader title="Historical Trends" :breadcrumbs="[{ label: 'Analytics', to: '/analytics' }, { label: 'Historical' }]" />
    <ModuleNav :items="analyticsNav" />
    <div class="flex flex-wrap gap-2">
      <VButton v-for="p in periods" :key="p" size="sm" :variant="period === p ? 'primary' : 'secondary'" @click="period = p">{{ p }}</VButton>
    </div>
    <VAlert v-if="store.error" variant="error">{{ store.error }}</VAlert>
    <LoadingSkeleton v-if="store.loading && !store.historical" variant="list" :rows="4" />
    <VCard v-else-if="store.historical" title="Vote trends">
      <LineChart
        :labels="(store.historical.vote_trends || []).map((p) => p.label)"
        :series="[{ name: 'Votes', data: (store.historical.vote_trends || []).map((p) => p.value), area: true }]"
      />
    </VCard>
  </div>
</template>
