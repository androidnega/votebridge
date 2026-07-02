<script setup>
import { onMounted, reactive, ref } from "vue";
import { RouterLink, useRoute, useRouter } from "vue-router";
import { VAlert, VButton, VCheckbox, VInput, VPasswordInput } from "@/components/ui";
import { useAuthStore } from "@/stores/auth";
import { getRememberedIdentifier, setRememberedIdentifier } from "@/utils/auth";
import { navigateAfterLogin } from "@/utils/postLoginNavigation";
import { minLength, required, validateFields } from "@/utils/validators";

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();

/** student | staff — staff path is reached via subtle “Staff access” only */
const entryMode = ref("student");
/** identity | password */
const step = ref("identity");
const form = reactive({
  identity: "",
  password: "",
  remember: false,
});
const errors = reactive({});
const submitError = ref("");

onMounted(() => {
  form.identity = getRememberedIdentifier();
  form.remember = Boolean(form.identity);
  import("@/views/auth/OTPVerificationView.vue");
});

function openStaffAccess() {
  entryMode.value = "staff";
  submitError.value = "";
  errors.identity = "";
  step.value = "identity";
}

function returnToStudentEntry() {
  entryMode.value = "student";
  submitError.value = "";
  errors.identity = "";
  errors.password = "";
  step.value = "identity";
}

async function goToOtpStep() {
  await router.push({
    name: "auth-otp",
    query: { redirect: route.query.redirect },
  });
}

async function continueIdentity() {
  submitError.value = "";
  const identityMessage =
    entryMode.value === "student" ? "Enter your index number." : "Enter your email or username.";
  const { valid, errors: fieldErrors } = validateFields(form, {
    identity: [required(identityMessage)],
  });
  errors.identity = fieldErrors.identity || "";
  if (!valid) return;

  if (form.remember) {
    setRememberedIdentifier(form.identity);
  } else {
    setRememberedIdentifier("");
  }

  try {
    const result = await authStore.continueLogin({
      identity: form.identity,
    });

    if (result?.completed) {
      await navigateAfterLogin(router, result.redirectPath || route.query.redirect);
      return;
    }

    if (result?.requires_password) {
      step.value = "password";
      return;
    }

    await goToOtpStep();
  } catch (error) {
    submitError.value = error.message;
  }
}

async function submitPassword() {
  submitError.value = "";
  const { valid, errors: fieldErrors } = validateFields(form, {
    password: [required("Password is required."), minLength(8)],
  });
  errors.password = fieldErrors.password || "";
  if (!valid) return;

  try {
    const challenge = await authStore.continueLogin({
      identity: form.identity,
      password: form.password,
    });

    if (challenge?.completed) {
      await navigateAfterLogin(router, challenge.redirectPath || route.query.redirect);
      return;
    }

    await goToOtpStep();
  } catch (error) {
    submitError.value = error.message;
  }
}

function backFromPassword() {
  submitError.value = "";
  step.value = "identity";
}
</script>

<template>
  <div class="space-y-4">
    <VAlert v-if="submitError" variant="error" dismissible @dismiss="submitError = ''">
      {{ submitError }}
    </VAlert>

    <form v-if="step === 'identity' && entryMode === 'student'" class="space-y-4" @submit.prevent="continueIdentity">
      <div>
        <h2 class="text-base font-semibold text-slate-800">Sign in</h2>
        <p class="mt-1 text-sm text-slate-500">
          Enter your index number. A one-time code will be sent to your registered phone or email.
        </p>
      </div>

      <VInput
        id="identity"
        v-model="form.identity"
        label="Index number"
        autocomplete="username"
        placeholder="BC/ITS/24/047"
        :error="errors.identity"
        required
      />

      <VButton type="submit" block :loading="authStore.loading">Continue</VButton>

      <p class="text-center">
        <button
          type="button"
          class="text-xs font-medium text-slate-400 hover:text-slate-600"
          @click="openStaffAccess"
        >
          Staff access
        </button>
      </p>
    </form>

    <form v-else-if="step === 'identity' && entryMode === 'staff'" class="space-y-4" @submit.prevent="continueIdentity">
      <div>
        <h2 class="text-base font-semibold text-slate-800">Staff access</h2>
        <p class="mt-1 text-sm text-slate-500">Enter your email or username to continue.</p>
      </div>

      <VInput
        id="staff-identity"
        v-model="form.identity"
        label="Email or username"
        autocomplete="username"
        placeholder="admin@ttu.edu.gh"
        :error="errors.identity"
        required
      />

      <VButton type="submit" block :loading="authStore.loading">Continue</VButton>

      <p class="text-center">
        <button
          type="button"
          class="text-xs font-medium text-slate-400 hover:text-slate-600"
          @click="returnToStudentEntry"
        >
          Back to student sign in
        </button>
      </p>
    </form>

    <form v-else-if="step === 'password'" class="space-y-4" @submit.prevent="submitPassword">
      <div>
        <h2 class="text-base font-semibold text-slate-800">Enter password</h2>
        <p class="mt-1 text-sm text-slate-500">Enter your password to continue signing in.</p>
        <p class="mt-1 truncate text-sm font-medium text-slate-700">{{ form.identity.trim() }}</p>
      </div>

      <VPasswordInput
        id="password"
        v-model="form.password"
        label="Password"
        autocomplete="current-password"
        placeholder="Enter your password"
        :error="errors.password"
        required
      />

      <div class="flex items-center justify-between gap-3">
        <VCheckbox id="remember" v-model="form.remember" label="Remember me" />
        <RouterLink to="/auth/forgot-password" class="text-sm font-medium text-brand-700 hover:underline">
          Forgot password?
        </RouterLink>
      </div>

      <VButton type="submit" block :loading="authStore.loading">Continue</VButton>

      <button
        type="button"
        class="w-full text-center text-sm font-medium text-slate-500 hover:text-slate-800"
        @click="backFromPassword"
      >
        Back
      </button>
    </form>
  </div>
</template>
