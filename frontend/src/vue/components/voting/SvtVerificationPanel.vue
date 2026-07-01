<script setup>
import { computed } from "vue";
import { formatSvtTokenInput, isValidSvtToken } from "@/utils/svtToken";
import { VButton } from "@/components/ui";

const props = defineProps({
  modelValue: { type: String, default: "" },
  maskedPhone: { type: String, default: "" },
  loading: { type: Boolean, default: false },
  resendLoading: { type: Boolean, default: false },
  resendSeconds: { type: Number, default: 0 },
  error: { type: String, default: "" },
});

const emit = defineEmits(["update:modelValue", "submit", "resend"]);

const canSubmit = computed(() => isValidSvtToken(props.modelValue));

const phoneHint = computed(() => props.maskedPhone || "your phone");

function onInput(event) {
  emit("update:modelValue", formatSvtTokenInput(event.target.value));
}

function onPaste(event) {
  event.preventDefault();
  const text = event.clipboardData?.getData("text") || "";
  emit("update:modelValue", formatSvtTokenInput(text));
}
</script>

<template>
  <section class="vb-svt-verify">
    <header class="vb-svt-verify-header">
      <p class="vb-svt-verify-kicker">Secure verification</p>
      <h1 class="vb-svt-verify-title">Voting code</h1>
      <p class="vb-svt-verify-subtitle">Enter the 6-digit code sent to {{ phoneHint }}</p>
    </header>

    <form class="vb-svt-verify-form" @submit.prevent="canSubmit && emit('submit')">
      <input
        :value="modelValue"
        type="text"
        inputmode="numeric"
        autocomplete="one-time-code"
        maxlength="6"
        placeholder="· · · · · ·"
        aria-label="6-digit voting code"
        class="vb-svt-verify-input"
        @input="onInput"
        @paste="onPaste"
      />

      <p v-if="error" class="text-sm text-red-600">{{ error }}</p>

      <VButton type="submit" class="min-h-[44px] w-full" :disabled="!canSubmit" :loading="loading">
        Verify &amp; continue
      </VButton>

      <div class="vb-svt-verify-footer">
        <button
          type="button"
          class="text-sm font-medium text-brand-700 hover:text-brand-800 disabled:opacity-50"
          :disabled="resendSeconds > 0 || resendLoading"
          @click="emit('resend')"
        >
          {{ resendLoading ? "Sending…" : "Resend code" }}
        </button>
        <span v-if="resendSeconds > 0" class="text-sm text-ink-secondary">{{ resendSeconds }}s</span>
      </div>
    </form>
  </section>
</template>
