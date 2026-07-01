<script setup>
import { computed, onMounted, ref } from "vue";
import { VAlert, VButton, VCard, VInput } from "@/components/ui";
import { useBiometricsStore } from "@/stores/biometrics";
import { useToast } from "@/composables/useToast";
import { toastMessages } from "@/config/toastMessages";

const store = useBiometricsStore();
const toast = useToast();

const password = ref("");
const otpCode = ref("");
const otpChallenge = ref(null);
const step = ref("idle");
const error = ref("");
const loading = ref(false);

const enrolled = computed(() => store.isEnrolled);

onMounted(() => {
  store.fetchStatus().catch(() => {});
});

async function requestResetOtp() {
  error.value = "";
  if (!password.value) {
    error.value = "Enter your password to continue.";
    return;
  }
  loading.value = true;
  try {
    otpChallenge.value = await store.requestResetOtp(password.value);
    step.value = "otp";
    toast.success("Verification code sent.");
  } catch (err) {
    error.value = err.message || store.error;
  } finally {
    loading.value = false;
  }
}

async function confirmReset() {
  error.value = "";
  if (!otpChallenge.value?.otp_request_uuid || !otpCode.value) {
    error.value = "Enter the verification code.";
    return;
  }
  loading.value = true;
  try {
    await store.resetProfile({
      password: password.value,
      otpRequestUuid: otpChallenge.value.otp_request_uuid,
      otpCode: otpCode.value,
    });
    await store.fetchStatus();
    toast.success(toastMessages.biometric.reset || "Biometric profile reset.");
    password.value = "";
    otpCode.value = "";
    otpChallenge.value = null;
    step.value = "idle";
  } catch (err) {
    error.value = err.message || store.error;
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <VCard v-if="enrolled" title="Biometric profile" class="mt-6">
    <p class="mb-4 text-sm text-slate-600">
      Remove your stored face profile. You will be asked to enroll again on your next sign-in.
    </p>

    <VAlert v-if="error" variant="error" class="mb-4">{{ error }}</VAlert>

    <VInput
      v-model="password"
      type="password"
      label="Account password"
      autocomplete="current-password"
      class="mb-3"
    />

    <VInput
      v-if="step === 'otp'"
      v-model="otpCode"
      label="Verification code"
      autocomplete="one-time-code"
      class="mb-3"
    />

    <VButton
      v-if="step === 'idle'"
      variant="danger"
      size="sm"
      :loading="loading"
      @click="requestResetOtp"
    >
      Reset biometric profile
    </VButton>
    <VButton
      v-else
      variant="danger"
      size="sm"
      :loading="loading"
      @click="confirmReset"
    >
      Confirm reset
    </VButton>
  </VCard>
</template>
