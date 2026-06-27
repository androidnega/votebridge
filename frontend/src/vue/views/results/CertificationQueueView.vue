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

function openDetail(item) {
  router.push(`/results/${item.election_uuid}`);
}
</script>

<template>
  <div class="vb-page">
    <PageHeader
      title="Certification queue"
      subtitle="Review generated results before certification."
      :breadcrumbs="[
        { label: 'Overview', to: '/' },
        { label: 'Results', to: '/results' },
        { label: 'Certification' },
      ]"
    >
      <template #actions>
        <ConnectionStatusIndicator :status="resultsStore.realtimeStatus" />
      </template>
    </PageHeader>

    <ModuleNav :items="resultsNav" aria-label="Results navigation" />

    <VAlert v-if="resultsStore.error" variant="error">{{ resultsStore.error }}</VAlert>
    <ResultsQueuePanel
      :items="resultsStore.certificationQueue"
      :loading="resultsStore.loading"
      empty-title="No pending certifications"
      empty-description="Generated results awaiting certification will appear here."
      @select="openDetail"
    />
  </div>
</template>
