<script setup>
import { computed, onMounted, onUnmounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { LoadingSkeleton, StatCard } from "@/components/dashboard";
import {
  IntegrityReportPanel,
  PositionResultsCard,
  ResultStatusBadge,
} from "@/components/results";
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

const electionUuid = computed(() => route.params.electionUuid);
const result = computed(() => resultsStore.currentResult);
const positions = computed(() => result.value?.standings?.positions || []);
const summary = computed(() => result.value?.standings?.summary || {});

const acknowledgeFraud = ref(false);

const isAutoProcessing = computed(
  () =>
    authStore.isElectionOfficer &&
    result.value?.result_status === "pending_generation" &&
    result.value?.election_status === "closed"
);

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
  if (authStore.isStudent) return result.value?.result_status === "published";
  if (authStore.isSuperAdmin) return result.value?.result_status === "published";
  return Boolean(positions.value.length);
});

const showDetailedIntegrity = computed(() => authStore.isElectionOfficer);

onMounted(() => {
  resultsStore.fetchResult(electionUuid.value).catch(() => {});
});

onUnmounted(() => {
  resultsStore.clearCurrent();
});

async function handleIntegrity() {
  await resultsStore.fetchIntegrity(electionUuid.value, acknowledgeFraud.value);
}

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
  <div class="space-y-8">
    <div class="flex flex-wrap items-start justify-between gap-4">
      <div>
        <VButton variant="ghost" size="sm" class="mb-2" @click="router.push('/dashboard/results')">
          ← Back to results
        </VButton>
        <h2 class="text-2xl font-bold text-slate-900">
          {{ result?.election_title || "Election results" }}
        </h2>
        <div v-if="result" class="mt-2 flex flex-wrap items-center gap-2">
          <ResultStatusBadge :status="result.result_status" />
        </div>
      </div>
      <VButton
        v-if="canReview"
        @click="router.push({ name: 'result-review', params: { electionUuid } })"
      >
        Open certification review
      </VButton>
    </div>

    <VAlert v-if="resultsStore.error" variant="error">{{ resultsStore.error }}</VAlert>
    <LoadingSkeleton v-if="resultsStore.loading && !result" variant="card" />

    <template v-else-if="result">
      <section class="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <StatCard label="Turnout" :value="`${result.turnout_percentage ?? summary.turnout_percentage ?? 0}%`" accent="brand" />
        <StatCard label="Votes cast" :value="result.total_votes_cast ?? summary.total_votes_cast ?? 0" accent="slate" />
        <StatCard
          label="Eligible voters"
          :value="result.eligible_voters ?? summary.eligible_voters ?? 0"
          accent="green"
        />
      </section>

      <VAlert v-if="isAutoProcessing" variant="info" title="Results processing">
        Results are generated automatically when an election closes.
      </VAlert>

      <VAlert v-if="authStore.isSuperAdmin" variant="info">
        Detailed evidence, custody records, and cryptographic seals are only available through an approved Strong Room session.
      </VAlert>

      <section v-if="authStore.isElectionOfficer" class="flex flex-wrap gap-2">
        <VButton
          variant="secondary"
          :loading="resultsStore.actionLoading"
          @click="handleIntegrity"
        >
          Run integrity check
        </VButton>
        <VButton
          v-if="showStandings"
          variant="secondary"
          @click="downloadReport('csv')"
        >
          Download CSV
        </VButton>
      </section>

      <section v-if="authStore.isSuperAdmin && (canPublish || canArchive)" class="flex flex-wrap gap-2">
        <VButton v-if="canPublish" :loading="resultsStore.actionLoading" @click="publishOpen = true">
          Publish results
        </VButton>
        <VButton
          v-if="canArchive"
          variant="secondary"
          :loading="resultsStore.actionLoading"
          @click="archiveOpen = true"
        >
          Archive election
        </VButton>
      </section>

      <IntegrityReportPanel
        v-if="showDetailedIntegrity"
        :report="resultsStore.integrityReport || result.integrity_report"
        :loading="resultsStore.actionLoading"
      />

      <section v-if="showStandings" class="space-y-6">
        <h3 class="text-lg font-semibold text-slate-900">Published results by position</h3>
        <PositionResultsCard
          v-for="position in positions"
          :key="position.position_uuid"
          :position="position"
        />
      </section>

      <VAlert v-else-if="authStore.isStudent" variant="info">
        Results will appear here once they are officially published.
      </VAlert>

      <VAlert v-else-if="authStore.isSuperAdmin" variant="info">
        Official standings are shown after publication. Use certification review for governance summaries.
      </VAlert>
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
