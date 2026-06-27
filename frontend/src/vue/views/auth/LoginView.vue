<script setup>
import { onMounted, reactive, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { VAlert, VButton, VCheckbox, VInput, VPasswordInput } from "@/components/ui";
import { branding } from "@/config/branding";
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

onMounted(() => {
  form.identity = getRememberedIdentifier();
  form.remember = Boolean(form.identity);
});

function validationSchema() {
  return {
    identity: [required("Enter your index number, username, or email address.")],
    password: [required("Password is required."), minLength(8)],
  };
}

async function handleSubmit() {
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
  <form class="space-y-input-gap" @submit.prevent="handleSubmit">
    <VAlert v-if="submitError" variant="error" dismissible @dismiss="submitError = ''">
      {{ submitError }}
    </VAlert>

    <VInput
      id="identity"
      v-model="form.identity"
      label="Identity"
      autocomplete="username"
      placeholder="Enter your Index Number, Username or Email Address"
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

    <div class="flex items-center justify-between gap-4">
      <VCheckbox id="remember" v-model="form.remember" label="Remember me" />
      <button
        type="button"
        class="text-sm font-medium text-brand-600 hover:text-brand-hover"
        @click="submitError = 'Contact the election office to reset your password.'"
      >
        Forgot password?
      </button>
    </div>

    <VButton type="submit" block size="lg" :loading="authStore.loading">
      Sign In
    </VButton>

    <p class="text-center text-sm text-slate-500">
      Need help?
      <a
        :href="`mailto:${branding.electionOfficeEmail}`"
        class="font-medium text-brand-600 hover:text-brand-hover"
      >
        Contact Election Office
      </a>
    </p>
  </form>
</template>
