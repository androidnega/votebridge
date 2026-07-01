<script setup>
import { computed, onMounted, onUnmounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import SvtCodeField from "@/components/voting/SvtCodeField.vue";
import { VButton, VIcon } from "@/components/ui";
import { branding } from "@/config/branding";
import { useVotingStore } from "@/stores/voting";
import { isValidSvtToken, normalizeSvtToken } from "@/utils/svtToken";

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
  () => votingStore.svtAccess?.election_title || votingStore.svtIssued?.election_title || "Election"
);

const maskedPhone = computed(() => votingStore.maskedPhone || "your registered mobile number");

const phoneHint = computed(() => {
  if (!maskedPhone.value || maskedPhone.value === "your registered mobile number") {
    return maskedPhone.value;
  }
  return maskedPhone.value;
});

const isExpired = computed(() => votingStore.svtStatus === "expired");

const canSubmit = computed(
  () => isValidSvtToken(svtInput.value) && !votingStore.validating && pageState.value === "form"
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

function hasValidatedSession() {
  return (
    votingStore.svtStatus === "validated" ||
    votingStore.svtSession?.status === "validated"
  );
}

async function bootstrap() {
  pageState.value = "loading";
  inlineError.value = "";
  try {
    votingStore.restoreSvtSession(electionUuid.value);
    await votingStore.fetchVotingAccess(electionUuid.value);

    if (votingStore.svtAccess?.has_submitted_ballot) {
      router.replace(`/dashboard/elections/${electionUuid.value}/confirmation`);
      return;
    }

    if (hasValidatedSession() && votingStore.tokenCode) {
      router.replace(`/dashboard/elections/${electionUuid.value}/vote`);
      return;
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
    updateResendCountdown();
  } catch {
    pageState.value = "error";
  }
}

async function handleVerify() {
  if (!canSubmit.value) return;
  inlineError.value = "";
  try {
    await votingStore.validateSvt(electionUuid.value, normalizeSvtToken(svtInput.value));
    pageState.value = "success";
    successTimer = window.setTimeout(() => {
      router.push(`/dashboard/elections/${electionUuid.value}/vote`);
    }, 1800);
  } catch {
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
  <div class="vb-svt-booth">
    <article class="vb-svt-booth-card">
      <header class="vb-svt-booth-header">
        <img
          :src="branding.institutionLogoUrl"
          :alt="`${branding.institutionName} logo`"
          class="vb-svt-booth-logo"
        />
        <p class="vb-svt-booth-brand">{{ branding.systemName }}</p>
        <h1 class="vb-svt-booth-title">Secure Voting Verification</h1>
        <p class="vb-svt-booth-subtitle">
          To protect election integrity, enter the Secure Voting Token sent to your registered mobile
          number before accessing your ballot.
        </p>
        <p v-if="pageState !== 'loading'" class="vb-svt-booth-phone">
          <span class="vb-svt-booth-phone-label">Token sent to</span>
          <span class="vb-svt-booth-phone-value">{{ phoneHint }}</span>
        </p>
        <p v-if="electionTitle" class="vb-svt-booth-election">{{ electionTitle }}</p>
      </header>

      <div v-if="pageState === 'loading'" class="vb-svt-booth-loading" aria-live="polite">
        <span class="vb-svt-booth-spinner" aria-hidden="true" />
        <p>Preparing secure verification…</p>
      </div>

      <div
        v-else-if="pageState === 'success'"
        class="vb-svt-booth-success"
        aria-live="polite"
      >
        <div class="vb-svt-booth-shield vb-svt-booth-shield--success" aria-hidden="true">
          <VIcon name="shieldCheck" class="h-10 w-10 text-brand-700" />
        </div>
        <div class="vb-svt-booth-lock vb-svt-booth-lock--open" aria-hidden="true">
          <VIcon name="lockOpen" class="h-5 w-5" />
        </div>
        <h2 class="vb-svt-booth-success-title">Secure Voting Session Created</h2>
        <p class="vb-svt-booth-success-text">Preparing your ballot…</p>
      </div>

      <div v-else-if="pageState === 'expired'" class="vb-svt-booth-expired">
        <div class="vb-svt-booth-shield" aria-hidden="true">
          <VIcon name="shield" class="h-10 w-10 text-slate-400" />
        </div>
        <p class="vb-svt-booth-expired-text">Your Voting Code has expired.</p>
        <p class="vb-svt-booth-expired-hint">Request a new code to continue.</p>
        <VButton
          class="mt-5 w-full min-h-[48px]"
          :loading="votingStore.requestingSvt"
          @click="handleGenerateNew"
        >
          Generate New Voting Code
        </VButton>
        <p v-if="inlineError" class="vb-svt-code-error mt-3 text-center" role="alert">
          {{ inlineError }}
        </p>
      </div>

      <form
        v-else-if="pageState === 'form'"
        class="vb-svt-booth-form"
        @submit.prevent="handleVerify"
      >
        <div class="vb-svt-booth-visual" aria-hidden="true">
          <div class="vb-svt-booth-shield">
            <VIcon name="shield" class="h-10 w-10 text-brand-700/80" />
          </div>
          <div class="vb-svt-booth-lock">
            <VIcon name="lock" class="h-5 w-5" />
          </div>
        </div>

        <SvtCodeField
          v-model="svtInput"
          :disabled="votingStore.validating"
          :error="inlineError"
          @submit="handleVerify"
        />

        <VButton
          type="submit"
          class="mt-5 w-full min-h-[48px]"
          :disabled="!canSubmit"
          :loading="votingStore.validating"
        >
          {{ votingStore.validating ? "Verifying…" : "Verify & Enter Secure Ballot" }}
        </VButton>

        <div class="vb-svt-booth-actions">
          <button
            type="button"
            class="vb-svt-booth-link"
            :disabled="resendSeconds > 0 || votingStore.resendingSvt || votingStore.validating"
            @click="handleResend"
          >
            {{
              votingStore.resendingSvt
                ? "Sending…"
                : resendSeconds > 0
                  ? `Resend Voting Code (${resendSeconds}s)`
                  : "Resend Voting Code"
            }}
          </button>
          <p class="vb-svt-booth-help">
            Need help?
            <a :href="`mailto:${branding.electionOfficeEmail}`" class="vb-svt-booth-help-link">
              Contact Election Office
            </a>
          </p>
        </div>
      </form>

      <div v-else class="vb-svt-booth-expired">
        <p class="vb-svt-booth-expired-text">Verification unavailable.</p>
        <p v-if="votingStore.error || inlineError" class="vb-svt-code-error mt-2 text-center">
          {{ votingStore.error || inlineError }}
        </p>
        <VButton variant="secondary" class="mt-4 w-full" @click="router.push({ name: 'dashboard' })">
          Back to dashboard
        </VButton>
      </div>

      <aside v-if="pageState === 'form' || pageState === 'success'" class="vb-svt-booth-info">
        <h2 class="vb-svt-booth-info-title">Security Information</h2>
        <ul class="vb-svt-booth-info-list">
          <li>Your Voting Code is unique.</li>
          <li>Valid for one voting session.</li>
          <li>Expires after 10 minutes.</li>
          <li>Never share it with anyone.</li>
          <li>Your ballot remains anonymous.</li>
        </ul>
      </aside>
    </article>
  </div>
</template>
