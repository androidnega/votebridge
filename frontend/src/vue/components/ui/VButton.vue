<script setup>
import { computed } from "vue";

const props = defineProps({
  variant: {
    type: String,
    default: "primary",
    validator: (value) => ["primary", "secondary", "danger", "ghost"].includes(value),
  },
  size: {
    type: String,
    default: "md",
    validator: (value) => ["sm", "md", "lg"].includes(value),
  },
  type: {
    type: String,
    default: "button",
  },
  loading: Boolean,
  disabled: Boolean,
  block: Boolean,
});

const classes = computed(() => {
  const base =
    "inline-flex min-h-touch items-center justify-center rounded-input font-semibold transition focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 disabled:cursor-not-allowed disabled:opacity-50";

  const variants = {
    primary:
      "bg-brand-600 text-white shadow-sm hover:bg-brand-hover focus-visible:outline-brand-600",
    secondary:
      "border border-brand-600 bg-white text-brand-600 shadow-sm hover:bg-brand-50 focus-visible:outline-brand-600",
    danger:
      "bg-danger-600 text-white shadow-sm hover:bg-danger-700 focus-visible:outline-danger-600",
    ghost:
      "bg-transparent text-slate-700 hover:bg-slate-100 focus-visible:outline-brand-600",
  };

  const sizes = {
    sm: "px-3 py-2 text-xs",
    md: "px-4 py-2.5 text-sm",
    lg: "px-5 py-3 text-base",
  };

  return [
    base,
    variants[props.variant],
    sizes[props.size],
    props.block ? "w-full" : "",
  ].join(" ");
});
</script>

<template>
  <button :type="type" :class="classes" :disabled="disabled || loading">
    <svg
      v-if="loading"
      class="-ml-0.5 mr-2 h-4 w-4 animate-spin"
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
      aria-hidden="true"
    >
      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
      <path
        class="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
      />
    </svg>
    <slot />
  </button>
</template>
