<script setup>
import { computed, onMounted, onUnmounted } from "vue";
import { useRoute } from "vue-router";
import { LiveFraudFeed, StatCard } from "@/components/dashboard";
import { EmptyState, LoadingSkeleton, PageHeader, VAlert } from "@/components/ui";
import { emptyStates } from "@/config/emptyStates";
import { useFraudStore } from "@/stores/fraud";

const route = useRoute();
const fraudStore = useFraudStore();

const isStrongroom = computed(() => route.path.startsWith("/dashboard/strongroom"));
const breadcrumbs = computed(() =>
  isStrongroom.value
    ? [
        { label: "Strong room", to: "/dashboard/strongroom" },
        { label: "Investigations", to: "/dashboard/strongroom/investigations" },
        { label: "Fraud" },
      ]
    : [{ label: "Dashboard", to: "/dashboard" }, { label: "Fraud" }]
);

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
      title="Fraud investigation"
      subtitle="Live fraud cases and integrity signals."
      :breadcrumbs="breadcrumbs"
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
      v-if="fraudStore.casesFeed.length || fraudStore.loading"
      title="Fraud cases"
      :items="fraudStore.casesFeed"
      :loading="fraudStore.loading"
      :status="fraudStore.realtimeStatus"
    />
    <EmptyState
      v-else-if="fraudStore.integrityReport"
      v-bind="emptyStates.fraud"
      class="mt-4"
    />
  </div>
</template>
