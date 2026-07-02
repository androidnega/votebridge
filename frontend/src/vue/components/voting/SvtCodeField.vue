<script setup>
import { computed, onMounted, ref, watch } from "vue";
import { formatSvtTokenInput, isValidSvtToken } from "@/utils/svtToken";

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
const isComplete = computed(() => isValidSvtToken(props.modelValue));

onMounted(() => {
  if (props.autofocus) {
    window.setTimeout(() => inputRef.value?.focus(), 120);
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

function handleInput(event) {
  const formatted = formatSvtTokenInput(event.target.value);
  emit("update:modelValue", formatted);
  event.target.value = formatted;
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
  <div class="space-y-1.5">
    <label :for="inputId" class="block text-sm font-medium text-ink-primary">
      Voting code
    </label>
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
      placeholder="VB-XXXX-XXXX"
      :disabled="disabled"
      :aria-invalid="error ? 'true' : 'false'"
      :aria-describedby="error ? `${inputId}-error` : undefined"
      class="block w-full min-h-[48px] rounded-lg border-2 border-slate-300 bg-white px-4 py-3 text-center font-mono text-lg tracking-wider text-ink-primary shadow-sm placeholder:font-sans placeholder:text-sm placeholder:tracking-normal placeholder:text-slate-400 focus:border-brand-600 focus:outline-none focus:ring-2 focus:ring-brand-600/20 disabled:cursor-not-allowed disabled:bg-slate-50 disabled:opacity-70"
      :class="error ? 'border-red-400 focus:border-red-500 focus:ring-red-500/20' : ''"
      aria-label="Secure Voting Token"
      @input="handleInput"
      @paste="handlePaste"
      @keydown="handleKeydown"
    />
    <p v-if="error" :id="`${inputId}-error`" class="text-sm text-red-600" role="alert">
      {{ error }}
    </p>
  </div>
</template>
