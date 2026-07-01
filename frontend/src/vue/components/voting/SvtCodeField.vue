<script setup>
import { computed, onMounted, ref, watch } from "vue";
import {
  formatSvtTokenInput,
  isValidSvtToken,
  normalizeSvtToken,
  svtTokenSegments,
} from "@/utils/svtToken";

const props = defineProps({
  modelValue: { type: String, default: "" },
  inputId: { type: String, default: "svt-code-input" },
  disabled: { type: Boolean, default: false },
  error: { type: String, default: "" },
  autofocus: { type: Boolean, default: true },
});

const emit = defineEmits(["update:modelValue", "submit"]);

const inputRef = ref(null);

const displayValue = computed(() => formatSvtTokenInput(props.modelValue));
const segments = computed(() => svtTokenSegments(props.modelValue));
const isComplete = computed(() => isValidSvtToken(props.modelValue));

onMounted(() => {
  if (props.autofocus) {
    window.setTimeout(() => inputRef.value?.focus(), 80);
  }
});

watch(
  () => props.modelValue,
  (value) => {
    if (isValidSvtToken(value)) {
      inputRef.value?.setSelectionRange?.(displayValue.value.length, displayValue.value.length);
    }
  }
);

function updateValue(raw) {
  emit("update:modelValue", formatSvtTokenInput(raw));
}

function handleInput(event) {
  updateValue(event.target.value);
  event.target.value = formatSvtTokenInput(event.target.value);
}

function handlePaste(event) {
  const pasted = event.clipboardData?.getData("text");
  if (!pasted) return;
  event.preventDefault();
  const formatted = formatSvtTokenInput(pasted);
  emit("update:modelValue", formatted);
  if (inputRef.value) {
    inputRef.value.value = formatted;
  }
}

function handleKeydown(event) {
  if (event.key === "Enter" && isComplete.value && !props.disabled) {
    event.preventDefault();
    emit("submit");
  }
}
</script>

<template>
  <div class="vb-svt-code-field" :class="{ 'vb-svt-code-field--error': error }">
    <div class="vb-svt-code-segments" aria-hidden="true">
      <span class="vb-svt-code-segment" :class="{ 'is-filled': segments[0] }">{{ segments[0] || "VB" }}</span>
      <span class="vb-svt-code-separator">-</span>
      <span class="vb-svt-code-segment" :class="{ 'is-filled': segments[1] }">{{ segments[1] || "····" }}</span>
      <span class="vb-svt-code-separator">-</span>
      <span class="vb-svt-code-segment" :class="{ 'is-filled': segments[2] }">{{ segments[2] || "····" }}</span>
    </div>

    <input
      :id="inputId"
      ref="inputRef"
      :value="displayValue"
      type="text"
      inputmode="text"
      autocomplete="one-time-code"
      autocapitalize="characters"
      autocorrect="off"
      spellcheck="false"
      maxlength="13"
      :disabled="disabled"
      :aria-invalid="error ? 'true' : 'false'"
      :aria-describedby="error ? `${inputId}-error` : `${inputId}-hint`"
      class="vb-svt-code-input"
      aria-label="Secure Voting Token"
      @input="handleInput"
      @paste="handlePaste"
      @keydown="handleKeydown"
    />

    <p :id="`${inputId}-hint`" class="sr-only">
      Enter your voting code in the format V B dash four characters dash four characters.
      Current value: {{ normalizeSvtToken(modelValue) || "empty" }}.
    </p>
    <p v-if="error" :id="`${inputId}-error`" class="vb-svt-code-error" role="alert">
      {{ error }}
    </p>
  </div>
</template>
