<script setup>
import { onMounted, onUnmounted } from "vue";
import { LiveSecurityFeed, StatCard } from "@/components/dashboard";
import { LoadingSkeleton, PageHeader, VAlert } from "@/components/ui";
import { useSecurityStore } from "@/stores/security";

const securityStore = useSecurityStore();

onMounted(() => {
  securityStore.fetchSummary().catch(() => {});
  securityStore.fetchSecurityFeed().catch(() => {});
  securityStore.connectRealtime();
});

onUnmounted(() => {
  securityStore.disconnectRealtime();
});
</script>

<template>
  <div class="vb-page">
    <PageHeader
      title="Security Center"
      subtitle="Live security alerts and monitoring activity."
      :breadcrumbs="[{ label: 'Overview', to: '/' }, { label: 'Security' }]"
    />

    <VAlert v-if="securityStore.error" variant="error">{{ securityStore.error }}</VAlert>

    <LoadingSkeleton
      v-if="securityStore.loading && !securityStore.summary"
      variant="stats"
      :rows="3"
    />

    <section
      v-else-if="securityStore.summary?.alerts"
      class="grid grid-cols-1 gap-4 xs:grid-cols-2 lg:grid-cols-3"
    >
      <StatCard label="Open alerts" :value="securityStore.summary.alerts.open ?? 0" accent="amber" />
      <StatCard label="Reviewing" :value="securityStore.summary.alerts.reviewing ?? 0" accent="brand" />
      <StatCard label="Resolved" :value="securityStore.summary.alerts.resolved ?? 0" accent="green" />
    </section>

    <LiveSecurityFeed
      title="Security alerts"
      :items="securityStore.alertsFeed"
      :loading="securityStore.loading"
      :status="securityStore.realtimeStatus"
    />
  </div>
</template>
