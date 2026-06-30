<script setup>
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import CameraCapture from "@/components/biometrics/CameraCapture.vue";
import ChallengePrompt from "@/components/biometrics/ChallengePrompt.vue";
import RiskNotificationBanner from "@/components/trusted-devices/RiskNotificationBanner.vue";
import { VAlert, VButton, VCard } from "@/components/ui";
import { useBiometricsStore } from "@/stores/biometrics";
import { useAuthStore } from "@/stores/auth";
import { useTrustedDevicesStore } from "@/stores/trustedDevices";
import { useToast } from "@/composables/useToast";
import { normalizeAuthRedirect } from "@/config/routes";

const router = useRouter();
const route = useRoute();
const biometricsStore = useBiometricsStore();
const authStore = useAuthStore();
const trustedStore = useTrustedDevicesStore();
const toast = useToast();

const frames = ref([]);
const submitError = ref("");
const capturing = ref(false);

const challenge = computed(() => biometricsStore.pendingAuth?.challenge || biometricsStore.challenge);
const pendingToken = computed(() => biometricsStore.pendingAuth?.pending_auth_token);

onMounted(() => {
  biometricsStore.loadPendingAuth();
  if (!pendingToken.value) {
    router.replace({ name: "auth-login" });
  }
});

async function handleFrame(frame) {
  if (capturing.value) return;
  capturing.value = true;
  frames.value.push(frame);
  capturing.value = false;

  if (frames.value.length >= 3) {
    await submitVerification();
  }
}

async function submitVerification() {
  submitError.value = "";
  try {
    const result = await biometricsStore.verifyLogin({
      pendingAuthToken: pendingToken.value,
      challengeId: challenge.value?.challenge_id,
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
  }
}

async function refreshChallenge() {
  await biometricsStore.requestChallenge(pendingToken.value);
  if (biometricsStore.challenge && biometricsStore.pendingAuth) {
    biometricsStore.setPendingAuth({
      ...biometricsStore.pendingAuth,
      challenge: biometricsStore.challenge,
    });
  }
}
</script>

<template>
  <div class="mx-auto w-full max-w-md space-y-section">
    <div class="text-center">
      <h1 class="text-2xl font-semibold text-brand">Identity verification</h1>
      <p class="mt-2 text-sm text-slate-600">Complete the face challenge to continue.</p>
    </div>

    <VAlert v-if="submitError" variant="error">{{ submitError }}</VAlert>

    <RiskNotificationBanner
      :reasons="trustedStore.lastRiskReasons"
      :risk-score="biometricsStore.pendingAuth?.risk_score"
    />

    <ChallengePrompt :challenge="challenge" :loading="biometricsStore.actionLoading" />

    <VCard>
      <CameraCapture @frame="handleFrame" />
      <p class="mt-3 text-center text-xs text-slate-500">
        Frames captured: {{ frames.length }} / 3
      </p>
    </VCard>

    <VButton
      variant="primary"
      block
      :loading="biometricsStore.actionLoading"
      :disabled="frames.length < 1"
      @click="submitVerification"
    >
      Verify identity
    </VButton>

    <VButton variant="ghost" block @click="refreshChallenge">New challenge</VButton>
  </div>
</template>
