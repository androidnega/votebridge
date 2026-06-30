<script setup>
import { computed, onMounted, onUnmounted, reactive, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { VAlert, VButton, VInput } from "@/components/ui";
import { normalizeAuthRedirect, DASHBOARD_ROOT } from "@/config/routes";
import { useToast } from "@/composables/useToast";
import { otpCode, required, validateFields } from "@/utils/validators";

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();
const toast = useToast();

const otp = ref("");
const errors = reactive({ otp_code: "" });
const submitError = ref("");
const resendCooldown = ref(0);
let cooldownTimer = null;

const challenge = computed(() => authStore.otpChallenge);
const channelLabel = computed(() => {
  const channel = challenge.value?.channel || "email";
  return channel.charAt(0).toUpperCase() + channel.slice(1);
});

const maskedDestination = computed(() => challenge.value?.masked_destination || "your registered contact");

onMounted(() => {
  if (authStore.isAuthenticated) {
    router.replace(authStore.postLoginRedirect || { name: "dashboard" });
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
  submitError.value = "";
  const { valid, errors: fieldErrors } = validateFields(
    { otp_code: otp.value },
    {
      otp_code: [required("Verification code is required."), otpCode()],
    }
  );
  errors.otp_code = fieldErrors.otp_code || "";
  if (!valid) return;

    try {
    const result = await authStore.verifyOtp(otp.value);
    if (result?.requiresBiometric) {
      await router.replace({
        name: "auth-biometric-verify",
        query: route.query.redirect ? { redirect: route.query.redirect } : {},
      });
      return;
    }
    toast.success("Signed in successfully");
    const redirect = normalizeAuthRedirect(
      typeof route.query.redirect === "string" && route.query.redirect.startsWith("/")
        ? route.query.redirect
        : result.redirectPath
    );
    await router.replace(redirect);
  } catch (error) {
    submitError.value = error.message;
  }
}

async function handleResend() {
  submitError.value = "";
  try {
    await authStore.resendOtp();
    toast.info("A new verification code has been sent.");
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
  <form class="space-y-5" @submit.prevent="handleVerify">
    <div>
      <h2 class="text-xl font-semibold text-slate-800">Verify your identity</h2>
      <p class="mt-1 text-sm text-slate-500">
        Enter the verification code sent to {{ maskedDestination }} via
        {{ channelLabel.toLowerCase() }}.
      </p>
    </div>

    <VAlert v-if="challenge?.mfa_required" variant="warning" title="Additional verification required">
      Enter the verification code sent to your registered contact to continue.
    </VAlert>

    <VAlert v-if="submitError" variant="error" dismissible @dismiss="submitError = ''">
      {{ submitError }}
    </VAlert>

    <VInput
      id="otp_code"
      v-model="otp"
      label="Verification code"
      inputmode="numeric"
      autocomplete="one-time-code"
      placeholder="Enter 6-digit code"
      :error="errors.otp_code"
      required
    />

    <VButton type="submit" block :loading="authStore.otpLoading">
      Verify &amp; sign in
    </VButton>

    <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <VButton
        type="button"
        variant="secondary"
        :disabled="resendCooldown > 0 || authStore.otpLoading"
        @click="handleResend"
      >
        {{
          resendCooldown > 0
            ? `Resend in ${resendCooldown}s`
            : "Resend code"
        }}
      </VButton>
      <button
        type="button"
        class="text-sm font-medium text-brand-600 hover:text-brand-hover"
        @click="backToLogin"
      >
        Back to sign in
      </button>
    </div>
  </form>
</template>
