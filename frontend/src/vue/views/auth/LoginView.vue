<script setup>
import { onMounted, reactive, ref } from "vue";
import { RouterLink, useRoute, useRouter } from "vue-router";
import AuthSecurityTerminal from "@/components/auth/AuthSecurityTerminal.vue";
import { VAlert, VButton, VCheckbox, VInput, VPasswordInput } from "@/components/ui";
import { useAuthStore } from "@/stores/auth";
import { navigateAfterLogin } from "@/utils/postLoginNavigation";
import { getRememberedIdentifier, setRememberedIdentifier } from "@/utils/auth";
import { minLength, required, validateFields } from "@/utils/validators";

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();

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

onMounted(() => {
  form.identity = getRememberedIdentifier();
  form.remember = Boolean(form.identity);
});

async function continueIdentity() {
  submitError.value = "";
  const { valid, errors: fieldErrors } = validateFields(form, {
    identity: [required("Enter your index number or administrator username.")],
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

    if (result?.mfa_required) {
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
        <h2 class="text-base font-semibold text-slate-800">Sign in</h2>
        <p class="mt-1 text-sm text-slate-500">
          Enter your student index number or administrator username.
        </p>
      </div>

      <VInput
        id="identity"
        v-model="form.identity"
        label="Index number or username"
        autocomplete="username"
        placeholder="BC/ITS/24/047 or admin@ttu.edu.gh"
        :error="errors.identity"
        required
      />

      <VButton type="submit" block :loading="authStore.loading">Continue</VButton>
    </form>

    <form v-else-if="step === 'password'" class="space-y-4" @submit.prevent="submitPassword">
      <div>
        <h2 class="text-base font-semibold text-slate-800">Enter password</h2>
        <p class="mt-1 truncate text-sm text-slate-500">{{ form.identity.trim() }}</p>
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
