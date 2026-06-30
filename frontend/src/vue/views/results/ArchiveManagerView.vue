<script setup>
import { onMounted, onUnmounted } from "vue";
import { useRouter } from "vue-router";
import { ResultsQueuePanel } from "@/components/results";
import { resultsNav } from "@/config/moduleNav";
import { ModuleNav, PageHeader, VAlert } from "@/components/ui";
import { useResultsStore } from "@/stores/results";

const router = useRouter();
const resultsStore = useResultsStore();

onMounted(() => {
  resultsStore.fetchQueues().catch(() => {});
});

onUnmounted(() => {
  resultsStore.disconnectRealtime();
});

async function archive(item) {
  await resultsStore.archive(item.election_uuid);
}

function openDetail(item) {
  router.push(`/dashboard/results/${item.election_uuid}`);
}
</script>

<template>
  <div class="vb-page">
    <PageHeader
      title="Archive manager"
      subtitle="Archive published results for long-term retention."
      :breadcrumbs="[
        { label: 'Dashboard', to: '/dashboard' },
        { label: 'Results', to: '/dashboard/results' },
        { label: 'Archive' },
      ]"
    />

    <ModuleNav :items="resultsNav" aria-label="Results navigation" />

    <VAlert v-if="resultsStore.error" variant="error">{{ resultsStore.error }}</VAlert>
    <ResultsQueuePanel
      :items="resultsStore.archiveQueue"
      :loading="resultsStore.loading"
      action-label="Archive"
      :action-loading="resultsStore.actionLoading"
      empty-title="Nothing to archive"
      empty-description="Published results eligible for archival will appear here."
      @action="archive"
      @select="openDetail"
    />
  </div>
</template>
