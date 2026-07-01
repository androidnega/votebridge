<script setup>
import { computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import { AdminElectionListCard } from "@/components/admin";
import EmptyState from "@/components/dashboard/EmptyState.vue";
import { PageHeader, SectionHeader, VAlert, VButton, VCard, VTable } from "@/components/ui";
import { emptyStates } from "@/config/emptyStates";
import { useAuthStore } from "@/stores/auth";
import { useElectionStore } from "@/stores/election";

const router = useRouter();
const electionStore = useElectionStore();
const authStore = useAuthStore();

const isOfficer = computed(() => authStore.isElectionOfficer);

const columns = [
  { key: "title", label: "Title" },
  { key: "status", label: "Status" },
  { key: "election_type_display", label: "Type" },
  { key: "start_date", label: "Starts" },
];

const statusCounts = computed(() => {
  const counts = { draft: 0, scheduled: 0, open: 0, closed: 0 };
  for (const row of electionStore.elections) {
    if (counts[row.status] != null) counts[row.status] += 1;
  }
  return counts;
});

onMounted(() => {
  electionStore.fetchElections().catch(() => {});
});

function openElection(row) {
  if (!row.uuid) return;
  if (authStore.isElectionOfficer) {
    router.push(`/dashboard/elections/${row.uuid}`);
    return;
  }
  router.push({ name: "election-detail", params: { uuid: row.uuid } });
}
</script>

<template>
  <div class="vb-page">
    <PageHeader
      :title="isOfficer ? 'Election workspace' : 'Elections'"
      :subtitle="
        isOfficer
          ? 'Create and manage elections from a single workspace.'
          : 'Browse campus elections and cast your vote.'
      "
      :breadcrumbs="[{ label: 'Dashboard', to: '/dashboard' }, { label: isOfficer ? 'Election workspace' : 'Elections' }]"
    >
      <template v-if="isOfficer" #actions>
        <VButton @click="router.push('/dashboard/elections/create')">Create election</VButton>
      </template>
    </PageHeader>

    <VAlert v-if="electionStore.error" variant="error" dismissible>
      {{ electionStore.error }}
    </VAlert>

    <template v-if="isOfficer && !electionStore.loading">
      <section class="grid grid-cols-2 gap-3 sm:grid-cols-4">
        <div class="rounded-card border border-border bg-white px-4 py-3 shadow-card">
          <p class="text-xs font-semibold uppercase tracking-wide text-slate-500">Draft</p>
          <p class="mt-1 text-xl font-semibold text-slate-900">{{ statusCounts.draft }}</p>
        </div>
        <div class="rounded-card border border-border bg-white px-4 py-3 shadow-card">
          <p class="text-xs font-semibold uppercase tracking-wide text-slate-500">Scheduled</p>
          <p class="mt-1 text-xl font-semibold text-slate-900">{{ statusCounts.scheduled }}</p>
        </div>
        <div class="rounded-card border border-border bg-white px-4 py-3 shadow-card">
          <p class="text-xs font-semibold uppercase tracking-wide text-slate-500">Open</p>
          <p class="mt-1 text-xl font-semibold text-slate-900">{{ statusCounts.open }}</p>
        </div>
        <div class="rounded-card border border-border bg-white px-4 py-3 shadow-card">
          <p class="text-xs font-semibold uppercase tracking-wide text-slate-500">Closed</p>
          <p class="mt-1 text-xl font-semibold text-slate-900">{{ statusCounts.closed }}</p>
        </div>
      </section>
    </template>

    <section>
      <SectionHeader
        title="All elections"
        :subtitle="isOfficer ? 'Select an election to open its workspace.' : 'Tap an election to view details.'"
      />

      <LoadingSkeleton v-if="electionStore.loading" variant="card" class="mt-4" />

      <div v-else-if="isOfficer && electionStore.elections.length" class="mt-4 grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
        <AdminElectionListCard
          v-for="election in electionStore.elections"
          :key="election.uuid"
          :election="election"
        />
      </div>

      <VCard v-else-if="!isOfficer" padding="none" class="mt-4">
        <VTable
          v-if="electionStore.loading || electionStore.elections.length"
          :columns="columns"
          :rows="electionStore.elections"
          :loading="electionStore.loading"
          @row-click="openElection"
        />
        <EmptyState
          v-else-if="!electionStore.error"
          v-bind="emptyStates.elections"
          class="p-card"
        />
      </VCard>

      <EmptyState
        v-else-if="!electionStore.loading && !electionStore.elections.length && !electionStore.error"
        v-bind="emptyStates.electionsAdmin"
        class="mt-4"
      >
        <template #action>
          <VButton @click="router.push('/dashboard/elections/create')">Create election</VButton>
        </template>
      </EmptyState>
    </section>
  </div>
</template>
