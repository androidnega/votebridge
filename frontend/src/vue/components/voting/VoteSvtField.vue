<script setup>
import { onMounted, ref } from "vue";
import { normalizeSvtToken } from "@/utils/svtToken";

defineProps({
  modelValue: { type: String, default: "" },
  inputId: { type: String, default: "vote-svt-input" },
  label: { type: String, default: "Secure voting token" },
  placeholder: { type: String, default: "Paste token to authenticate" },
  error: { type: String, default: "" },
  disabled: { type: Boolean, default: false },
  required: { type: Boolean, default: false },
});

const emit = defineEmits(["update:modelValue"]);

const fieldName = ref(`vb-svt-${crypto.randomUUID?.() ?? Date.now()}`);
const isLocked = ref(true);
const inputRef = ref(null);

onMounted(() => {
  window.setTimeout(() => inputRef.value?.focus(), 60);
});

function unlockField() {
  if (isLocked.value) {
    isLocked.value = false;
  }
}

function updateValue(raw) {
  emit("update:modelValue", normalizeSvtToken(raw));
}

function handleInput(event) {
  updateValue(event.target.value);
}

function handlePaste(event) {
  unlockField();
  const pasted = event.clipboardData?.getData("text");
  if (!pasted) return;
  event.preventDefault();
  updateValue(pasted);
  if (inputRef.value) {
    inputRef.value.value = normalizeSvtToken(pasted);
  }
}
</script>

<template>
  <div class="vb-svt-field">
    <label :for="inputId" class="vb-svt-field-label">
      {{ label }}
      <span v-if="required" class="text-red-500">*</span>
    </label>

    <!-- Decoy fields discourage browser/password-manager autofill -->
    <input
      type="text"
      tabindex="-1"
      autocomplete="username"
      aria-hidden="true"
      class="pointer-events-none absolute h-0 w-0 opacity-0"
    />

    <div class="relative">
      <input
        :id="inputId"
        ref="inputRef"
        :name="fieldName"
        :value="modelValue"
        type="text"
        inputmode="text"
        autocomplete="one-time-code"
        autocapitalize="off"
        autocorrect="off"
        spellcheck="false"
        data-lpignore="true"
        data-1p-ignore
        data-form-type="other"
        :placeholder="placeholder"
        :disabled="disabled"
        :required="required"
        :readonly="isLocked"
        class="vb-svt-field-input"
        :class="error ? 'vb-svt-field-input-error' : ''"
        @focus="unlockField"
        @mousedown="unlockField"
        @input="handleInput"
        @paste="handlePaste"
      />
      <span class="vb-svt-field-badge" aria-hidden="true">SVT</span>
    </div>

    <p v-if="error" class="text-sm text-red-600">{{ error }}</p>
    <p v-else class="vb-svt-field-hint">One-time code · paste or type · not stored in browser</p>
  </div>
</template>
