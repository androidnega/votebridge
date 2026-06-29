<script setup>
const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false,
  },
  disabled: {
    type: Boolean,
    default: false,
  },
  loading: {
    type: Boolean,
    default: false,
  },
  label: {
    type: String,
    default: "Feature flag",
  },
  compact: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(["update:modelValue"]);

function select(value) {
  if (props.disabled || props.loading || value === props.modelValue) return;
  emit("update:modelValue", value);
}
</script>

<template>
  <div
    class="relative inline-grid grid-cols-2 rounded-input bg-slate-100 p-0.5"
    :class="compact ? 'w-[8.5rem]' : 'w-full max-w-[11rem]'"
    role="radiogroup"
    :aria-label="`${label} status`"
  >
    <span
      class="pointer-events-none absolute bottom-0.5 top-0.5 rounded-input shadow-sm transition-[left,background-color] duration-200 ease-out"
      :class="[
        modelValue
          ? 'left-[calc(50%+0.0625rem)] bg-success-600'
          : 'left-0.5 bg-danger-600',
        loading ? 'opacity-70' : '',
      ]"
      style="width: calc(50% - 0.25rem)"
      aria-hidden="true"
    />

    <button
      type="button"
      role="radio"
      class="relative z-10 rounded-input px-2.5 font-semibold uppercase tracking-wide transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-600 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-60"
      :class="[
        compact ? 'py-1.5 text-[0.625rem]' : 'min-h-touch py-2 text-xs',
        modelValue ? 'text-slate-500' : 'text-white',
      ]"
      :aria-checked="!modelValue"
      :disabled="disabled || loading"
      @click="select(false)"
    >
      Off
    </button>

    <button
      type="button"
      role="radio"
      class="relative z-10 rounded-input px-2.5 font-semibold uppercase tracking-wide transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-600 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-60"
      :class="[
        compact ? 'py-1.5 text-[0.625rem]' : 'min-h-touch py-2 text-xs',
        modelValue ? 'text-white' : 'text-slate-500',
      ]"
      :aria-checked="modelValue"
      :disabled="disabled || loading"
      @click="select(true)"
    >
      On
    </button>
  </div>
</template>
