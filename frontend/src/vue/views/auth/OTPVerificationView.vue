<script setup>
import { computed, onMounted, onUnmounted, reactive, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import OtpPinInput from "@/components/auth/OtpPinInput.vue";
import { VAlert, VButton } from "@/components/ui";
import { useToast } from "@/composables/useToast";
import { useAuthStore } from "@/stores/auth";
import { navigateAfterLogin } from "@/utils/postLoginNavigation";
import { otpCode, required, validateFields } from "@/utils/validators";

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();
const toast = useToast();

const otp = ref("");
const errors = reactive({ otp_code: "" });
const submitError = ref("");
const resendCooldown = ref(0);
const verifying = ref(false);
let cooldownTimer = null;

const challenge = computed(() => authStore.otpChallenge);
const channelLabel = computed(() => {
  const channel = challenge.value?.channel || "sms";
  return channel === "email" ? "Email" : "SMS";
});

const maskedDestination = computed(() => challenge.value?.masked_destination || "your registered contact");

onMounted(() => {
  if (authStore.isAuthenticated) {
    navigateAfterLogin(router, authStore.postLoginRedirect).catch(() => {});
    return;
  }
  if (!authStore.hasPendingOtp) {
    router.replace({ name: "auth-login" });
  }
});

onUnmounted(() => {
  if (cooldownTimer) window.clearInterval(cooldownTimer);
});

function startCooldown(seconds = 60) {
  resendCooldown.value = seconds;
  cooldownTimer = window.setInterval(() => {
    resendCooldown.value -= 1;
    if (resendCooldown.value <= 0) {
      window.clearInterval(cooldownTimer);
      cooldownTimer = null;
    }
  }, 1000);
}

async function handleVerify() {
  if (verifying.value || authStore.otpLoading) return;

  submitError.value = "";
  const { valid, errors: fieldErrors } = validateFields(
    { otp_code: otp.value },
    {
      otp_code: [required("Enter the full verification code."), otpCode()],
    }
  );
  errors.otp_code = fieldErrors.otp_code || "";
  if (!valid) return;

  verifying.value = true;
  try {
    const result = await authStore.verifyOtp(otp.value);
    if (result?.requiresEnrollment) {
      await router.replace({
        name: "auth-biometric-enroll",
        query: route.query.redirect ? { redirect: route.query.redirect } : {},
      });
      return;
    }
    if (result?.requiresBiometric) {
      await router.replace({
        name: "auth-biometric-verify",
        query: route.query.redirect ? { redirect: route.query.redirect } : {},
      });
      return;
    }
    toast.success("Signed in successfully");
    const redirect =
      typeof route.query.redirect === "string" && route.query.redirect.startsWith("/")
        ? route.query.redirect
        : result.redirectPath;
    await navigateAfterLogin(router, redirect);
  } catch (error) {
    submitError.value = error.message;
    otp.value = "";
  } finally {
    verifying.value = false;
  }
}

async function handleResend() {
  submitError.value = "";
  try {
    await authStore.resendOtp();
    toast.info("A new verification code has been sent.");
    otp.value = "";
    startCooldown();
  } catch (error) {
    submitError.value = error.message;
  }
}

function backToLogin() {
  authStore.clearOtpFlow();
  router.push({ name: "auth-login" });
}
</script>

<template>
  <form class="space-y-4" @submit.prevent="handleVerify">
    <div class="vb-auth-channel">
      <h2 class="text-base font-semibold text-slate-800">Verify your identity</h2>
      <p class="vb-auth-channel-label mt-2">Secure verification channel</p>
      <p class="mt-1 text-sm text-slate-600">
        A 6-digit code was sent via {{ channelLabel.toLowerCase() }} to
        <span class="font-medium text-slate-800">{{ maskedDestination }}</span>.
      </p>
    </div>

    <VAlert v-if="submitError" variant="error" dismissible @dismiss="submitError = ''">
      {{ submitError }}
    </VAlert>

    <OtpPinInput
      v-model="otp"
      :error="errors.otp_code"
      :disabled="authStore.otpLoading || verifying"
      @complete="handleVerify"
    />

    <VButton type="submit" block :loading="authStore.otpLoading || verifying" :disabled="otp.length < 6 || verifying">
      Verify &amp; sign in
    </VButton>

    <div class="flex flex-col gap-3 border-t border-border pt-4 sm:flex-row sm:items-center sm:justify-between">
      <button
        type="button"
        class="text-sm font-medium text-slate-500 hover:text-slate-800 disabled:opacity-50"
        :disabled="resendCooldown > 0 || authStore.otpLoading"
        @click="handleResend"
      >
        {{ resendCooldown > 0 ? `Resend in ${resendCooldown}s` : "Resend code" }}
      </button>
      <button
        type="button"
        class="text-sm font-medium text-slate-500 hover:text-slate-800"
        @click="backToLogin"
      >
        Back to sign in
      </button>
    </div>
  </form>
</template>
