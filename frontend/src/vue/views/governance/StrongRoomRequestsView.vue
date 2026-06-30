<script setup>
import { onMounted } from "vue";
import { useRouter } from "vue-router";
import { LoadingSkeleton, PageHeader, VAlert, VButton, VCard, VTable } from "@/components/ui";
import { useToast } from "@/composables/useToast";
import { useVaultAccessQueue } from "@/composables/useVaultAccessQueue";
import { useResultsStore } from "@/stores/results";
import { useStrongroomStore } from "@/stores/strongroom";

const router = useRouter();
const resultsStore = useResultsStore();
const strongroomStore = useStrongroomStore();
const toast = useToast();
const { pendingRequests, loading, error, loadPendingRequests } = useVaultAccessQueue();

const columns = [
  { key: "reason_label", label: "Reason" },
  { key: "election_title", label: "Election" },
  { key: "requested_by", label: "Requested by" },
  { key: "requested_at", label: "Date" },
  { key: "actions", label: "Actions" },
];

onMounted(async () => {
  if (!resultsStore.results.length) {
    await resultsStore.fetchResults().catch(() => {});
  }
  await loadPendingRequests(resultsStore.results).catch(() => {});
});

function formatDate(value) {
  if (!value) return "—";
  return new Date(value).toLocaleString();
}

async function review(request, action) {
  await strongroomStore.reviewAccessRequest(request.election_uuid, request.uuid, action);
  toast.success(action === "approve" ? "Access request approved." : "Access request denied.");
  await loadPendingRequests(resultsStore.results).catch(() => {});
}

function openRequest(request) {
  router.push({
    name: "election-vault-access",
    params: { uuid: request.election_uuid },
  });
}
</script>

<template>
  <div class="vb-page">
    <PageHeader
      title="Strong Room access requests"
      subtitle="Governance approval for exceptional vault access only."
      :breadcrumbs="[
        { label: 'Dashboard', to: '/dashboard' },
        { label: 'Strong Room requests' },
      ]"
    />

    <VAlert variant="info">
      The Strong Room is a sealed election vault. Access requires an approved request and multi-custodian authentication.
    </VAlert>

    <VAlert v-if="error || strongroomStore.error" variant="error">
      {{ error || strongroomStore.error }}
    </VAlert>

    <VCard padding="none">
      <LoadingSkeleton v-if="loading" variant="list" :rows="4" />

      <VTable v-else :columns="columns" :rows="pendingRequests" empty-text="No pending Strong Room requests.">
        <template #cell-reason_label="{ row }">
          <span class="font-medium text-ink-primary">{{ row.reason_label || row.reason }}</span>
        </template>
        <template #cell-election_title="{ row }">
          {{ row.election_title }}
        </template>
        <template #cell-requested_by="{ row }">
          {{ row.requested_by }}
        </template>
        <template #cell-requested_at="{ row }">
          {{ formatDate(row.requested_at) }}
        </template>
        <template #cell-actions="{ row }">
          <div class="flex flex-wrap gap-2" @click.stop>
            <template v-if="row.status === 'pending'">
              <VButton size="sm" @click="review(row, 'approve')">Approve</VButton>
              <VButton size="sm" variant="danger" @click="review(row, 'deny')">Reject</VButton>
            </template>
            <VButton
              v-else-if="row.status === 'approved'"
              size="sm"
              variant="secondary"
              @click="openRequest(row)"
            >
              Open terminal
            </VButton>
          </div>
        </template>
      </VTable>
    </VCard>
  </div>
</template>
