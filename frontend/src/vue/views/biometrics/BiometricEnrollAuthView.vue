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

const router = useRouter();
const route = useRoute();
const biometricsStore = useBiometricsStore();
const authStore = useAuthStore();
const toast = useToast();

const FRAMES_REQUIRED = 5;

const frames = ref([]);
const submitError = ref("");
const capturing = ref(false);
const submitting = ref(false);

const pendingToken = computed(() => biometricsStore.pendingAuth?.pending_auth_token);
const framesCaptured = computed(() => frames.value.length);

onMounted(() => {
  biometricsStore.loadPendingAuth();
  if (!pendingToken.value || !biometricsStore.pendingAuth?.requires_enrollment) {
    router.replace({ name: "auth-login" });
  }
});

async function handleFrame(frame) {
  if (capturing.value || submitting.value) return;
  capturing.value = true;
  frames.value.push(frame);
  capturing.value = false;

  if (frames.value.length >= FRAMES_REQUIRED) {
    await completeEnrollment();
  }
}

async function completeEnrollment() {
  if (submitting.value || biometricsStore.actionLoading) return;
  if (!pendingToken.value) {
    submitError.value = "Session expired. Please sign in again.";
    return;
  }
  if (frames.value.length < FRAMES_REQUIRED) return;

  submitting.value = true;
  submitError.value = "";
  try {
    const result = await biometricsStore.enrollLogin({
      pendingAuthToken: pendingToken.value,
      frames: frames.value,
    });
    await authStore.fetchProfile();
    toast.success(toastMessages.biometric.enrolled);
    const redirect = normalizeAuthRedirect(
      typeof route.query.redirect === "string" && route.query.redirect.startsWith("/")
        ? route.query.redirect
        : result.redirect_path
    );
    await router.replace(redirect);
  } catch (error) {
    submitError.value = error.message || biometricsStore.error;
    frames.value = [];
  } finally {
    submitting.value = false;
  }
}
</script>

<template>
  <div class="vb-biometric-enroll-auth">
    <h1 class="vb-biometric-enroll-auth__title">Biometric enrollment</h1>

    <p class="vb-biometric-enroll-auth__subtitle">
      This is a one-time setup to secure your account.
    </p>

    <p class="vb-biometric-enroll-auth__instruction">
      Let's set up your biometric profile. Align your face, complete the blink and head-turn checks, then capture
      {{ FRAMES_REQUIRED }} verification frames.
    </p>

    <VAlert
      v-if="submitError"
      variant="error"
      dismissible
      class="vb-biometric-enroll-auth__alert"
      @dismiss="submitError = ''"
    >
      {{ submitError }}
    </VAlert>

    <BiometricScanner
      mode="enrollment"
      :frames-captured="framesCaptured"
      :frames-required="FRAMES_REQUIRED"
      @frame="handleFrame"
    />

    <VButton
      variant="primary"
      block
      size="sm"
      :loading="biometricsStore.actionLoading || submitting"
      :disabled="frames.length < FRAMES_REQUIRED || submitting"
      @click="completeEnrollment"
    >
      Complete enrollment
    </VButton>

    <VButton
      v-if="submitError"
      variant="ghost"
      block
      size="sm"
      :disabled="submitting"
      @click="frames = []; submitError = ''"
    >
      Try again
    </VButton>
  </div>
</template>

<style scoped>
.vb-biometric-enroll-auth {
  @apply flex w-full flex-col gap-3;
}

.vb-biometric-enroll-auth__title {
  @apply text-center text-lg font-semibold text-brand;
}

.vb-biometric-enroll-auth__subtitle {
  @apply text-center text-xs text-slate-600;
}

.vb-biometric-enroll-auth__instruction {
  @apply text-center text-sm text-slate-700;
}

.vb-biometric-enroll-auth__alert {
  @apply text-sm;
}
</style>
