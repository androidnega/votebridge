<script setup>
import { onMounted } from "vue";
import { ussdNav } from "@/config/moduleNav";
import { EmptyState, LoadingSkeleton, ModuleNav, PageHeader, VAlert, VButton, VInput, VTable } from "@/components/ui";
import { useUssdStore } from "@/stores/ussd";

const store = useUssdStore();

const columns = [
  { key: "session_id", label: "Session" },
  { key: "msisdn", label: "MSISDN" },
  { key: "status", label: "Status" },
  { key: "current_step", label: "Step" },
  { key: "completed_vote", label: "Voted" },
  { key: "started_at", label: "Started" },
];

onMounted(() => {
  store.fetchSessions().catch(() => {});
});

async function search() {
  await store.fetchSessions().catch(() => {});
}

function formatDate(v) {
  return v ? new Date(v).toLocaleString() : "—";
}
</script>

<template>
  <div class="vb-page">
    <PageHeader
      title="Session monitor"
      subtitle="Live and historical USSD voting sessions."
      :breadcrumbs="[
        { label: 'Overview', to: '/' },
        { label: 'USSD', to: '/ussd' },
        { label: 'Sessions' },
      ]"
    />

    <ModuleNav :items="ussdNav" aria-label="USSD navigation" />

    <form class="flex flex-col gap-3 sm:flex-row sm:items-end" @submit.prevent="search">
      <VInput
        v-model="store.sessionFilters.search"
        label="Search"
        placeholder="Session ID, MSISDN…"
        class="flex-1"
      />
      <VButton type="submit" variant="secondary">Search</VButton>
    </form>

    <div class="flex flex-wrap gap-2">
      <VButton
        size="sm"
        :variant="!store.sessionFilters.status ? 'primary' : 'secondary'"
        @click="store.sessionFilters.status = ''; store.fetchSessions()"
      >
        All
      </VButton>
      <VButton
        size="sm"
        :variant="store.sessionFilters.status === 'active' ? 'primary' : 'secondary'"
        @click="store.sessionFilters.status = 'active'; store.fetchSessions()"
      >
        Active
      </VButton>
      <VButton
        size="sm"
        :variant="store.sessionFilters.status === 'completed' ? 'primary' : 'secondary'"
        @click="store.sessionFilters.status = 'completed'; store.fetchSessions()"
      >
        Completed
      </VButton>
      <VButton
        size="sm"
        :variant="store.sessionFilters.status === 'failed' ? 'primary' : 'secondary'"
        @click="store.sessionFilters.status = 'failed'; store.fetchSessions()"
      >
        Failed
      </VButton>
    </div>

    <VAlert v-if="store.error" variant="error">{{ store.error }}</VAlert>
    <LoadingSkeleton v-if="store.loading && !store.sessions.length" variant="list" :rows="6" />

    <VTable v-else-if="store.sessions.length" :columns="columns" :rows="store.sessions">
      <template #cell-completed_vote="{ row }">
        {{ row.completed_vote ? "Yes" : "No" }}
      </template>
      <template #cell-started_at="{ row }">
        {{ formatDate(row.started_at) }}
      </template>
    </VTable>

    <EmptyState
      v-else
      title="No sessions"
      description="USSD sessions appear when students dial the shortcode."
      icon="ussd"
    />
  </div>
</template>
