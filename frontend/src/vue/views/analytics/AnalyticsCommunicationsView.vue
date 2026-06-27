<script setup>
import { onMounted } from "vue";
import BarChart from "@/components/charts/BarChart.vue";
import { StatCard } from "@/components/dashboard";
import { analyticsNav } from "@/config/moduleNav";
import { LoadingSkeleton, ModuleNav, PageHeader, VAlert, VCard } from "@/components/ui";
import { useAnalyticsStore } from "@/stores/analytics";

const store = useAnalyticsStore();
onMounted(() => store.fetchCommunications().catch(() => {}));
</script>

<template>
  <div class="vb-page">
    <PageHeader title="Communication Analytics" :breadcrumbs="[{ label: 'Analytics', to: '/analytics' }, { label: 'Communications' }]" />
    <ModuleNav :items="analyticsNav" />
    <VAlert v-if="store.error" variant="error">{{ store.error }}</VAlert>
    <LoadingSkeleton v-if="store.loading && !store.communications" variant="stats" :rows="4" />
    <template v-else-if="store.communications">
      <section class="grid grid-cols-1 gap-4 xs:grid-cols-2 lg:grid-cols-4">
        <StatCard label="SMS delivered" :value="store.communications.sms_delivered" accent="green" />
        <StatCard label="SMS failed" :value="store.communications.sms_failed" accent="red" />
        <StatCard label="Email delivered" :value="store.communications.email_delivered" accent="brand" />
        <StatCard label="Success rate" :value="`${store.communications.delivery_success_rate}%`" accent="green" />
      </section>
      <VCard title="Delivery volumes">
        <BarChart :labels="['SMS', 'Email', 'Failed']" :values="[store.communications.sms_delivered, store.communications.email_delivered, store.communications.sms_failed]" />
      </VCard>
    </template>
  </div>
</template>
