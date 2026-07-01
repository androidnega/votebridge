<script setup>
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import BiometricScanner from "@/components/biometrics/BiometricScanner.vue";
import { VAlert, VButton } from "@/components/ui";
import { toastMessages } from "@/config/toastMessages";
import { normalizeAuthRedirect } from "@/config/routes";
import { useToast } from "@/composables/useToast";
import { useBiometricsStore } from "@/stores/biometrics";
import { useAuthStore } from "@/stores/auth";
import { useTrustedDevicesStore } from "@/stores/trustedDevices";

const router = useRouter();
const route = useRoute();
const biometricsStore = useBiometricsStore();
const authStore = useAuthStore();
const trustedStore = useTrustedDevicesStore();
const toast = useToast();

const FRAMES_REQUIRED = 3;

const frames = ref([]);
const submitError = ref("");
const capturing = ref(false);
const submitting = ref(false);

const challenge = computed(() => biometricsStore.pendingAuth?.challenge || biometricsStore.challenge);
const pendingToken = computed(() => biometricsStore.pendingAuth?.pending_auth_token);
const instruction = computed(
  () => challenge.value?.instruction || "Follow the on-screen prompts to verify your identity."
);
const showRiskHint = computed(() => (trustedStore.lastRiskReasons?.length ?? 0) > 0);
const framesCaptured = computed(() => frames.value.length);

async function ensureChallenge() {
  if (!pendingToken.value) return;
  if (challenge.value?.challenge_id) return;
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
  if (capturing.value || submitting.value) return;
  capturing.value = true;
  frames.value.push(frame);
  capturing.value = false;

  if (frames.value.length >= FRAMES_REQUIRED) {
    await submitVerification();
  }
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
    const redirect = normalizeAuthRedirect(
      typeof route.query.redirect === "string" && route.query.redirect.startsWith("/")
        ? route.query.redirect
        : result.redirect_path
    );
    await router.replace(redirect);
  } catch (error) {
    submitError.value = error.message || biometricsStore.error;
    frames.value = [];
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
    <h1 class="vb-biometric-verify__title">Verify your identity</h1>

    <p class="vb-biometric-verify__subtitle">
      Complete the live face check to continue signing in.
    </p>

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
      Extra verification required for this sign-in.
    </p>

    <BiometricScanner
      mode="verify"
      :challenge="challenge"
      :frames-captured="framesCaptured"
      :frames-required="FRAMES_REQUIRED"
      @frame="handleFrame"
    />

    <VButton
      variant="primary"
      block
      size="sm"
      :loading="biometricsStore.actionLoading || submitting"
      :disabled="frames.length < 1 || submitting"
      @click="submitVerification"
    >
      Verify &amp; continue
    </VButton>

    <VButton
      v-if="submitError"
      variant="ghost"
      block
      size="sm"
      :disabled="biometricsStore.actionLoading || submitting"
      @click="tryAgain"
    >
      Try again
    </VButton>
  </div>
</template>

<style scoped>
.vb-biometric-verify {
  @apply flex w-full flex-col gap-3;
}

.vb-biometric-verify__title {
  @apply text-center text-lg font-semibold text-brand;
}

.vb-biometric-verify__subtitle {
  @apply text-center text-xs text-slate-600;
}

.vb-biometric-verify__instruction {
  @apply text-center text-sm font-medium text-slate-700;
}

.vb-biometric-verify__hint {
  @apply text-center text-xs text-slate-500;
}

.vb-biometric-verify__alert {
  @apply text-sm;
}
</style>
