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

const certifyOpen = ref(false);
const publishOpen = ref(false);
const archiveOpen = ref(false);

const electionUuid = computed(() => route.params.electionUuid);
const result = computed(() => resultsStore.currentResult);
const positions = computed(() => result.value?.standings?.positions || []);
const summary = computed(() => result.value?.standings?.summary || {});

const certifyNotes = ref("");
const acknowledgeFraud = ref(false);
const fraudNotes = ref("");

const canGenerate = computed(
  () =>
    authStore.isAdmin &&
    result.value &&
    ["pending_generation", "generated"].includes(result.value.result_status)
);

const canCertify = computed(
  () => authStore.isSuperAdmin && result.value?.result_status === "pending_certification"
);

const canPublish = computed(
  () => authStore.isSuperAdmin && result.value?.result_status === "certified"
);

const canArchive = computed(
  () => authStore.isSuperAdmin && result.value?.result_status === "published"
);

const showStandings = computed(() => {
  if (authStore.isStudent) return result.value?.result_status === "published";
  return Boolean(positions.value.length);
});

onMounted(() => {
  resultsStore.fetchResult(electionUuid.value).catch(() => {});
});

onUnmounted(() => {
  resultsStore.clearCurrent();
});

async function handleGenerate() {
  await resultsStore.generateResults(electionUuid.value);
}

async function handleIntegrity() {
  await resultsStore.fetchIntegrity(electionUuid.value, acknowledgeFraud.value);
}

async function handleCertify() {
  await resultsStore.certify(electionUuid.value, {
    notes: certifyNotes.value,
    acknowledge_fraud: acknowledgeFraud.value,
    fraud_notes: fraudNotes.value,
  });
  certifyOpen.value = false;
  toast.success(toastMessages.results.certified);
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
        <VButton variant="ghost" size="sm" class="mb-2" @click="router.push('/results')">
          ← Back to results
        </VButton>
        <h2 class="text-2xl font-bold text-slate-900">
          {{ result?.election_title || "Election results" }}
        </h2>
        <div v-if="result" class="mt-2 flex flex-wrap items-center gap-2">
          <ResultStatusBadge :status="result.result_status" />
        </div>
      </div>
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

      <section v-if="authStore.isAdmin || authStore.isSuperAdmin" class="flex flex-wrap gap-2">
        <VButton v-if="canGenerate" :loading="resultsStore.actionLoading" @click="handleGenerate">
          Generate results
        </VButton>
        <VButton
          v-if="authStore.isAdmin"
          variant="secondary"
          :loading="resultsStore.actionLoading"
          @click="handleIntegrity"
        >
          Run integrity check
        </VButton>
        <VButton
          v-if="authStore.isAdmin && showStandings"
          variant="secondary"
          @click="downloadReport('csv')"
        >
          Download CSV
        </VButton>
        <VButton v-if="canCertify" :loading="resultsStore.actionLoading" @click="certifyOpen = true">
          Certify results
        </VButton>
        <VButton v-if="canPublish" :loading="resultsStore.actionLoading" @click="publishOpen = true">
          Publish results
        </VButton>
        <VButton
          v-if="canArchive"
          variant="secondary"
          :loading="resultsStore.actionLoading"
          @click="archiveOpen = true"
        >
          Archive
        </VButton>
      </section>

      <IntegrityReportPanel
        v-if="authStore.isAdmin || authStore.isSuperAdmin"
        :report="resultsStore.integrityReport || result.integrity_report"
        :loading="resultsStore.actionLoading"
      />

      <section v-if="canCertify" class="rounded-xl bg-white p-5 shadow-sm ring-1 ring-slate-900/5">
        <h3 class="text-sm font-semibold text-slate-900">Certification notes</h3>
        <textarea
          v-model="certifyNotes"
          class="mt-2 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm"
          rows="2"
          placeholder="Optional certification notes"
        />
        <label class="mt-3 flex items-center gap-2 text-sm text-slate-700">
          <input v-model="acknowledgeFraud" type="checkbox" class="rounded border-slate-300" />
          Acknowledge open fraud cases
        </label>
        <textarea
          v-if="acknowledgeFraud"
          v-model="fraudNotes"
          class="mt-2 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm"
          rows="2"
          placeholder="Fraud acknowledgment notes"
        />
      </section>

      <section v-if="showStandings" class="space-y-6">
        <h3 class="text-lg font-semibold text-slate-900">Results by position</h3>
        <PositionResultsCard
          v-for="position in positions"
          :key="position.position_uuid"
          :position="position"
        />
      </section>

      <VAlert v-else-if="authStore.isStudent" variant="info">
        Results will appear here once they are officially published.
      </VAlert>
    </template>

    <ConfirmDialog
      v-model="certifyOpen"
      title="Certify election results?"
      description="Certification confirms the results are accurate and ready for publication. This action is recorded in the audit trail."
      confirm-label="Certify results"
      icon="results"
      :loading="resultsStore.actionLoading"
      @confirm="handleCertify"
    />
    <ConfirmDialog
      v-model="publishOpen"
      title="Publish results?"
      description="Published results become visible to students and the public. Ensure certification is complete before publishing."
      confirm-label="Publish results"
      icon="results"
      :loading="resultsStore.actionLoading"
      @confirm="handlePublish"
    />
    <ConfirmDialog
      v-model="archiveOpen"
      title="Archive results?"
      description="Archived results remain available for audit but are removed from active publication queues."
      variant="danger"
      confirm-label="Archive results"
      icon="inbox"
      :loading="resultsStore.actionLoading"
      @confirm="handleArchive"
    />
  </div>
</template>
