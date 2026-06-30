<script setup>
import { computed, onMounted } from "vue";
import MetricBars from "@/components/operations/MetricBars.vue";
import OpsHealthBadge from "@/components/operations/OpsHealthBadge.vue";
import { StatCard } from "@/components/dashboard";
import { operationsNav } from "@/config/moduleNav";
import { LoadingSkeleton, ModuleNav, PageHeader, VAlert } from "@/components/ui";
import { useOperationsStore } from "@/stores/operations";

const store = useOperationsStore();

const trendBars = computed(() => {
  const points = store.performance?.trends?.vote_throughput_hourly || [];
  const max = Math.max(...points.map((p) => p.votes), 1);
  return points.map((p) => ({
    label: p.label,
    value: p.votes,
    percent: (p.votes / max) * 100,
  }));
});

onMounted(() => {
  store.fetchPerformance().catch(() => {});
});
</script>

<template>
  <div class="vb-page">
    <PageHeader
      title="Performance"
      subtitle="Platform throughput and resource metrics."
      :breadcrumbs="[{ label: 'Dashboard', to: '/dashboard' }, { label: 'Operations', to: '/dashboard/operations' }, { label: 'Performance' }]"
    />
    <ModuleNav :items="operationsNav" />
    <VAlert v-if="store.error" variant="error">{{ store.error }}</VAlert>
    <LoadingSkeleton v-if="store.loading && !store.performance" variant="stats" :rows="4" />

    <template v-else-if="store.performance">
      <section class="grid grid-cols-1 gap-4 xs:grid-cols-2 lg:grid-cols-4">
        <StatCard label="API response (ms)" :value="store.performance.api_response_time_ms ?? '—'" accent="brand" />
        <StatCard label="Auth requests (24h)" :value="store.performance.authentication_requests_24h ?? 0" accent="slate" />
        <StatCard label="Vote throughput (24h)" :value="store.performance.vote_throughput_24h ?? 0" accent="green" />
        <StatCard label="USSD requests" :value="store.performance.ussd_requests_24h ?? 0" accent="brand" />
        <StatCard label="SMS throughput" :value="store.performance.sms_throughput_24h ?? 0" accent="green" />
        <StatCard label="Email throughput" :value="store.performance.email_throughput_24h ?? 0" accent="brand" />
      </section>

      <div class="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <div class="rounded-card border border-border bg-white p-card shadow-card">
          <MetricBars title="Vote throughput (hourly)" :items="trendBars" />
        </div>
        <div class="rounded-card border border-border bg-white p-card shadow-card">
          <h4 class="mb-4 text-sm font-semibold text-slate-800">Resource usage</h4>
          <div class="space-y-3">
            <div class="flex items-center justify-between text-sm">
              <span>CPU</span>
              <OpsHealthBadge :status="(store.performance.cpu_usage_percent ?? 0) > 80 ? 'warning' : 'healthy'" />
              <span>{{ store.performance.cpu_usage_percent ?? '—' }}%</span>
            </div>
            <div class="flex items-center justify-between text-sm">
              <span>Memory</span>
              <span>{{ store.performance.memory_usage_percent ?? '—' }}%</span>
            </div>
            <div class="flex items-center justify-between text-sm">
              <span>Disk</span>
              <span>{{ store.performance.disk_usage_percent ?? '—' }}%</span>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
