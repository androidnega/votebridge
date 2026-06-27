<script setup>
import { onMounted } from "vue";
import { StatCard } from "@/components/dashboard";
import GaugeChart from "@/components/charts/GaugeChart.vue";
import { analyticsNav } from "@/config/moduleNav";
import { LoadingSkeleton, ModuleNav, PageHeader, VAlert, VCard } from "@/components/ui";
import { useAnalyticsStore } from "@/stores/analytics";

const store = useAnalyticsStore();
onMounted(() => store.fetchUssd().catch(() => {}));
</script>

<template>
  <div class="vb-page">
    <PageHeader title="USSD Analytics" :breadcrumbs="[{ label: 'Analytics', to: '/analytics' }, { label: 'USSD' }]" />
    <ModuleNav :items="analyticsNav" />
    <VAlert v-if="store.error" variant="error">{{ store.error }}</VAlert>
    <LoadingSkeleton v-if="store.loading && !store.ussd" variant="stats" :rows="4" />
    <template v-else-if="store.ussd">
      <section class="grid grid-cols-1 gap-4 xs:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Active sessions" :value="store.ussd.active_sessions ?? 0" accent="brand" />
        <StatCard label="Completed" :value="store.ussd.completed_votes ?? 0" accent="green" />
        <StatCard label="Abandoned" :value="store.ussd.abandoned_sessions ?? 0" accent="amber" />
        <StatCard label="Requests today" :value="store.ussd.requests_today ?? 0" accent="slate" />
      </section>
      <VCard title="Voting completion rate"><GaugeChart :value="store.ussd.voting_completion_rate || 0" /></VCard>
    </template>
  </div>
</template>
