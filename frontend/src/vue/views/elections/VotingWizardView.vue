<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { LoadingSkeleton } from "@/components/dashboard";
import {
  BallotProgressBar,
  BallotReviewStep,
  SvtVerificationPanel,
  VoteCandidatePicker,
  VoteValidationSequence,
} from "@/components/voting";
import { VAlert } from "@/components/ui";
import { useElectionRealtime } from "@/composables/useElectionRealtime";
import { useVotingStore } from "@/stores/voting";

const SUBMIT_STEPS = ["Validating ballot…", "Recording votes…", "Generating receipt…"];

const route = useRoute();
const router = useRouter();
const votingStore = useVotingStore();

const phase = ref("loading");
const svtInput = ref("");
const resendSeconds = ref(0);
let resendTimer = null;

const electionUuid = computed(() => route.params.uuid);

useElectionRealtime(electionUuid);

const electionTitle = computed(() => votingStore.ballot?.election_title || "Election");
const positionCount = computed(() => votingStore.sortedPositions.length);

const activePosition = computed(() => votingStore.currentPosition);

const selectedUuids = computed({
  get() {
    if (!activePosition.value) return [];
    return votingStore.selections[activePosition.value.uuid] || [];
  },
  set(value) {
    if (activePosition.value) {
      votingStore.setSelection(activePosition.value.uuid, value);
      votingStore.persistBallotState(electionUuid.value);
    }
  },
});

function sleep(ms) {
  return new Promise((resolve) => window.setTimeout(resolve, ms));
}

function goToMyElections() {
  router.push({ name: "student-my-elections" });
}

function updateResendCountdown() {
  if (!votingStore.resendAvailableAt) {
    resendSeconds.value = 0;
    return;
  }
  const diff = Math.ceil((new Date(votingStore.resendAvailableAt).getTime() - Date.now()) / 1000);
  resendSeconds.value = Math.max(0, diff);
}

async function ensureSvtIssued() {
  await votingStore.fetchVotingAccess(electionUuid.value);
  if (votingStore.svtAccess?.has_submitted_ballot) {
    router.replace(`/dashboard/elections/${electionUuid.value}/confirmation`);
    return false;
  }
  if (votingStore.ballotSessionActive && votingStore.tokenCode) {
    phase.value = "ballot";
    return true;
  }
  if (votingStore.svtStatus === "issued" || votingStore.svtIssued) {
    phase.value = "svt-verify";
    return true;
  }
  if (votingStore.canRequestSvt) {
    await votingStore.requestSvt(electionUuid.value);
  }
  phase.value = "svt-verify";
  updateResendCountdown();
  return true;
}

async function handleVerifySvt() {
  try {
    await votingStore.validateSvt(electionUuid.value, svtInput.value);
    votingStore.currentStep = 1;
    phase.value = "ballot";
  } catch {
    /* error in store */
  }
}

async function handleResendSvt() {
  if (resendSeconds.value > 0) return;
  try {
    await votingStore.resendSvt(electionUuid.value);
    updateResendCountdown();
  } catch {
    /* error in store */
  }
}

function handleNext() {
  if (votingStore.isReviewStep) return;
  votingStore.nextStep(electionUuid.value);
}

function handleBack() {
  if (votingStore.isReviewStep) {
    votingStore.prevStep(electionUuid.value);
    return;
  }
  if (votingStore.currentStep <= 1) return;
  votingStore.prevStep(electionUuid.value);
}

function handleEditPosition(positionUuid) {
  votingStore.goToPositionStep(positionUuid, electionUuid.value);
}

async function handleSubmitBallot() {
  phase.value = "submitting";
  try {
    await Promise.all([
      sleep(1400),
      votingStore.submitBallot(electionUuid.value),
    ]);
    router.push(`/dashboard/elections/${electionUuid.value}/confirmation`);
  } catch {
    phase.value = "ballot";
  }
}

onMounted(async () => {
  resendTimer = window.setInterval(updateResendCountdown, 1000);
  try {
    await votingStore.fetchBallot(electionUuid.value);
    votingStore.restoreSvtSession(electionUuid.value);
    const ok = await ensureSvtIssued();
    if (!ok) return;
  } catch {
    phase.value = "error";
  }
});

onUnmounted(() => {
  if (resendTimer) window.clearInterval(resendTimer);
  votingStore.disconnectElectionRealtime();
});

watch(
  () => votingStore.selections,
  () => votingStore.persistBallotState(electionUuid.value),
  { deep: true }
);
</script>

<template>
  <div class="w-full">
    <header v-if="phase === 'ballot'" class="mb-4">
      <p class="text-xs font-semibold uppercase tracking-wide text-brand-700">{{ electionTitle }}</p>
      <h1 class="mt-1 text-2xl font-bold text-ink-primary">Official ballot</h1>
    </header>

    <VAlert v-if="votingStore.error && phase !== 'loading'" variant="error" class="mb-6">
      {{ votingStore.error }}
    </VAlert>

    <LoadingSkeleton v-if="phase === 'loading' || votingStore.loading" variant="list" :rows="4" />

    <SvtVerificationPanel
      v-else-if="phase === 'svt-verify'"
      v-model="svtInput"
      :masked-phone="votingStore.maskedPhone"
      :loading="votingStore.validating"
      :resend-loading="votingStore.resendingSvt"
      :resend-seconds="resendSeconds"
      :error="votingStore.error"
      @submit="handleVerifySvt"
      @resend="handleResendSvt"
    />

    <VoteValidationSequence
      v-else-if="phase === 'submitting'"
      :active="true"
      :steps="SUBMIT_STEPS"
    />

    <template v-else-if="phase === 'ballot'">
      <BallotProgressBar
        :current-step="votingStore.currentStep"
        :total-steps="votingStore.totalWizardSteps"
        :position-title="activePosition?.title || (votingStore.isReviewStep ? 'Review' : '')"
        :percent="votingStore.progressPercent"
      />

      <VoteCandidatePicker
        v-if="activePosition && !votingStore.isReviewStep"
        :position="activePosition"
        v-model:selected-uuids="selectedUuids"
        :submitting="false"
        skip-label="Skip position"
        @back="handleBack"
        @confirm="handleNext"
      />

      <BallotReviewStep
        v-else-if="votingStore.isReviewStep"
        :review-items="votingStore.reviewSelections"
        :skipped-count="votingStore.skippedCount"
        :submitting="votingStore.submitting"
        @back="handleBack"
        @edit="handleEditPosition"
        @submit="handleSubmitBallot"
      />
    </template>

    <VAlert v-else variant="error" title="Ballot unavailable">
      This election may not be open for voting, or you may not be eligible.
      <button
        type="button"
        class="mt-3 block text-sm font-medium text-brand-700"
        @click="goToMyElections"
      >
        Back to My Elections
      </button>
    </VAlert>
  </div>
</template>
