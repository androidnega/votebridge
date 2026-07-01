<script setup>
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import BiometricScanner from "@/components/biometrics/BiometricScanner.vue";
import { useBiometricCapture } from "@/composables/useBiometricCapture";
import {
  isValidVerifyChallenge,
  verifyChallengeInstruction,
} from "@/services/biometricChallengeManager";
import { VAlert, VButton } from "@/components/ui";
import { toastMessages } from "@/config/toastMessages";
import { useToast } from "@/composables/useToast";
import { useBiometricsStore } from "@/stores/biometrics";
import { useAuthStore } from "@/stores/auth";
import { useTrustedDevicesStore } from "@/stores/trustedDevices";
import { navigateAfterLogin } from "@/utils/postLoginNavigation";

const router = useRouter();
const route = useRoute();
const biometricsStore = useBiometricsStore();
const authStore = useAuthStore();
const trustedStore = useTrustedDevicesStore();
const toast = useToast();

const FRAMES_REQUIRED = 3;

const scannerRef = ref(null);
const frames = ref([]);
const submitError = ref("");
const submitting = ref(false);
const autoCaptureStarted = ref(false);

const challenge = computed(() => biometricsStore.pendingAuth?.challenge || biometricsStore.challenge);
const pendingToken = computed(() => biometricsStore.pendingAuth?.pending_auth_token);
const instruction = computed(() => {
  const type = challenge.value?.challenge_type;
  if (type) return verifyChallengeInstruction(type);
  return "Blink once to continue";
});
const showRiskHint = computed(() => (trustedStore.lastRiskReasons?.length ?? 0) > 0);
const framesCaptured = computed(() => frames.value.length);

const { capturing, captureSequence, resetCapture } = useBiometricCapture({
  framesRequired: FRAMES_REQUIRED,
  onFrame: handleFrame,
});

async function ensureChallenge() {
  if (!pendingToken.value) return;
  if (isValidVerifyChallenge(challenge.value)) return;

  const next = await biometricsStore.requestChallenge(pendingToken.value);
  if (next && biometricsStore.pendingAuth) {
    biometricsStore.setPendingAuth({
      ...biometricsStore.pendingAuth,
      challenge: next,
    });
  }
}

onMounted(async () => {
  biometricsStore.loadPendingAuth();
  if (!pendingToken.value) {
    router.replace({ name: "auth-login" });
    return;
  }
  try {
    await ensureChallenge();
  } catch (error) {
    submitError.value = error.message || "Could not load verification challenge.";
  }
});

async function handleFrame(frame) {
  if (submitting.value) return;
  frames.value.push(frame);

  if (frames.value.length >= FRAMES_REQUIRED) {
    await submitVerification();
  }
}

async function onChallengeComplete() {
  if (autoCaptureStarted.value || submitting.value) return;
  autoCaptureStarted.value = true;
  await captureSequence(() => scannerRef.value?.captureFrame?.());
}

async function submitVerification() {
  if (submitting.value || biometricsStore.actionLoading) return;

  if (!pendingToken.value) {
    submitError.value = "Session expired. Please sign in again.";
    return;
  }
  if (!challenge.value?.challenge_id) {
    await tryAgain();
    return;
  }
  if (frames.value.length < 1) return;

  submitting.value = true;
  submitError.value = "";
  try {
    const result = await biometricsStore.verifyLogin({
      pendingAuthToken: pendingToken.value,
      challengeId: challenge.value.challenge_id,
      frames: frames.value,
    });
    await authStore.fetchProfile();
    toast.success(toastMessages.biometric.verified);
    const redirect =
      typeof route.query.redirect === "string" && route.query.redirect.startsWith("/")
        ? route.query.redirect
        : result.redirect_path;
    await navigateAfterLogin(router, redirect);
  } catch (error) {
    submitError.value = error.message || biometricsStore.error;
    frames.value = [];
    autoCaptureStarted.value = false;
    resetCapture();
    await tryAgain();
  } finally {
    submitting.value = false;
  }
}

async function tryAgain() {
  if (!pendingToken.value || submitting.value) return;
  try {
    const next = await biometricsStore.requestChallenge(pendingToken.value);
    if (next && biometricsStore.pendingAuth) {
      biometricsStore.setPendingAuth({
        ...biometricsStore.pendingAuth,
        challenge: next,
      });
    }
  } catch (error) {
    submitError.value = error.message || biometricsStore.error;
  }
}
</script>

<template>
  <div class="vb-biometric-verify">
    <header class="vb-biometric-verify__header">
      <h1 class="vb-biometric-verify__title">Verify your identity</h1>
      <p class="vb-biometric-verify__subtitle">
        Secure face verification required to continue.
      </p>
    </header>

    <p class="vb-biometric-verify__instruction">{{ instruction }}</p>

    <VAlert
      v-if="submitError"
      variant="error"
      dismissible
      class="vb-biometric-verify__alert"
      @dismiss="submitError = ''"
    >
      {{ submitError }}
    </VAlert>

    <p v-else-if="showRiskHint" class="vb-biometric-verify__hint">
      Additional verification is required for this sign-in.
    </p>

    <BiometricScanner
      ref="scannerRef"
      mode="verify"
      auto-capture
      :challenge="challenge"
      :frames-captured="framesCaptured"
      :frames-required="FRAMES_REQUIRED"
      @frame="handleFrame"
      @challenge-complete="onChallengeComplete"
    />

    <VButton
      v-if="submitError"
      variant="ghost"
      block
      :disabled="biometricsStore.actionLoading || submitting || capturing"
      @click="tryAgain"
    >
      Try again
    </VButton>

    <p v-else-if="capturing || submitting" class="vb-biometric-verify__processing">
      {{ submitting ? "Verifying identity…" : "Capturing frames…" }}
    </p>
  </div>
</template>

<style scoped>
.vb-biometric-verify {
  @apply mx-auto flex w-full max-w-sm flex-col gap-3;
}

.vb-biometric-verify__header {
  @apply space-y-0.5 text-center;
}

.vb-biometric-verify__title {
  @apply text-base font-semibold text-brand;
}

.vb-biometric-verify__subtitle {
  @apply text-xs text-slate-600;
}

.vb-biometric-verify__instruction {
  @apply text-center text-xs font-medium text-slate-700;
}

.vb-biometric-verify__hint {
  @apply text-center text-xs text-slate-500;
}

.vb-biometric-verify__alert {
  @apply text-sm;
}

.vb-biometric-verify__processing {
  @apply text-center text-sm font-medium text-brand;
}
</style>
