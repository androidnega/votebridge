<script setup>
import { onMounted, onUnmounted } from "vue";
import { useRouter } from "vue-router";
import { ConnectionStatusIndicator } from "@/components/dashboard";
import { ResultsQueuePanel } from "@/components/results";
import { resultsNav } from "@/config/moduleNav";
import { ModuleNav, PageHeader, VAlert } from "@/components/ui";
import { useResultsStore } from "@/stores/results";

const router = useRouter();
const resultsStore = useResultsStore();

onMounted(() => {
  resultsStore.fetchQueues().catch(() => {});
  resultsStore.connectRealtime();
});

onUnmounted(() => {
  resultsStore.disconnectRealtime();
});

async function publish(item) {
  await resultsStore.publish(item.election_uuid);
}

function openDetail(item) {
  router.push(`/results/${item.election_uuid}`);
}
</script>

<template>
  <div class="vb-page">
    <PageHeader
      title="Publication center"
      subtitle="Publish certified results for students and the public."
      :breadcrumbs="[
        { label: 'Overview', to: '/' },
        { label: 'Results', to: '/results' },
        { label: 'Publication' },
      ]"
    >
      <template #actions>
        <ConnectionStatusIndicator :status="resultsStore.realtimeStatus" />
      </template>
    </PageHeader>

    <ModuleNav :items="resultsNav" aria-label="Results navigation" />

    <VAlert v-if="resultsStore.error" variant="error">{{ resultsStore.error }}</VAlert>
    <ResultsQueuePanel
      :items="resultsStore.publicationQueue"
      :loading="resultsStore.loading"
      action-label="Publish"
      :action-loading="resultsStore.actionLoading"
      empty-title="No certified results"
      empty-description="Certified elections ready for publication will appear here."
      @action="publish"
      @select="openDetail"
    />
  </div>
</template>
