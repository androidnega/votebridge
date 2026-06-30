<script setup>
import { computed, nextTick, onMounted, ref, watch } from "vue";

const props = defineProps({
  modelValue: { type: String, default: "" },
  length: { type: Number, default: 6 },
  disabled: Boolean,
  error: { type: String, default: "" },
});

const emit = defineEmits(["update:modelValue", "complete"]);

const inputs = ref([]);
const digits = ref(Array.from({ length: props.length }, () => ""));

const code = computed(() => digits.value.join(""));

watch(
  () => props.modelValue,
  (value) => {
    const chars = String(value || "")
      .replace(/\D/g, "")
      .slice(0, props.length)
      .split("");
    digits.value = Array.from({ length: props.length }, (_, i) => chars[i] || "");
  },
  { immediate: true }
);

watch(code, (value) => {
  emit("update:modelValue", value);
  if (value.length === props.length) {
    emit("complete", value);
  }
});

onMounted(() => {
  inputs.value[0]?.focus();
});

function focusInput(index) {
  nextTick(() => inputs.value[index]?.focus());
}

function onInput(index, event) {
  const raw = event.target.value.replace(/\D/g, "");
  if (!raw) {
    digits.value[index] = "";
    return;
  }
  digits.value[index] = raw.slice(-1);
  if (index < props.length - 1) {
    focusInput(index + 1);
  }
}

function onKeydown(index, event) {
  if (event.key === "Backspace" && !digits.value[index] && index > 0) {
    digits.value[index - 1] = "";
    focusInput(index - 1);
    event.preventDefault();
  }
  if (event.key === "ArrowLeft" && index > 0) {
    focusInput(index - 1);
  }
  if (event.key === "ArrowRight" && index < props.length - 1) {
    focusInput(index + 1);
  }
}

function onPaste(event) {
  event.preventDefault();
  const pasted = event.clipboardData.getData("text").replace(/\D/g, "").slice(0, props.length);
  if (!pasted) return;
  digits.value = Array.from({ length: props.length }, (_, i) => pasted[i] || "");
  focusInput(Math.min(pasted.length, props.length - 1));
}
</script>

<template>
  <div>
    <div
      class="flex justify-center gap-2 sm:gap-2.5"
      role="group"
      aria-label="Verification code"
      @paste="onPaste"
    >
      <input
        v-for="(_, index) in length"
        :key="index"
        :ref="(el) => (inputs[index] = el)"
        :value="digits[index]"
        type="text"
        inputmode="numeric"
        autocomplete="one-time-code"
        maxlength="1"
        class="vb-otp-box"
        :class="{ 'vb-otp-box--filled': digits[index], 'vb-otp-box--error': error }"
        :disabled="disabled"
        :aria-label="`Digit ${index + 1} of ${length}`"
        @input="onInput(index, $event)"
        @keydown="onKeydown(index, $event)"
      />
    </div>
    <p v-if="error" class="mt-2 text-center text-xs text-danger-600">{{ error }}</p>
  </div>
</template>
