<script setup>
import { computed, onMounted } from "vue";
import LineChart from "@/components/charts/LineChart.vue";
import { StatCard } from "@/components/dashboard";
import { analyticsNav } from "@/config/moduleNav";
import { LoadingSkeleton, ModuleNav, PageHeader, VAlert, VCard } from "@/components/ui";
import { useAnalyticsStore } from "@/stores/analytics";

const store = useAnalyticsStore();
const alerts = computed(() => store.security?.alerts_over_time || []);

onMounted(() => store.fetchSecurity().catch(() => {}));
</script>

<template>
  <div class="vb-page">
    <PageHeader title="Security Analytics" :breadcrumbs="[{ label: 'Analytics', to: '/analytics' }, { label: 'Security' }]" />
    <ModuleNav :items="analyticsNav" />
    <VAlert v-if="store.error" variant="error">{{ store.error }}</VAlert>
    <LoadingSkeleton v-if="store.loading && !store.security" variant="stats" :rows="4" />
    <template v-else-if="store.security">
      <section class="grid grid-cols-1 gap-4 xs:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Failed logins (7d)" :value="store.security.failed_logins_7d" accent="red" />
        <StatCard label="Successful logins" :value="store.security.successful_logins_7d" accent="green" />
        <StatCard label="OTP requests" :value="store.security.otp_requests_7d" accent="brand" />
        <StatCard label="Open alerts" :value="store.security.security_alerts?.open ?? 0" accent="amber" />
      </section>
      <VCard title="Security alerts over time">
        <LineChart :labels="alerts.map((p) => p.label)" :series="[{ name: 'Alerts', data: alerts.map((p) => p.value) }]" />
      </VCard>
    </template>
  </div>
</template>
