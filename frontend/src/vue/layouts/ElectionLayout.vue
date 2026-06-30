<script setup>
import { computed, onMounted, onUnmounted, watch } from "vue";
import { RouterLink, RouterView, useRoute } from "vue-router";
import { ModuleNav, PageHeader } from "@/components/ui";
import { dashboardPath } from "@/config/routes";
import { getElectionWorkspaceNav } from "@/config/electionWorkspaceNav";
import { useAuthStore } from "@/stores/auth";
import { useElectionStore } from "@/stores/election";
import { useVotingStore } from "@/stores/voting";

const route = useRoute();
const authStore = useAuthStore();
const electionStore = useElectionStore();
const votingStore = useVotingStore();

const electionUuid = computed(() => route.params.uuid);

const electionTitle = computed(
  () => electionStore.currentElection?.title || "Election workspace"
);

const liveStatus = computed(
  () => votingStore.electionStatus || electionStore.currentElection?.status
);

const canVote = computed(() => {
  if (!authStore.isStudent) return false;
  return ["open", "paused"].includes(liveStatus.value);
});

const adminTabs = computed(() => {
  if (!authStore.isElectionOfficer) return [];
  return getElectionWorkspaceNav(electionUuid.value, liveStatus.value);
});

const studentTabs = computed(() => {
  if (!authStore.isStudent && !authStore.isCandidate) return [];
  const uuid = electionUuid.value;
  const base = dashboardPath(`elections/${uuid}`);
  return [
    { label: "Overview", to: base, exact: true },
    { label: "Vote", to: `${base}/vote`, disabled: !canVote.value },
    { label: "Confirmation", to: `${base}/confirmation` },
  ];
});

const breadcrumbs = computed(() => {
  const root = authStore.isElectionOfficer
    ? [{ label: "Election workspace", to: dashboardPath("elections") }]
    : [{ label: "Elections", to: dashboardPath("elections") }];
  return [...root, { label: electionTitle.value }];
});

async function loadElection() {
  if (!electionUuid.value) return;
  await electionStore.fetchElection(electionUuid.value).catch(() => {});
}

onMounted(loadElection);
watch(electionUuid, loadElection);

onUnmounted(() => {
  electionStore.clearCurrent();
  votingStore.clearBallot();
});
</script>

<template>
  <div class="min-h-screen bg-surface-muted">
    <header class="border-b border-border bg-surface shadow-sm">
      <div class="mx-auto max-w-content px-4 py-4 sm:px-page">
        <PageHeader :title="electionTitle" :breadcrumbs="breadcrumbs" />

        <ModuleNav
          v-if="adminTabs.length"
          class="mt-4"
          :items="adminTabs"
          aria-label="Election workspace"
        />

        <nav
          v-else-if="studentTabs.length"
          class="mt-4 flex flex-wrap gap-2"
          aria-label="Election sections"
        >
          <RouterLink
            v-for="tab in studentTabs"
            :key="tab.to"
            :to="tab.disabled ? route.path : tab.to"
            class="inline-flex min-h-touch items-center rounded-input px-3 py-2 text-sm font-medium transition duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-600 focus-visible:ring-offset-2"
            :class="
              route.path === tab.to || (tab.exact && route.path === tab.to)
                ? 'bg-brand-600 text-white'
                : tab.disabled
                  ? 'cursor-not-allowed bg-surface-muted text-slate-400'
                  : 'bg-surface text-slate-700 ring-1 ring-border hover:bg-surface-muted'
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
