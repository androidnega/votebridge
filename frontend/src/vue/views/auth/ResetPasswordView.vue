<script setup>
import { reactive, ref } from "vue";
import { RouterLink, useRoute } from "vue-router";
import { VAlert, VButton, VPasswordInput } from "@/components/ui";
import { branding } from "@/config/branding";
import { minLength, required, validateFields } from "@/utils/validators";

const route = useRoute();
const form = reactive({ password: "", confirm: "" });
const errors = reactive({ password: "", confirm: "" });
const submitted = ref(false);

const tokenPresent = Boolean(route.query.token);

function handleSubmit() {
  const { valid, errors: fieldErrors } = validateFields(form, {
    password: [required("Password is required."), minLength(8)],
    confirm: [required("Confirm your password.")],
  });
  errors.password = fieldErrors.password || "";
  errors.confirm = fieldErrors.confirm || "";
  if (form.password !== form.confirm) {
    errors.confirm = "Passwords do not match.";
    return;
  }
  if (!valid) return;
  submitted.value = true;
}
</script>

<template>
  <form class="space-y-4" @submit.prevent="handleSubmit">
    <h2 class="text-base font-semibold text-slate-800">Reset password</h2>

    <VAlert v-if="!tokenPresent" variant="warning">
      This reset link is invalid or expired. Contact
      <a class="font-medium underline" :href="`mailto:${branding.electionOfficeEmail}`">
        {{ branding.electionOfficeEmail }}
      </a>
      for a new link.
    </VAlert>

    <VAlert v-else-if="submitted" variant="success">
      Your password has been recorded. You may now sign in with your new credentials.
    </VAlert>

    <template v-else>
      <VPasswordInput
        id="reset-password"
        v-model="form.password"
        label="New password"
        autocomplete="new-password"
        :error="errors.password"
      />
      <VPasswordInput
        id="reset-confirm"
        v-model="form.confirm"
        label="Confirm password"
        autocomplete="new-password"
        :error="errors.confirm"
      />
      <VButton type="submit" block>Reset password</VButton>
    </template>

    <p class="text-center text-sm text-slate-600">
      <RouterLink to="/auth/login" class="font-medium text-brand-700 hover:underline">Back to sign in</RouterLink>
    </p>
  </form>
</template>
