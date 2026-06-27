<script setup>
import { VButton, VInput, VModal } from "@/components/ui";

defineProps({
  modelValue: Boolean,
  otpCode: String,
  verifying: Boolean,
  requesting: Boolean,
});

const emit = defineEmits(["update:modelValue", "update:otpCode", "verify", "resend"]);
</script>

<template>
  <VModal
    :model-value="modelValue"
    title="Confirm your identity"
    size="sm"
    @update:model-value="emit('update:modelValue', $event)"
  >
    <p class="mb-4 text-sm text-slate-600">
      This action requires step-up authentication. Enter the verification code sent to your registered contact.
    </p>
    <VInput
      :model-value="otpCode"
      label="Verification code"
      autocomplete="one-time-code"
      inputmode="numeric"
      @update:model-value="emit('update:otpCode', $event)"
    />
    <template #footer>
      <div class="flex flex-col gap-2 sm:flex-row sm:justify-end">
        <VButton variant="ghost" :disabled="requesting" @click="emit('resend')">Resend code</VButton>
        <VButton variant="primary" :loading="verifying" @click="emit('verify')">Verify &amp; continue</VButton>
      </div>
    </template>
  </VModal>
</template>
