<script setup>
import { computed, onMounted, onUnmounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { LoadingSkeleton } from "@/components/dashboard";
import { PositionResultsCard, PositionWinnerCard, ResultStatusBadge } from "@/components/results";
import { ConfirmDialog, VAlert, VButton } from "@/components/ui";
import { toastMessages } from "@/config/toastMessages";
import { useToast } from "@/composables/useToast";
import { useAuthStore } from "@/stores/auth";
import { useResultsStore } from "@/stores/results";

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const resultsStore = useResultsStore();
const toast = useToast();

const publishOpen = ref(false);
const archiveOpen = ref(false);
const showFullStandings = ref(false);

const electionUuid = computed(() => route.params.electionUuid);
const result = computed(() => resultsStore.currentResult);
const positions = computed(() => result.value?.standings?.positions || []);
const summary = computed(() => result.value?.standings?.summary || {});

const isPublished = computed(() => result.value?.result_status === "published");
const isArchived = computed(() => result.value?.result_status === "archived");
const isComplete = computed(() => isPublished.value || isArchived.value);

const canReview = computed(
  () =>
    authStore.isSuperAdmin &&
    ["pending_certification", "generated"].includes(result.value?.result_status)
);

const canPublish = computed(
  () => authStore.isSuperAdmin && result.value?.result_status === "certified"
);

const canArchive = computed(
  () => authStore.isSuperAdmin && result.value?.result_status === "published"
);

const showStandings = computed(() => {
  if (authStore.isStudent) return isPublished.value;
  if (authStore.isSuperAdmin) return isComplete.value;
  return Boolean(positions.value.length);
});

const winnerPositions = computed(() =>
  positions.value.filter((position) => (position.candidates || []).some((candidate) => candidate.is_winner))
);

const statItems = computed(() => [
  {
    label: "Turnout",
    value: `${Number(result.value?.turnout_percentage ?? summary.value.turnout_percentage ?? 0).toFixed(1)}%`,
  },
  {
    label: "Votes cast",
    value: result.value?.total_votes_cast ?? summary.value.total_votes_cast ?? 0,
  },
  {
    label: "Offices",
    value: winnerPositions.value.length || positions.value.length,
  },
]);

function formatDate(value) {
  if (!value) return null;
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

const publishedLabel = computed(() => formatDate(result.value?.published_at));

onMounted(() => {
  resultsStore.fetchResult(electionUuid.value).catch(() => {});
});

onUnmounted(() => {
  resultsStore.clearCurrent();
});

async function handlePublish() {
  await resultsStore.publish(electionUuid.value);
  publishOpen.value = false;
  toast.success(toastMessages.results.published);
}

async function handleArchive() {
  await resultsStore.archive(electionUuid.value);
  archiveOpen.value = false;
  toast.success(toastMessages.results.archived);
}

async function downloadReport(format) {
  const payload = await resultsStore.fetchReport(electionUuid.value, format);
  if (format === "csv" && payload?.content) {
    const blob = new Blob([payload.content], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = payload.filename || "results.csv";
    link.click();
    URL.revokeObjectURL(url);
  }
}
</script>

<template>
  <div class="mx-auto max-w-6xl space-y-6">
    <div class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
      <div class="min-w-0">
        <VButton variant="ghost" size="sm" class="mb-2 -ml-2" @click="router.push('/dashboard/results')">
          ← Results
        </VButton>
        <h1 class="text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">
          {{ result?.election_title || "Election results" }}
        </h1>
        <div v-if="result" class="mt-2 flex flex-wrap items-center gap-2">
          <ResultStatusBadge :status="result.result_status" />
          <span v-if="publishedLabel" class="text-sm text-slate-500">Published {{ publishedLabel }}</span>
        </div>
      </div>

      <div v-if="result" class="flex flex-wrap gap-2 sm:justify-end">
        <VButton v-if="canReview" size="sm" @click="router.push({ name: 'result-review', params: { electionUuid } })">
          Certification review
        </VButton>
        <VButton
          v-if="authStore.isElectionOfficer && showStandings"
          size="sm"
          variant="secondary"
          :loading="resultsStore.actionLoading"
          @click="downloadReport('csv')"
        >
          Download CSV
        </VButton>
        <VButton v-if="canPublish" size="sm" :loading="resultsStore.actionLoading" @click="publishOpen = true">
          Publish
        </VButton>
        <VButton
          v-if="canArchive"
          size="sm"
          variant="secondary"
          :loading="resultsStore.actionLoading"
          @click="archiveOpen = true"
        >
          Archive
        </VButton>
      </div>
    </div>

    <VAlert v-if="resultsStore.error" variant="error">{{ resultsStore.error }}</VAlert>
    <LoadingSkeleton v-if="resultsStore.loading && !result" variant="card" />

    <template v-else-if="result">
      <section class="grid grid-cols-3 gap-3 rounded-card border border-border bg-surface p-4 shadow-card sm:gap-4 sm:p-5">
        <div v-for="item in statItems" :key="item.label" class="text-center sm:text-left">
          <p class="text-[11px] font-medium uppercase tracking-wide text-slate-500">{{ item.label }}</p>
          <p class="mt-1 text-xl font-semibold tabular-nums text-slate-900 sm:text-2xl">{{ item.value }}</p>
        </div>
      </section>

      <VAlert
        v-if="authStore.isStudent && !isPublished"
        variant="info"
      >
        Results will appear here once they are officially published.
      </VAlert>

      <section v-if="showStandings && winnerPositions.length" class="space-y-4">
        <div>
          <h2 class="text-lg font-semibold text-slate-900">Office holders</h2>
          <p class="mt-1 text-sm text-slate-500">Winning candidates for each position on the ballot.</p>
        </div>

        <div class="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
          <PositionWinnerCard
            v-for="position in winnerPositions"
            :key="position.position_uuid"
            :position="position"
          />
        </div>
      </section>

      <section v-if="showStandings && positions.length" class="rounded-card border border-border bg-slate-50/60">
        <button
          type="button"
          class="flex w-full items-center justify-between gap-3 px-4 py-3 text-left text-sm font-medium text-slate-700 sm:px-5"
          @click="showFullStandings = !showFullStandings"
        >
          <span>Full standings by position</span>
          <span class="text-slate-400">{{ showFullStandings ? "Hide" : "Show" }}</span>
        </button>

        <div v-if="showFullStandings" class="space-y-4 border-t border-border px-4 py-4 sm:px-5">
          <PositionResultsCard
            v-for="position in positions"
            :key="position.position_uuid"
            :position="position"
          />
        </div>
      </section>
    </template>

    <ConfirmDialog
      v-model="publishOpen"
      title="Publish results?"
      description="Published results become visible to students and the public."
      confirm-label="Publish results"
      icon="results"
      :loading="resultsStore.actionLoading"
      @confirm="handlePublish"
    />
    <ConfirmDialog
      v-model="archiveOpen"
      title="Archive results?"
      description="Archived results remain available for audit but leave active publication queues."
      variant="danger"
      confirm-label="Archive results"
      icon="inbox"
      :loading="resultsStore.actionLoading"
      @confirm="handleArchive"
    />
  </div>
</template>
