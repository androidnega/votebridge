<script setup>
import { onMounted } from "vue";
import LineChart from "@/components/charts/LineChart.vue";
import { StatCard } from "@/components/dashboard";
import { analyticsNav } from "@/config/moduleNav";
import { LoadingSkeleton, ModuleNav, PageHeader, VAlert, VCard } from "@/components/ui";
import { useAnalyticsStore } from "@/stores/analytics";

const store = useAnalyticsStore();

onMounted(() => store.fetchOperations().catch(() => {}));
</script>

<template>
  <div class="vb-page">
    <PageHeader title="Operations Analytics" :breadcrumbs="[{ label: 'Analytics', to: '/analytics' }, { label: 'Operations' }]" />
    <ModuleNav :items="analyticsNav" />
    <VAlert v-if="store.error" variant="error">{{ store.error }}</VAlert>
    <LoadingSkeleton v-if="store.loading && !store.operations" variant="stats" :rows="4" />
    <template v-else-if="store.operations">
      <section class="grid grid-cols-1 gap-4 xs:grid-cols-2 lg:grid-cols-4">
        <StatCard label="API response (ms)" :value="store.operations.api_performance?.api_response_time_ms ?? '—'" accent="brand" />
        <StatCard label="Memory %" :value="store.operations.memory_percent ?? '—'" accent="slate" />
        <StatCard label="Storage %" :value="store.operations.storage_percent ?? '—'" accent="amber" />
        <StatCard label="Pending queue" :value="store.operations.queue_performance?.pending_queue ?? 0" accent="red" />
      </section>
      <VCard title="Throughput trend">
        <LineChart
          :labels="(store.operations.cpu_trend || []).map((p) => p.label)"
          :series="[{ name: 'Votes', data: (store.operations.cpu_trend || []).map((p) => p.votes || p.value) }]"
        />
      </VCard>
    </template>
  </div>
</template>
