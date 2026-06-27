<script setup>
import { ref } from "vue";

defineProps({
  modelValue: {
    type: [String, Number],
    default: "",
  },
  label: String,
  placeholder: String,
  error: String,
  hint: String,
  disabled: Boolean,
  required: Boolean,
  id: String,
  autocomplete: {
    type: String,
    default: "current-password",
  },
});

defineEmits(["update:modelValue"]);

const visible = ref(false);
</script>

<template>
  <div class="space-y-1.5">
    <label v-if="label" :for="id" class="vb-label">
      {{ label }}
      <span v-if="required" class="text-red-500">*</span>
    </label>
    <div class="relative">
      <input
        :id="id"
        :type="visible ? 'text' : 'password'"
        :value="modelValue"
        :placeholder="placeholder"
        :disabled="disabled"
        :required="required"
        :autocomplete="autocomplete"
        class="vb-input pr-10"
        :class="error ? 'ring-red-300 focus:ring-red-500' : ''"
        @input="$emit('update:modelValue', $event.target.value)"
      />
      <button
        type="button"
        class="absolute inset-y-0 right-0 flex items-center px-3 text-slate-500 hover:text-slate-700"
        :aria-label="visible ? 'Hide password' : 'Show password'"
        @click="visible = !visible"
      >
        <span class="text-xs font-medium">{{ visible ? "Hide" : "Show" }}</span>
      </button>
    </div>
    <p v-if="error" class="text-sm text-red-600">{{ error }}</p>
    <p v-else-if="hint" class="text-sm text-slate-500">{{ hint }}</p>
  </div>
</template>
