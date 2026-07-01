<script setup>
import { computed, ref } from "vue";
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

const inputRef = ref(null);

const canSubmit = computed(() => isValidSvtToken(props.modelValue));

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
  <section class="mx-auto w-full max-w-md">
    <header class="mb-6 text-center">
      <p class="text-xs font-semibold uppercase tracking-wide text-brand-700">
        Secure Voting Verification
      </p>
      <h1 class="mt-2 text-2xl font-bold text-ink-primary">Enter your voting code</h1>
      <p class="mt-3 text-sm leading-relaxed text-ink-secondary">
        To protect your ballot, a Secure Voting Token has been sent to your registered phone number
        <span v-if="maskedPhone" class="font-semibold text-ink-primary">{{ maskedPhone }}</span>.
        Enter the 6-digit code below to begin voting.
      </p>
    </header>

    <form class="space-y-4" @submit.prevent="canSubmit && emit('submit')">
      <label class="block">
        <span class="vb-svt-field-label">Secure Voting Token</span>
        <input
          ref="inputRef"
          :value="modelValue"
          type="text"
          inputmode="numeric"
          autocomplete="one-time-code"
          maxlength="6"
          placeholder="000000"
          class="vb-svt-field-input text-center text-2xl tracking-[0.35em]"
          @input="onInput"
          @paste="onPaste"
        />
      </label>

      <p v-if="error" class="text-sm text-red-600">{{ error }}</p>

      <VButton type="submit" class="min-h-[48px] w-full" :disabled="!canSubmit" :loading="loading">
        Verify &amp; Continue
      </VButton>

      <div class="flex items-center justify-between text-sm">
        <button
          type="button"
          class="font-medium text-brand-700 hover:text-brand-800 disabled:cursor-not-allowed disabled:opacity-50"
          :disabled="resendSeconds > 0 || resendLoading"
          @click="emit('resend')"
        >
          Resend SVT
        </button>
        <span class="text-ink-secondary">
          <template v-if="resendSeconds > 0">Resend in {{ resendSeconds }}s</template>
          <template v-else>Didn't receive it?</template>
        </span>
      </div>
    </form>
  </section>
</template>
