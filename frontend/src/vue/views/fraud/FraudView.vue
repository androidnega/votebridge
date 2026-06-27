<script setup>
import { onMounted, onUnmounted } from "vue";
import { LiveFraudFeed, StatCard } from "@/components/dashboard";
import { LoadingSkeleton, PageHeader, VAlert } from "@/components/ui";
import { useFraudStore } from "@/stores/fraud";

const fraudStore = useFraudStore();

onMounted(() => {
  fraudStore.fetchIntegrityReport().catch(() => {});
  fraudStore.fetchFraudFeed().catch(() => {});
  fraudStore.connectRealtime();
});

onUnmounted(() => {
  fraudStore.disconnectRealtime();
});
</script>

<template>
  <div class="vb-page">
    <PageHeader
      title="Fraud Dashboard"
      subtitle="Live fraud investigations and integrity metrics."
      :breadcrumbs="[{ label: 'Overview', to: '/' }, { label: 'Fraud' }]"
    />

    <VAlert v-if="fraudStore.error" variant="error">{{ fraudStore.error }}</VAlert>

    <LoadingSkeleton
      v-if="fraudStore.loading && !fraudStore.integrityReport"
      variant="stats"
      :rows="4"
    />

    <section
      v-else-if="fraudStore.integrityReport"
      class="grid grid-cols-1 gap-4 xs:grid-cols-2 lg:grid-cols-4"
    >
      <StatCard label="Open" :value="fraudStore.integrityReport.open_cases ?? 0" accent="amber" />
      <StatCard label="Resolved" :value="fraudStore.integrityReport.resolved_cases ?? 0" accent="green" />
      <StatCard label="High risk" :value="fraudStore.integrityReport.high_risk_cases ?? 0" accent="red" />
      <StatCard label="Critical" :value="fraudStore.integrityReport.critical_cases ?? 0" accent="red" />
    </section>

    <LiveFraudFeed
      title="Fraud cases"
      :items="fraudStore.casesFeed"
      :loading="fraudStore.loading"
      :status="fraudStore.realtimeStatus"
    />
  </div>
</template>
