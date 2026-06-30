<script setup>
import { computed, onMounted } from "vue";
import { useRoute } from "vue-router";
import BiometricStatusCard from "@/components/biometrics/BiometricStatusCard.vue";
import { EmptyState, LoadingSkeleton, PageHeader, VAlert, VTable } from "@/components/ui";
import { useBiometricsStore } from "@/stores/biometrics";

const route = useRoute();
const store = useBiometricsStore();

const isStrongroom = computed(() => route.path.startsWith("/dashboard/strongroom"));
const breadcrumbs = computed(() =>
  isStrongroom.value
    ? [
        { label: "Strong room", to: "/dashboard/strongroom" },
        { label: "Investigations", to: "/dashboard/strongroom/investigations" },
        { label: "Identity investigations" },
      ]
    : [
        { label: "Security", to: "/security" },
        { label: "Biometric history" },
      ]
);

onMounted(async () => {
  await Promise.all([store.fetchStatus(), store.fetchHistory()]);
});

const columns = [
  { key: "created_at", label: "Time" },
  { key: "event_type", label: "Event" },
  { key: "outcome", label: "Outcome" },
  { key: "confidence", label: "Confidence" },
  { key: "challenge_type", label: "Challenge" },
];
</script>

<template>
  <div class="vb-page">
    <PageHeader
      :title="isStrongroom ? 'Identity investigations' : 'Biometric history'"
      :breadcrumbs="breadcrumbs"
    />

    <VAlert v-if="store.error" variant="error">{{ store.error }}</VAlert>
    <LoadingSkeleton v-if="store.loading && !store.history.length" variant="list" :rows="6" />

    <BiometricStatusCard :status="store.status" :loading="store.loading" class="mb-section" />

    <EmptyState
      v-if="!store.loading && !store.history.length"
      title="No verification events"
      description="Biometric audit events will appear here."
    />

    <VTable v-else :columns="columns" :rows="store.history" row-key="uuid">
      <template #cell-created_at="{ row }">
        {{ new Date(row.created_at).toLocaleString() }}
      </template>
      <template #cell-confidence="{ row }">
        {{ row.confidence != null ? row.confidence.toFixed(3) : "—" }}
      </template>
    </VTable>
  </div>
</template>
