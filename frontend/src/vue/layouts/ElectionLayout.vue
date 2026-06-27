<script setup>
import { computed, onMounted, onUnmounted } from "vue";
import { RouterLink, RouterView, useRoute } from "vue-router";
import { PageHeader } from "@/components/ui";
import { useAuthStore } from "@/stores/auth";
import { useElectionStore } from "@/stores/election";
import { useVotingStore } from "@/stores/voting";

const route = useRoute();
const authStore = useAuthStore();
const electionStore = useElectionStore();
const votingStore = useVotingStore();

const electionUuid = computed(() => route.params.uuid);

const electionTitle = computed(
  () => electionStore.currentElection?.title || "Election Workspace"
);

const liveStatus = computed(
  () => votingStore.electionStatus || electionStore.currentElection?.status
);

const canVote = computed(() => {
  if (!authStore.isStudent) return false;
  return ["open", "paused"].includes(liveStatus.value);
});

const tabs = computed(() => {
  const uuid = electionUuid.value;
  if (!uuid) return [];
  return [
    { label: "Overview", to: `/elections/${uuid}`, name: "election-detail" },
    {
      label: "Vote",
      to: `/elections/${uuid}/vote`,
      name: "election-vote",
      disabled: !canVote.value,
    },
    {
      label: "Confirmation",
      to: `/elections/${uuid}/confirmation`,
      name: "election-confirmation",
      disabled: !authStore.isStudent,
    },
  ];
});

function isActiveTab(tab) {
  return route.name === tab.name;
}

onMounted(() => {
  if (electionUuid.value) {
    electionStore.fetchElection(electionUuid.value).catch(() => {});
  }
});

onUnmounted(() => {
  electionStore.clearCurrent();
  votingStore.clearBallot();
});
</script>

<template>
  <div class="min-h-screen bg-surface-muted">
    <header class="border-b border-border bg-white shadow-sm">
      <div class="mx-auto max-w-content px-4 py-4 sm:px-page">
        <PageHeader
          :title="electionTitle"
          :breadcrumbs="[
            { label: 'Elections', to: '/elections' },
            { label: electionTitle },
          ]"
        />

        <nav
          v-if="tabs.length"
          class="mt-4 flex flex-wrap gap-2"
          aria-label="Election sections"
        >
          <RouterLink
            v-for="tab in tabs"
            :key="tab.to"
            :to="tab.disabled ? route.path : tab.to"
            class="inline-flex min-h-touch items-center rounded-input px-3 py-2 text-sm font-medium transition duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-600 focus-visible:ring-offset-2"
            :class="
              isActiveTab(tab)
                ? 'bg-brand-600 text-white'
                : tab.disabled
                  ? 'cursor-not-allowed bg-surface-muted text-slate-400'
                  : 'bg-white text-slate-700 ring-1 ring-border hover:bg-surface-muted'
            "
            :aria-disabled="tab.disabled ? 'true' : undefined"
          >
            {{ tab.label }}
          </RouterLink>
        </nav>
      </div>
    </header>

    <main class="mx-auto max-w-content px-4 py-page sm:px-page">
      <RouterView />
    </main>
  </div>
</template>
