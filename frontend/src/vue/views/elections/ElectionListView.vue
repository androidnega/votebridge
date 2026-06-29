<script setup>
import { onMounted } from "vue";
import { useRouter } from "vue-router";
import EmptyState from "@/components/dashboard/EmptyState.vue";
import ElectionStatusBadge from "@/components/voting/ElectionStatusBadge.vue";
import { ModuleNav, PageHeader, VAlert, VButton, VCard, VTable } from "@/components/ui";
import { electionManagementNav } from "@/config/moduleNav";
import { useAuthStore } from "@/stores/auth";
import { useElectionStore } from "@/stores/election";

const router = useRouter();
const electionStore = useElectionStore();
const authStore = useAuthStore();

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
    >
      <template v-if="authStore.isAdmin" #actions>
        <VButton @click="router.push('/elections/create')">Create election</VButton>
      </template>
    </PageHeader>

    <ModuleNav v-if="authStore.isAdmin" :items="electionManagementNav" />

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
