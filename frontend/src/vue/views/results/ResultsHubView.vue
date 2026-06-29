<script setup>
import { computed, onMounted, onUnmounted } from "vue";
import { useRouter } from "vue-router";
import { ConnectionStatusIndicator } from "@/components/dashboard";
import { ResultStatusBadge } from "@/components/results";
import { resultsNav } from "@/config/moduleNav";
import {
  EmptyState,
  LoadingSkeleton,
  ModuleNav,
  PageHeader,
  VAlert,
  VButton,
  VCard,
} from "@/components/ui";
import { useAuthStore } from "@/stores/auth";
import { emptyStates } from "@/config/emptyStates";
import { useResultsStore } from "@/stores/results";

const router = useRouter();
const authStore = useAuthStore();
const resultsStore = useResultsStore();

const title = computed(() => {
  if (authStore.isSuperAdmin) return "Results command center";
  if (authStore.isAdmin) return "Election results";
  return "Published results";
});

const subtitle = computed(() => {
  if (authStore.isStudent) return "Official results for completed elections.";
  if (authStore.isAdmin) return "Generate, preview, and verify election results.";
  return "Certify, publish, and archive official results.";
});

onMounted(() => {
  resultsStore.fetchResults().catch(() => {});
  if (authStore.isAdmin || authStore.isSuperAdmin) {
    resultsStore.fetchQueues().catch(() => {});
    resultsStore.connectRealtime();
  }
});

onUnmounted(() => {
  resultsStore.disconnectRealtime();
});
</script>

<template>
  <div class="vb-page">
    <PageHeader
      :title="title"
      :subtitle="subtitle"
      :breadcrumbs="[{ label: 'Overview', to: '/' }, { label: 'Results' }]"
    >
      <template v-if="authStore.isAdmin || authStore.isSuperAdmin" #actions>
        <ConnectionStatusIndicator :status="resultsStore.realtimeStatus" />
      </template>
    </PageHeader>

    <ModuleNav v-if="authStore.isSuperAdmin" :items="resultsNav" aria-label="Results navigation" />

    <VAlert v-if="resultsStore.error" variant="error">{{ resultsStore.error }}</VAlert>

    <LoadingSkeleton
      v-if="resultsStore.loading && !resultsStore.results.length"
      variant="list"
      :rows="5"
    />

    <VCard v-else padding="none">
      <EmptyState
        v-if="!resultsStore.results.length"
        v-bind="emptyStates.results"
        class="m-card"
      />
      <ul v-else class="divide-y divide-border">
        <li
          v-for="result in resultsStore.results"
          :key="result.uuid"
          class="flex flex-col gap-3 p-card sm:flex-row sm:items-center sm:justify-between"
        >
          <div>
            <p class="font-medium text-slate-800">{{ result.election_title }}</p>
            <div class="mt-2 flex flex-wrap items-center gap-2">
              <ResultStatusBadge :status="result.result_status" />
              <span class="text-xs text-slate-500">Turnout {{ result.turnout_percentage }}%</span>
            </div>
          </div>
          <VButton
            size="sm"
            variant="secondary"
            @click="router.push(`/results/${result.election_uuid}`)"
          >
            View details
          </VButton>
        </li>
      </ul>
    </VCard>
  </div>
</template>
