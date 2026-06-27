<script setup>
defineProps({
  modelValue: Boolean,
  label: String,
  id: String,
  disabled: Boolean,
});
defineEmits(["update:modelValue"]);
</script>

<template>
  <label
    :for="id"
    class="inline-flex min-h-touch cursor-pointer select-none items-center gap-2 text-sm text-slate-700"
    :class="disabled ? 'cursor-not-allowed opacity-50' : ''"
  >
    <input
      :id="id"
      type="checkbox"
      class="h-4 w-4 rounded border-border text-brand-600 focus:ring-brand-600/30"
      :checked="modelValue"
      :disabled="disabled"
      @change="$emit('update:modelValue', $event.target.checked)"
    />
    <span v-if="label">{{ label }}</span>
  </label>
</template>
