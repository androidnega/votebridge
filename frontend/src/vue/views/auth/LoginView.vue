<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import { RouterLink, useRoute, useRouter } from "vue-router";
import AuthSecurityTerminal from "@/components/auth/AuthSecurityTerminal.vue";
import { VAlert, VButton, VCheckbox, VInput, VPasswordInput } from "@/components/ui";
import { useAuthStore } from "@/stores/auth";
import { getRememberedIdentifier, looksLikeStaffIdentity, setRememberedIdentifier } from "@/utils/auth";
import { navigateAfterLogin } from "@/utils/postLoginNavigation";
import { minLength, required, validateFields } from "@/utils/validators";

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();

/** student | staff */
const loginMode = ref("student");
/** identity | password | auth-check (super admin only) */
const step = ref("identity");
const form = reactive({
  identity: "",
  password: "",
  remember: false,
});
const errors = reactive({});
const submitError = ref("");

const authLines = [
  "Establishing encrypted session...",
  "Verifying credentials...",
  "Identity confirmed.",
  "Opening secure OTP channel...",
];

const isStudentMode = computed(() => loginMode.value === "student");

const identityValidationMessage = computed(() =>
  isStudentMode.value ? "Enter your index number." : "Enter your email or username."
);

onMounted(() => {
  form.identity = getRememberedIdentifier();
  form.remember = Boolean(form.identity);
  if (form.identity && looksLikeStaffIdentity(form.identity)) {
    loginMode.value = "staff";
  }
});

function switchLoginMode(mode) {
  loginMode.value = mode;
  submitError.value = "";
  errors.identity = "";
  step.value = "identity";
}

async function continueIdentity() {
  submitError.value = "";
  const { valid, errors: fieldErrors } = validateFields(form, {
    identity: [required(identityValidationMessage.value)],
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
      loginMode.value = "staff";
      step.value = "password";
      return;
    }

    if (result?.mfa_required) {
      loginMode.value = "staff";
      step.value = "auth-check";
      return;
    }

    await router.push({
      name: "auth-otp",
      query: { redirect: route.query.redirect },
    });
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

    if (challenge?.mfa_required) {
      step.value = "auth-check";
      return;
    }

    await router.push({
      name: "auth-otp",
      query: { redirect: route.query.redirect },
    });
  } catch (error) {
    submitError.value = error.message;
  }
}

async function onAuthCheckComplete() {
  await router.push({
    name: "auth-otp",
    query: { redirect: route.query.redirect },
  });
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

    <form v-if="step === 'identity'" class="space-y-4" @submit.prevent="continueIdentity">
      <div>
        <h2 class="text-base font-semibold text-slate-800">
          {{ isStudentMode ? "Student sign in" : "Administrator sign in" }}
        </h2>
        <p class="mt-1 text-sm text-slate-500">
          <template v-if="isStudentMode">
            Enter your index number. Candidates use the same sign-in — a one-time code will be sent to
            your registered phone or email.
          </template>
          <template v-else>
            Enter your email or username, then your password and verification code.
          </template>
        </p>
      </div>

      <VInput
        id="identity"
        v-model="form.identity"
        :label="isStudentMode ? 'Index number' : 'Email or username'"
        autocomplete="username"
        :placeholder="isStudentMode ? 'BC/ITS/24/047' : 'admin@ttu.edu.gh'"
        :error="errors.identity"
        required
      />

      <VButton type="submit" block :loading="authStore.loading">Continue</VButton>

      <p class="text-center text-sm text-slate-600">
        <button
          v-if="isStudentMode"
          type="button"
          class="font-medium text-brand-700 hover:underline"
          @click="switchLoginMode('staff')"
        >
          Election officer or administrator sign in
        </button>
        <button
          v-else
          type="button"
          class="font-medium text-brand-700 hover:underline"
          @click="switchLoginMode('student')"
        >
          Student or candidate? Sign in with index number
        </button>
      </p>
    </form>

    <form v-else-if="step === 'password'" class="space-y-4" @submit.prevent="submitPassword">
      <div>
        <h2 class="text-base font-semibold text-slate-800">Administrator sign in</h2>
        <p class="mt-1 text-sm text-slate-500">Enter your password to continue.</p>
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

    <AuthSecurityTerminal
      v-else-if="step === 'auth-check'"
      :lines="authLines"
      :min-duration="2200"
      @complete="onAuthCheckComplete"
    />
  </div>
</template>
