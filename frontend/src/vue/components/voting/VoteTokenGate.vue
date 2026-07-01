<script setup>
import { computed, watch } from "vue";
import { VAlert, VButton } from "@/components/ui";
import VoteSvtField from "./VoteSvtField.vue";
import {
  isValidSvtToken,
  looksLikePartialSvtToken,
  normalizeSvtToken,
} from "@/utils/svtToken";

const props = defineProps({
  modelValue: { type: String, default: "" },
  electionTitle: { type: String, default: "" },
  loading: { type: Boolean, default: false },
  requesting: { type: Boolean, default: false },
  issuedToken: { type: String, default: "" },
  error: { type: String, default: "" },
  canRequestToken: { type: Boolean, default: true },
  hasActiveToken: { type: Boolean, default: false },
  validationFailures: { type: Number, default: 0 },
  maxFailuresBeforeRequest: { type: Number, default: 3 },
});

const emit = defineEmits(["update:modelValue", "request-token", "validate", "back"]);

const INPUT_ID = "vote-svt-input";

const tokenReady = computed(() => isValidSvtToken(props.modelValue));
const tokenIncomplete = computed(() => looksLikePartialSvtToken(props.modelValue));

const showRequestToken = computed(
  () =>
    props.validationFailures >= props.maxFailuresBeforeRequest && props.canRequestToken
);

const failuresRemaining = computed(() =>
  Math.max(0, props.maxFailuresBeforeRequest - props.validationFailures)
);

const requestHint = computed(() => {
  if (showRequestToken.value) return "";
  if (props.hasActiveToken && !props.canRequestToken) {
    return "You already have an active token. Paste it above to continue.";
  }
  if (props.validationFailures > 0 && failuresRemaining.value > 0) {
    return `${failuresRemaining.value} attempt${failuresRemaining.value === 1 ? "" : "s"} left before you can request a new token.`;
  }
  return "";
});

watch(
  () => props.issuedToken,
  (token) => {
    if (token) {
      emit("update:modelValue", normalizeSvtToken(token));
    }
  }
);
</script>

<template>
  <section class="w-full" aria-labelledby="vote-token-heading">
    <div class="rounded-card border border-border bg-surface p-6 shadow-card sm:p-8">
      <header class="max-w-xl">
        <h2 id="vote-token-heading" class="text-xl font-semibold text-ink-primary sm:text-2xl">
          Enter your voting token
        </h2>
        <p v-if="electionTitle" class="mt-1 text-sm font-medium text-brand-700">
          {{ electionTitle }}
        </p>
        <p class="mt-2 text-sm text-ink-secondary">
          Paste the token sent to you to continue voting.
        </p>
      </header>

      <VAlert v-if="error" class="mt-6 max-w-xl" variant="error">{{ error }}</VAlert>

      <VAlert
        v-if="issuedToken"
        class="mt-6 max-w-xl"
        variant="warning"
        title="Save your token"
      >
        <p class="break-all font-mono text-sm">{{ issuedToken }}</p>
      </VAlert>

      <VAlert
        v-else-if="hasActiveToken && !modelValue"
        class="mt-6 max-w-xl"
        variant="info"
      >
        You already have an active token for this election. Paste it below to continue.
      </VAlert>

      <form
        class="mt-6 max-w-xl space-y-4"
        autocomplete="off"
        @submit.prevent="tokenReady && $emit('validate')"
      >
        <VoteSvtField
          :input-id="INPUT_ID"
          :model-value="modelValue"
          :error="tokenIncomplete ? 'Token looks incomplete. Paste the full code from your message.' : ''"
          required
          @update:model-value="emit('update:modelValue', $event)"
        />

        <div class="flex flex-col gap-3 pt-1 sm:flex-row sm:items-center">
          <VButton
            v-if="tokenReady"
            type="submit"
            :loading="loading"
            class="min-h-[48px] sm:min-w-[160px]"
          >
            Continue
          </VButton>

          <button
            v-if="showRequestToken"
            type="button"
            class="text-sm font-medium text-brand-700 hover:text-brand-hover disabled:opacity-50"
            :disabled="requesting || loading"
            @click="$emit('request-token')"
          >
            {{ requesting ? "Sending…" : "Request a new token" }}
          </button>

          <p v-else-if="requestHint" class="text-sm text-ink-secondary">
            {{ requestHint }}
          </p>
        </div>
      </form>
    </div>

    <button
      type="button"
      class="mt-5 text-sm font-medium text-ink-secondary hover:text-ink-primary"
      @click="$emit('back')"
    >
      ← Back to my elections
    </button>
  </section>
</template>
