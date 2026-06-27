<script setup>
import { onMounted } from "vue";
import { ussdNav } from "@/config/moduleNav";
import { EmptyState, LoadingSkeleton, ModuleNav, PageHeader, VAlert, VButton, VInput, VTable } from "@/components/ui";
import { useUssdStore } from "@/stores/ussd";

const store = useUssdStore();

const columns = [
  { key: "carrier_session_id", label: "Session" },
  { key: "step_after", label: "Step" },
  { key: "outcome", label: "Outcome" },
  { key: "duration_ms", label: "Ms" },
  { key: "created_at", label: "Time" },
];

onMounted(() => {
  store.fetchLogs().catch(() => {});
});
</script>

<template>
  <div class="vb-page">
    <PageHeader
      title="USSD activity logs"
      subtitle="Every USSD callback and step transition is recorded here."
      :breadcrumbs="[
        { label: 'Overview', to: '/' },
        { label: 'USSD', to: '/ussd' },
        { label: 'Activity logs' },
      ]"
    />

    <ModuleNav :items="ussdNav" aria-label="USSD navigation" />

    <form class="flex flex-col gap-3 sm:flex-row sm:items-end" @submit.prevent="store.fetchLogs()">
      <VInput v-model="store.logFilters.search" label="Search" class="flex-1" />
      <VButton type="submit" variant="secondary">Search</VButton>
    </form>

    <div class="flex flex-wrap gap-2">
      <VButton
        size="sm"
        :variant="!store.logFilters.outcome ? 'primary' : 'secondary'"
        @click="store.logFilters.outcome = ''; store.fetchLogs()"
      >
        All
      </VButton>
      <VButton
        size="sm"
        :variant="store.logFilters.outcome === 'success' ? 'primary' : 'secondary'"
        @click="store.logFilters.outcome = 'success'; store.fetchLogs()"
      >
        Success
      </VButton>
      <VButton
        size="sm"
        :variant="store.logFilters.outcome === 'error' ? 'primary' : 'secondary'"
        @click="store.logFilters.outcome = 'error'; store.fetchLogs()"
      >
        Failed
      </VButton>
    </div>

    <VAlert v-if="store.error" variant="error">{{ store.error }}</VAlert>
    <LoadingSkeleton v-if="store.loading && !store.logs.length" variant="list" :rows="8" />

    <VTable v-else-if="store.logs.length" :columns="columns" :rows="store.logs">
      <template #cell-created_at="{ row }">
        {{ new Date(row.created_at).toLocaleString() }}
      </template>
    </VTable>

    <EmptyState
      v-else
      title="No activity logs"
      description="Every USSD callback is logged here."
      icon="ussd"
    />
  </div>
</template>
