<script setup>
import { onMounted } from "vue";
import BarChart from "@/components/charts/BarChart.vue";
import { StatCard } from "@/components/dashboard";
import { analyticsNav } from "@/config/moduleNav";
import { LoadingSkeleton, ModuleNav, PageHeader, VAlert, VCard } from "@/components/ui";
import { useAnalyticsStore } from "@/stores/analytics";

const store = useAnalyticsStore();
onMounted(() => store.fetchStrongroom().catch(() => {}));
</script>

<template>
  <div class="vb-page">
    <PageHeader title="Strongroom Analytics" :breadcrumbs="[{ label: 'Analytics', to: '/dashboard/analytics' }, { label: 'Strongroom' }]" />
    <ModuleNav :items="analyticsNav" />
    <VAlert v-if="store.error" variant="error">{{ store.error }}</VAlert>
    <LoadingSkeleton v-if="store.loading && !store.strongroom" variant="list" :rows="4" />
    <template v-else-if="store.strongroom">
      <StatCard class="mb-4 max-w-xs" label="Average integrity score" :value="store.strongroom.average_integrity_score ?? '—'" accent="green" />
      <VCard title="Verification trends">
        <BarChart
          :labels="(store.strongroom.verification_trends || []).map((t) => t.label)"
          :values="(store.strongroom.verification_trends || []).map((t) => t.value)"
        />
      </VCard>
    </template>
  </div>
</template>
