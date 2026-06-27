<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { LoadingSkeleton } from "@/components/dashboard";
import {
  BallotReview,
  PositionSelector,
  Stepper,
} from "@/components/voting";
import { VAlert, VButton, VInput } from "@/components/ui";
import { useElectionRealtime } from "@/composables/useElectionRealtime";
import { useVotingStore } from "@/stores/voting";

const route = useRoute();
const router = useRouter();
const votingStore = useVotingStore();

const electionUuid = computed(() => route.params.uuid);
const manualToken = ref("");

useElectionRealtime(electionUuid);

const wizardSteps = computed(() => {
  const steps = [{ id: "svt", label: "Verify token" }];
  for (const position of votingStore.sortedPositions) {
    steps.push({ id: position.uuid, label: position.title });
  }
  steps.push({ id: "review", label: "Review" });
  return steps;
});

watch(
  () => votingStore.tokenCode,
  (value) => {
    manualToken.value = value;
  },
  { immediate: true }
);

onMounted(async () => {
  try {
    await votingStore.fetchBallot(electionUuid.value);
  } catch {
    /* error shown in template */
  }
});

onUnmounted(() => {
  votingStore.resetWizard();
});

async function handleRequestSvt() {
  try {
    await votingStore.requestSvt(electionUuid.value);
  } catch {
    /* store error */
  }
}

async function handleValidateSvt() {
  try {
    await votingStore.validateSvt(electionUuid.value, manualToken.value);
  } catch {
    /* store error */
  }
}

function handlePositionUpdate(uuids) {
  const position = votingStore.currentPosition;
  if (position) {
    votingStore.setSelection(position.uuid, uuids);
  }
}

function goToPositionEdit(positionUuid) {
  const index = votingStore.sortedPositions.findIndex((p) => p.uuid === positionUuid);
  if (index >= 0) {
    votingStore.goToStep(index + 1);
  }
}

async function handleSubmit() {
  try {
    await votingStore.submitBallot(electionUuid.value);
    router.push(`/elections/${electionUuid.value}/confirmation`);
  } catch {
    /* store error */
  }
}
</script>

<template>
  <div class="mx-auto max-w-3xl space-y-8">
    <header>
      <h2 class="text-2xl font-bold text-slate-900">Voting wizard</h2>
      <p class="mt-1 text-sm text-slate-500">
        {{ votingStore.ballot?.election_title || "Complete each step to cast your ballot." }}
      </p>
    </header>

    <VAlert v-if="votingStore.error" variant="error">{{ votingStore.error }}</VAlert>

    <LoadingSkeleton v-if="votingStore.loading" variant="list" :rows="5" />

    <template v-else-if="votingStore.ballot">
      <Stepper
        :steps="wizardSteps"
        :current-step="votingStore.currentStep"
        @go-to="votingStore.goToStep($event)"
      />

      <section
        v-if="votingStore.isSvtStep"
        class="rounded-xl bg-white p-6 shadow-sm ring-1 ring-slate-900/5"
        aria-labelledby="svt-heading"
      >
        <h3 id="svt-heading" class="text-lg font-semibold text-slate-900">
          Step 1 — Secure Voting Token
        </h3>
        <p class="mt-2 text-sm text-slate-600">
          Request a one-time token or paste an existing token to unlock your ballot.
        </p>

        <div class="mt-6 flex flex-col gap-4 sm:flex-row sm:items-end">
          <VButton :loading="votingStore.requestingSvt" variant="secondary" @click="handleRequestSvt">
            Request new token
          </VButton>
        </div>

        <VAlert
          v-if="votingStore.svtIssued?.token_code"
          class="mt-4"
          variant="warning"
          title="Save your token"
        >
          This code is shown once. Store it securely before continuing.
        </VAlert>

        <form class="mt-6 space-y-4" @submit.prevent="handleValidateSvt">
          <VInput
            v-model="manualToken"
            label="SVT token"
            placeholder="Enter your secure voting token"
            autocomplete="off"
            required
          />
          <VButton type="submit" :loading="votingStore.validating">
            Validate &amp; continue
          </VButton>
        </form>

        <VAlert
          v-if="votingStore.svtSession?.status === 'validated'"
          class="mt-4"
          variant="success"
          title="Token validated"
        >
          Your ballot session is active. Continue to select candidates.
        </VAlert>
      </section>

      <section v-else-if="votingStore.currentPosition" aria-labelledby="position-heading">
        <h3 id="position-heading" class="sr-only">
          Select candidates for {{ votingStore.currentPosition.title }}
        </h3>
        <PositionSelector
          :position="votingStore.currentPosition"
          :selected-uuids="votingStore.selections[votingStore.currentPosition.uuid] || []"
          @update:selected-uuids="handlePositionUpdate"
        />
      </section>

      <BallotReview
        v-else-if="votingStore.isReviewStep"
        :items="votingStore.reviewSelections"
        :election-title="votingStore.ballot.election_title"
        @edit="goToPositionEdit"
      />

      <nav class="flex flex-col-reverse gap-3 sm:flex-row sm:justify-between">
        <VButton
          variant="secondary"
          :disabled="votingStore.currentStep === 0"
          @click="votingStore.prevStep()"
        >
          Back
        </VButton>

        <VButton
          v-if="!votingStore.isReviewStep"
          :disabled="!votingStore.canProceed"
          @click="votingStore.nextStep()"
        >
          Continue
        </VButton>

        <VButton
          v-else
          :loading="votingStore.submitting"
          :disabled="!votingStore.allPositionsComplete"
          @click="handleSubmit"
        >
          Submit ballot
        </VButton>
      </nav>
    </template>

    <VAlert v-else variant="error" title="Ballot unavailable">
      This election may not be open for voting, or you may not be eligible.
    </VAlert>
  </div>
</template>
