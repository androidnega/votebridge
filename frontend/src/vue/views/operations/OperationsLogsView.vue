<script setup>
import { onMounted } from "vue";
import { operationsNav } from "@/config/moduleNav";
import { EmptyState, LoadingSkeleton, ModuleNav, PageHeader, VAlert, VButton, VInput, VTable } from "@/components/ui";
import { useOperationsStore } from "@/stores/operations";

const store = useOperationsStore();

const columns = [
  { key: "timestamp", label: "Time" },
  { key: "event_type", label: "Event" },
  { key: "category", label: "Category" },
  { key: "title", label: "Title" },
  { key: "user_email", label: "User" },
];

onMounted(() => {
  store.fetchLogs().catch(() => {});
});

function search() {
  store.fetchLogs().catch(() => {});
}

function formatRows(rows) {
  return rows.map((row) => ({
    ...row,
    timestamp: row.timestamp ? new Date(row.timestamp).toLocaleString() : "—",
  }));
}
</script>

<template>
  <div class="vb-page">
    <PageHeader
      title="Operations logs"
      subtitle="Enterprise audit log viewer with search and pagination."
      :breadcrumbs="[{ label: 'Overview', to: '/' }, { label: 'Operations', to: '/operations' }, { label: 'Logs' }]"
    >
      <template #actions>
        <VButton variant="secondary" size="sm" disabled title="Export ready — backend endpoint prepared">
          Export
        </VButton>
      </template>
    </PageHeader>

    <ModuleNav :items="operationsNav" />

    <form class="flex flex-col gap-3 sm:flex-row sm:items-end" @submit.prevent="search">
      <VInput v-model="store.logsFilters.search" label="Search logs" class="flex-1" />
      <VButton type="submit" variant="secondary">Search</VButton>
    </form>

    <VAlert v-if="store.error" variant="error">{{ store.error }}</VAlert>
    <LoadingSkeleton v-if="store.loading && !store.logs.items.length" variant="list" :rows="8" />

    <VTable
      v-else-if="store.logs.items.length"
      :columns="columns"
      :rows="formatRows(store.logs.items)"
      empty-text="No log entries."
    />

    <EmptyState v-else title="No logs found" description="Adjust filters or time range." icon="operations" />
  </div>
</template>
