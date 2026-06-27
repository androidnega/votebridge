<script setup>
import { onMounted } from "vue";
import { useRouter } from "vue-router";
import EmptyState from "@/components/dashboard/EmptyState.vue";
import ElectionStatusBadge from "@/components/voting/ElectionStatusBadge.vue";
import { PageHeader, VAlert, VCard, VTable } from "@/components/ui";
import { useElectionStore } from "@/stores/election";

const router = useRouter();
const electionStore = useElectionStore();

const columns = [
  { key: "title", label: "Title" },
  { key: "status", label: "Status" },
  { key: "election_type_display", label: "Type" },
  { key: "start_date", label: "Starts" },
];

onMounted(() => {
  electionStore.fetchElections().catch(() => {});
});

function openElection(row) {
  if (row.uuid) {
    router.push({ name: "election-detail", params: { uuid: row.uuid } });
  }
}
</script>

<template>
  <div class="vb-page">
    <PageHeader
      title="Elections"
      subtitle="Manage and monitor campus election activity."
    />

    <VAlert v-if="electionStore.error" variant="error" dismissible>
      {{ electionStore.error }}
    </VAlert>

    <VCard padding="none">
      <div class="border-b border-border p-card">
        <h3 class="text-base font-semibold text-slate-800">All elections</h3>
        <p class="mt-1 text-sm text-slate-500">Browse elections by status and type.</p>
      </div>

      <VTable
        :columns="columns"
        :rows="electionStore.elections"
        :loading="electionStore.loading"
        empty-text="No elections found."
        @row-click="openElection"
      >
        <template #cell-status="{ row }">
          <ElectionStatusBadge :status="row.status" />
        </template>
      </VTable>

      <EmptyState
        v-if="!electionStore.loading && !electionStore.elections.length && !electionStore.error"
        title="No elections yet"
        description="Elections will appear here once they are created and published."
        class="p-card"
      />
    </VCard>
  </div>
</template>
