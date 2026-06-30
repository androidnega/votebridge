<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import { RouterLink, useRoute, useRouter } from "vue-router";
import { VAlert, VButton, VCheckbox, VInput, VPasswordInput } from "@/components/ui";
import { useAuthStore } from "@/stores/auth";
import { getRememberedIdentifier, setRememberedIdentifier } from "@/utils/auth";
import { minLength, required, validateFields } from "@/utils/validators";

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();

const form = reactive({
  identity: "",
  password: "",
  remember: false,
});
const errors = reactive({});
const submitError = ref("");

const credentialsReady = computed(() => {
  const identity = form.identity.trim();
  return identity.length > 0 && form.password.length >= 8;
});

onMounted(() => {
  form.identity = getRememberedIdentifier();
  form.remember = Boolean(form.identity);
});

function validationSchema() {
  return {
    identity: [required("Enter your index number.")],
    password: [required("Password is required."), minLength(8)],
  };
}

async function handleSubmit() {
  if (!credentialsReady.value) return;

  submitError.value = "";
  const { valid, errors: fieldErrors } = validateFields(form, validationSchema());
  Object.assign(errors, {
    identity: fieldErrors.identity || "",
    password: fieldErrors.password || "",
  });
  if (!valid) return;

  try {
    if (form.remember) {
      setRememberedIdentifier(form.identity);
    } else {
      setRememberedIdentifier("");
    }

    await authStore.initiateLogin({
      identity: form.identity,
      password: form.password,
    });
    await router.push({
      name: "auth-otp",
      query: { redirect: route.query.redirect },
    });
  } catch (error) {
    submitError.value = error.message;
  }
}
</script>

<template>
  <form class="space-y-3" @submit.prevent="handleSubmit">
    <h2 class="text-base font-semibold text-slate-800">Sign in</h2>

    <VAlert v-if="submitError" variant="error" dismissible @dismiss="submitError = ''">
      {{ submitError }}
    </VAlert>

    <VInput
      id="identity"
      v-model="form.identity"
      label="Index number"
      autocomplete="username"
      placeholder="BC/ITS/24/047"
      :error="errors.identity"
      required
    />

    <VPasswordInput
      id="password"
      v-model="form.password"
      label="Password"
      placeholder="Enter your password"
      :error="errors.password"
      required
    />

    <p class="text-right text-sm">
      <RouterLink to="/auth/forgot-password" class="font-medium text-brand-700 hover:underline">
        Forgot password?
      </RouterLink>
    </p>

    <Transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="opacity-0 translate-y-1"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition duration-150 ease-in"
      leave-from-class="opacity-100 translate-y-0"
      leave-to-class="opacity-0 translate-y-1"
    >
      <div
        v-if="credentialsReady"
        class="space-y-3 border-t border-border pt-3"
      >
        <p class="text-xs text-slate-500">
          Credentials entered. Continue to verify your identity.
        </p>

        <VCheckbox id="remember" v-model="form.remember" label="Remember me" />

        <VButton type="submit" block :loading="authStore.loading">
          Continue securely
        </VButton>
      </div>
    </Transition>
  </form>
</template>
