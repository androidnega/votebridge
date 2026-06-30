<script setup>
import { computed, onMounted, onUnmounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { LoadingSkeleton } from "@/components/dashboard";
import { ResultStatusBadge } from "@/components/results";
import { ConfirmDialog, VAlert, VButton, VCard } from "@/components/ui";
import { toastMessages } from "@/config/toastMessages";
import { useToast } from "@/composables/useToast";
import { useDashboardStore } from "@/stores/dashboard";
import { useResultsStore } from "@/stores/results";

const route = useRoute();
const router = useRouter();
const resultsStore = useResultsStore();
const dashboardStore = useDashboardStore();
const toast = useToast();

const electionUuid = computed(() => route.params.electionUuid);
const result = computed(() => resultsStore.currentResult);

const committeeNotes = ref("");
const acknowledgeFraud = ref(false);
const fraudNotes = ref("");
const rejectOpen = ref(false);

const integritySummary = computed(() => {
  const report = result.value?.integrity_report || {};
  return {
    status: report.is_valid ? "Valid" : report.is_valid === false ? "Issues detected" : "Not verified",
    blockingCount: report.blocking_issues?.length || 0,
    checksPassed: Object.values(report.checks || {}).filter((check) => check.passed).length,
    checksTotal: Object.keys(report.checks || {}).length,
  };
});

const auditSummary = computed(() => ({
  generatedBy: result.value?.generated_by_name || "Election system",
  generatedAt: result.value?.generated_at
    ? new Date(result.value.generated_at).toLocaleString()
    : "—",
  certificationNotes: result.value?.certification_notes || "None recorded",
}));

const fraudSummary = computed(() => ({
  openCases: dashboardStore.adminOverview?.fraud_cases?.open_cases ?? 0,
  fraudAcknowledged: result.value?.fraud_acknowledged ? "Yes" : "No",
  fraudNotes: result.value?.fraud_acknowledgment_notes || "None recorded",
}));

const canDecide = computed(() =>
  ["pending_certification", "generated"].includes(result.value?.result_status)
);

onMounted(async () => {
  await resultsStore.fetchResult(electionUuid.value).catch(() => {});
  if (!dashboardStore.adminOverview) {
    dashboardStore.fetchSuperAdminDashboard().catch(() => {});
  }
  committeeNotes.value = result.value?.certification_notes || "";
});

onUnmounted(() => {
  resultsStore.clearCurrent();
});

async function handleApprove() {
  await resultsStore.certify(electionUuid.value, {
    notes: committeeNotes.value,
    acknowledge_fraud: acknowledgeFraud.value,
    fraud_notes: fraudNotes.value,
  });
  toast.success(toastMessages.results.certified);
  router.push({ name: "results", query: { filter: "certification" } });
}

function handleReject() {
  rejectOpen.value = true;
}

function confirmReject() {
  rejectOpen.value = false;
  toast.success("Certification declined. Election remains awaiting certification.");
  router.push({ name: "results", query: { filter: "certification" } });
}
</script>

<template>
  <div class="vb-page space-y-section">
    <div>
      <VButton variant="ghost" size="sm" class="mb-2" @click="router.push({ name: 'results' })">
        ← Back to results
      </VButton>
      <h2 class="text-2xl font-semibold text-ink-primary">Election certification review</h2>
      <p class="mt-1 text-sm text-ink-secondary">
        Governance summaries only — detailed evidence requires Strong Room access.
      </p>
    </div>

    <VAlert v-if="resultsStore.error" variant="error">{{ resultsStore.error }}</VAlert>
    <LoadingSkeleton v-if="resultsStore.loading && !result" variant="card" />

    <template v-else-if="result">
      <VCard title="Election summary">
        <dl class="grid gap-4 sm:grid-cols-2">
          <div>
            <dt class="text-xs font-semibold uppercase tracking-wide text-ink-secondary">Election</dt>
            <dd class="mt-1 font-medium text-ink-primary">{{ result.election_title }}</dd>
          </div>
          <div>
            <dt class="text-xs font-semibold uppercase tracking-wide text-ink-secondary">Status</dt>
            <dd class="mt-1"><ResultStatusBadge :status="result.result_status" /></dd>
          </div>
          <div>
            <dt class="text-xs font-semibold uppercase tracking-wide text-ink-secondary">Turnout</dt>
            <dd class="mt-1 text-ink-primary">{{ result.turnout_percentage }}%</dd>
          </div>
          <div>
            <dt class="text-xs font-semibold uppercase tracking-wide text-ink-secondary">Votes cast</dt>
            <dd class="mt-1 text-ink-primary">{{ result.total_votes_cast }}</dd>
          </div>
        </dl>
      </VCard>

      <VCard title="Integrity summary">
        <dl class="grid gap-4 sm:grid-cols-3">
          <div>
            <dt class="text-xs font-semibold uppercase tracking-wide text-ink-secondary">Overall</dt>
            <dd class="mt-1 font-medium text-ink-primary">{{ integritySummary.status }}</dd>
          </div>
          <div>
            <dt class="text-xs font-semibold uppercase tracking-wide text-ink-secondary">Blocking issues</dt>
            <dd class="mt-1 font-medium text-ink-primary">{{ integritySummary.blockingCount }}</dd>
          </div>
          <div>
            <dt class="text-xs font-semibold uppercase tracking-wide text-ink-secondary">Checks passed</dt>
            <dd class="mt-1 font-medium text-ink-primary">
              {{ integritySummary.checksTotal ? `${integritySummary.checksPassed}/${integritySummary.checksTotal}` : "—" }}
            </dd>
          </div>
        </dl>
      </VCard>

      <VCard title="Audit summary">
        <dl class="grid gap-4 sm:grid-cols-2">
          <div>
            <dt class="text-xs font-semibold uppercase tracking-wide text-ink-secondary">Generated by</dt>
            <dd class="mt-1 text-ink-primary">{{ auditSummary.generatedBy }}</dd>
          </div>
          <div>
            <dt class="text-xs font-semibold uppercase tracking-wide text-ink-secondary">Generated at</dt>
            <dd class="mt-1 text-ink-primary">{{ auditSummary.generatedAt }}</dd>
          </div>
        </dl>
      </VCard>

      <VCard title="Fraud review summary">
        <dl class="grid gap-4 sm:grid-cols-2">
          <div>
            <dt class="text-xs font-semibold uppercase tracking-wide text-ink-secondary">Open platform cases</dt>
            <dd class="mt-1 text-ink-primary">{{ fraudSummary.openCases }}</dd>
          </div>
          <div>
            <dt class="text-xs font-semibold uppercase tracking-wide text-ink-secondary">Prior acknowledgment</dt>
            <dd class="mt-1 text-ink-primary">{{ fraudSummary.fraudAcknowledged }}</dd>
          </div>
        </dl>
      </VCard>

      <VCard v-if="canDecide" title="Committee notes">
        <textarea
          v-model="committeeNotes"
          rows="3"
          class="vb-input"
          placeholder="Record governance notes for the certification decision."
        />
        <label class="mt-4 flex items-center gap-2 text-sm text-ink-primary">
          <input v-model="acknowledgeFraud" type="checkbox" class="rounded border-border" />
          Acknowledge open fraud cases
        </label>
        <textarea
          v-if="acknowledgeFraud"
          v-model="fraudNotes"
          rows="2"
          class="vb-input mt-2"
          placeholder="Fraud acknowledgment notes"
        />
      </VCard>

      <VCard v-if="canDecide" title="Certification decision">
        <p class="mb-4 text-sm text-ink-secondary">
          Approve to certify results for publication. Reject to return the election to the certification queue.
        </p>
        <div class="flex flex-wrap gap-2">
          <VButton :loading="resultsStore.actionLoading" @click="handleApprove">Approve</VButton>
          <VButton variant="danger" @click="handleReject">Reject</VButton>
        </div>
      </VCard>

      <VAlert v-else variant="info">
        This election is no longer awaiting certification review.
      </VAlert>
    </template>

    <ConfirmDialog
      v-model="rejectOpen"
      title="Decline certification?"
      description="The election will remain in the certification queue. Document findings in committee notes or initiate a Strong Room access request if detailed evidence is required."
      variant="danger"
      confirm-label="Decline certification"
      @confirm="confirmReject"
    />
  </div>
</template>
