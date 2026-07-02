<script setup>
import { computed, onMounted, onUnmounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import SvtCodeField from "@/components/voting/SvtCodeField.vue";
import VoteValidationSequence from "@/components/voting/VoteValidationSequence.vue";
import { VButton } from "@/components/ui";
import { useVotingStore } from "@/stores/voting";
import { isValidSvtToken, normalizeSvtToken } from "@/utils/svtToken";

const SVT_VALIDATE_STEPS = [
  "Checking voting code…",
  "Verifying secure token…",
  "Opening ballot session…",
];

function isSvtAlreadyActiveError(message = "") {
  return String(message).toLowerCase().includes("already active");
}

const route = useRoute();
const router = useRouter();
const votingStore = useVotingStore();

const electionUuid = computed(() => route.params.uuid);
const svtInput = ref("");
const pageState = ref("loading");
const resendSeconds = ref(0);
const inlineError = ref("");
let resendTimer = null;
let successTimer = null;

const electionTitle = computed(
  () => votingStore.svtAccess?.election_title || votingStore.svtIssued?.election_title || ""
);

const maskedPhone = computed(() => votingStore.maskedPhone || "your phone");

const canSubmit = computed(
  () => isValidSvtToken(svtInput.value) && !votingStore.validating && pageState.value === "form"
);

const showVerifyButton = computed(
  () =>
    pageState.value === "form" &&
    (isValidSvtToken(svtInput.value) || votingStore.validating)
);

function updateResendCountdown() {
  if (!votingStore.resendAvailableAt) {
    resendSeconds.value = 0;
    return;
  }
  resendSeconds.value = Math.max(
    0,
    Math.ceil((new Date(votingStore.resendAvailableAt).getTime() - Date.now()) / 1000)
  );
}

async function bootstrap() {
  pageState.value = "loading";
  inlineError.value = "";
  try {
    votingStore.resetSvtMemory();
    await votingStore.fetchVotingAccess(electionUuid.value);

    if (votingStore.svtAccess?.has_submitted_ballot) {
      router.replace(`/dashboard/elections/${electionUuid.value}/confirmation`);
      return;
    }

    votingStore.restoreSvtSession(electionUuid.value);

    if (votingStore.hasValidatedBallotSession) {
      router.replace(`/dashboard/vote/presence/${electionUuid.value}`);
      return;
    }

    if (votingStore.tokenCode && votingStore.svtStatus === "issued") {
      try {
        await votingStore.validateSvt(electionUuid.value, votingStore.tokenCode);
        router.replace(`/dashboard/vote/presence/${electionUuid.value}`);
        return;
      } catch {
        if (isSvtAlreadyActiveError(votingStore.error)) {
          router.replace(`/dashboard/vote/presence/${electionUuid.value}`);
          return;
        }
        votingStore.clearElectionSvtState(electionUuid.value);
        inlineError.value =
          votingStore.error ||
          "This voting token does not belong to this election. Enter the correct code.";
      }
    }

    if (votingStore.svtStatus === "expired") {
      pageState.value = "expired";
      return;
    }

    if (votingStore.svtStatus !== "issued") {
      if (votingStore.canRequestSvt) {
        await votingStore.requestSvt(electionUuid.value);
      }
    }

    pageState.value = "form";
    if (!inlineError.value && votingStore.error) {
      inlineError.value = votingStore.error;
    }
    updateResendCountdown();
  } catch {
    pageState.value = "error";
  }
}

async function handleVerify() {
  if (!canSubmit.value) return;
  inlineError.value = "";
  pageState.value = "validating";
  try {
    await votingStore.validateSvt(electionUuid.value, normalizeSvtToken(svtInput.value));
    pageState.value = "success";
    successTimer = window.setTimeout(() => {
      router.push(`/dashboard/vote/presence/${electionUuid.value}`);
    }, 1600);
  } catch {
    pageState.value = "form";
    inlineError.value =
      votingStore.error ||
      "Invalid Secure Voting Token. Please check the code sent to your phone.";
  }
}

async function handleResend() {
  if (resendSeconds.value > 0 || votingStore.resendingSvt) return;
  inlineError.value = "";
  try {
    await votingStore.resendSvt(electionUuid.value);
    pageState.value = "form";
    updateResendCountdown();
  } catch {
    inlineError.value = votingStore.error || "Unable to resend your voting code.";
  }
}

async function handleGenerateNew() {
  inlineError.value = "";
  try {
    await votingStore.requestSvt(electionUuid.value);
    pageState.value = "form";
    updateResendCountdown();
  } catch {
    inlineError.value = votingStore.error || "Unable to generate a new voting code.";
  }
}

onMounted(async () => {
  resendTimer = window.setInterval(updateResendCountdown, 1000);
  await bootstrap();
});

onUnmounted(() => {
  if (resendTimer) window.clearInterval(resendTimer);
  if (successTimer) window.clearTimeout(successTimer);
});
</script>

<template>
  <div class="w-full min-w-0 vb-vote-phase">
    <article class="w-full overflow-hidden rounded-card border border-border bg-surface p-5 shadow-card sm:p-6">
      <header
        v-if="pageState !== 'validating' && pageState !== 'success'"
        class="mb-5 border-b border-border pb-4"
      >
        <h1 class="text-lg font-semibold text-ink-primary">Secure Voting Verification</h1>
        <p class="mt-1 text-sm text-ink-secondary">
          Enter the voting code sent to your registered mobile number to open your ballot.
        </p>
        <p v-if="pageState !== 'loading' && electionTitle" class="mt-2 text-sm font-medium text-brand-700">
          {{ electionTitle }}
        </p>
        <p v-if="pageState !== 'loading'" class="mt-1 text-xs text-ink-secondary">
          Sent to <span class="font-mono font-semibold text-ink-primary">{{ maskedPhone }}</span>
        </p>
      </header>

      <Transition name="vb-vote-phase" mode="out-in">
        <div v-if="pageState === 'loading'" key="loading" class="py-4">
          <VoteValidationSequence
            :active="true"
            :steps="['Preparing verification…', 'Loading election access…']"
            hint="Setting up your secure session"
            :interval-ms="900"
          />
        </div>

        <VoteValidationSequence
          v-else-if="pageState === 'validating'"
          key="validating"
          :active="true"
          :steps="SVT_VALIDATE_STEPS"
          hint="Please wait while we verify your code"
        />

        <VoteValidationSequence
          v-else-if="pageState === 'success'"
          key="success"
          :active="false"
          :success="true"
          :steps="SVT_VALIDATE_STEPS"
          success-title="Secure voting session created"
          success-text="Opening presence check…"
        />

        <div v-else-if="pageState === 'expired'" key="expired" class="space-y-4">
          <p class="text-sm text-ink-secondary">
            Your voting code has expired. Request a new code to continue.
          </p>
          <VButton class="w-full min-h-[44px]" :loading="votingStore.requestingSvt" @click="handleGenerateNew">
            Generate new voting code
          </VButton>
          <p v-if="inlineError" class="text-sm text-red-600" role="alert">{{ inlineError }}</p>
        </div>

        <form v-else-if="pageState === 'form'" key="form" class="space-y-4" @submit.prevent="handleVerify">
          <SvtCodeField
            v-model="svtInput"
            :disabled="votingStore.validating"
            :error="inlineError"
            @submit="handleVerify"
          />

          <VButton
            v-if="showVerifyButton"
            type="submit"
            class="w-full min-h-[44px]"
            :disabled="!canSubmit"
          >
            Verify & enter ballot
          </VButton>

          <div class="border-t border-border pt-4">
            <button
              type="button"
              class="text-sm font-medium text-brand-700 hover:text-brand-hover disabled:opacity-50"
              :disabled="resendSeconds > 0 || votingStore.resendingSvt || votingStore.validating"
              @click="handleResend"
            >
              {{
                votingStore.resendingSvt
                  ? "Sending…"
                  : resendSeconds > 0
                    ? `Resend code (${resendSeconds}s)`
                    : "Resend voting code"
              }}
            </button>
          </div>
        </form>

        <div v-else key="error" class="space-y-3">
          <p class="text-sm text-ink-secondary">Verification is unavailable right now.</p>
          <p v-if="votingStore.error || inlineError" class="text-sm text-red-600">
            {{ votingStore.error || inlineError }}
          </p>
          <VButton variant="secondary" class="w-full" @click="router.push({ name: 'dashboard' })">
            Back to dashboard
          </VButton>
        </div>
      </Transition>
    </article>
  </div>
</template>
