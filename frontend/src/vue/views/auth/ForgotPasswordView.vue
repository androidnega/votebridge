<script setup>
import { reactive, ref } from "vue";
import { RouterLink } from "vue-router";
import { VAlert, VButton, VInput } from "@/components/ui";
import { branding } from "@/config/branding";
import { required, validateFields } from "@/utils/validators";

const form = reactive({ identity: "" });
const errors = reactive({ identity: "" });
const submitted = ref(false);

function handleSubmit() {
  const { valid, errors: fieldErrors } = validateFields(form, {
    identity: [required("Enter your email or username.")],
  });
  errors.identity = fieldErrors.identity || "";
  if (!valid) return;
  submitted.value = true;
}
</script>

<template>
  <form class="space-y-4" @submit.prevent="handleSubmit">
    <h2 class="text-base font-semibold text-slate-800">Forgot password</h2>
    <p class="text-sm text-slate-600">
      For election officers and administrators. Students and candidates sign in with their index
      number only — contact the election office if you need help accessing your account.
    </p>

    <VAlert v-if="submitted" variant="info">
      If an account exists for {{ form.identity.trim() }}, visit the election office or email
      <a class="font-medium underline" :href="`mailto:${branding.electionOfficeEmail}`">
        {{ branding.electionOfficeEmail }}
      </a>
      to complete your reset.
    </VAlert>

    <VInput
      id="forgot-identity"
      v-model="form.identity"
      label="Email or username"
      autocomplete="username"
      placeholder="admin@ttu.edu.gh"
      :error="errors.identity"
    />

    <VButton type="submit" block>Request password help</VButton>

    <p class="text-center text-sm text-slate-600">
      <RouterLink to="/auth/login" class="font-medium text-brand-700 hover:underline">Back to sign in</RouterLink>
    </p>
  </form>
</template>
