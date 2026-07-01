<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { LoadingSkeleton } from "@/components/dashboard";
import {
  BallotProgressBar,
  BallotReviewStep,
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
let redirecting = false;

const electionUuid = computed(() => route.params.uuid);

useElectionRealtime(electionUuid);

const electionTitle = computed(() => votingStore.ballot?.election_title || "Election");
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

function hasActiveBallotSession() {
  return (
    votingStore.ballotSessionActive ||
    votingStore.svtStatus === "validated" ||
    votingStore.svtSession?.status === "validated"
  );
}

async function ensureBallotAuthorized() {
  votingStore.restoreSvtSession(electionUuid.value);
  await votingStore.fetchVotingAccess(electionUuid.value);

  if (votingStore.svtAccess?.has_submitted_ballot) {
    router.replace(`/dashboard/elections/${electionUuid.value}/confirmation`);
    return false;
  }

  if (!hasActiveBallotSession() || !votingStore.tokenCode) {
    router.replace(`/dashboard/vote/verify/${electionUuid.value}`);
    return false;
  }

  return true;
}

function handleNext() {
  if (votingStore.isReviewStep) return;
  votingStore.nextStep(electionUuid.value);
}

function handleSkip() {
  if (!activePosition.value) return;
  votingStore.skipPosition(activePosition.value, electionUuid.value);
  handleNext();
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

function handleContinueLater() {
  votingStore.continueLater(electionUuid.value);
  router.push({ name: "student-my-elections" });
}

async function handleSubmitBallot() {
  phase.value = "submitting";
  try {
    await Promise.all([sleep(1400), votingStore.submitBallot(electionUuid.value)]);
    router.push(`/dashboard/elections/${electionUuid.value}/confirmation`);
  } catch {
    phase.value = "ballot";
  }
}

onMounted(async () => {
  if (redirecting) return;
  try {
    const authorized = await ensureBallotAuthorized();
    if (!authorized) {
      redirecting = true;
      return;
    }
    await votingStore.fetchBallot(electionUuid.value);
    phase.value = "ballot";
  } catch {
    phase.value = "error";
  }
});

onUnmounted(() => {
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
    <header v-if="phase === 'ballot'" class="mb-4 flex flex-wrap items-start justify-between gap-3">
      <div>
        <p class="text-xs font-semibold uppercase tracking-wide text-brand-700">{{ electionTitle }}</p>
        <h1 class="mt-1 text-2xl font-bold text-ink-primary">Official ballot</h1>
        <p class="mt-1 text-xs text-ink-secondary">Choices are saved locally until you submit.</p>
      </div>
      <button
        type="button"
        class="text-sm font-medium text-brand-700 hover:text-brand-800"
        @click="handleContinueLater"
      >
        Continue later
      </button>
    </header>

    <VAlert v-if="votingStore.error && phase !== 'loading'" variant="error" class="mb-6">
      {{ votingStore.error }}
    </VAlert>

    <LoadingSkeleton v-if="phase === 'loading' || votingStore.loading" variant="list" :rows="4" />

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
        :show-back="!votingStore.isFirstBallotStep"
        :is-last-step="votingStore.isLastPositionStep"
        @back="handleBack"
        @confirm="handleNext"
        @skip="handleSkip"
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
