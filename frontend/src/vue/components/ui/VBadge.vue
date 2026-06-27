<script setup>
defineProps({
  variant: {
    type: String,
    default: "default",
    validator: (v) =>
      ["default", "success", "warning", "danger", "info", "draft", "scheduled", "open", "paused", "closed", "archived"].includes(v),
  },
  size: {
    type: String,
    default: "md",
    validator: (v) => ["sm", "md", "lg"].includes(v),
  },
  dot: Boolean,
});

const variantClasses = {
  default: "bg-slate-100 text-slate-700 ring-slate-200",
  success: "bg-success-50 text-success-600 ring-success-600/20",
  warning: "bg-warning-50 text-warning-600 ring-warning-600/20",
  danger: "bg-danger-50 text-danger-600 ring-danger-600/20",
  info: "bg-info-50 text-info-600 ring-info-600/20",
  draft: "bg-slate-100 text-slate-600 ring-slate-200",
  scheduled: "bg-slate-200 text-slate-700 ring-slate-300",
  open: "bg-success-50 text-success-600 ring-success-600/20",
  paused: "bg-warning-50 text-warning-600 ring-warning-600/20",
  closed: "bg-danger-50 text-danger-600 ring-danger-600/20",
  archived: "bg-slate-700 text-slate-100 ring-slate-800",
};

const sizeClasses = {
  sm: "px-2 py-0.5 text-xs",
  md: "px-2.5 py-0.5 text-xs",
  lg: "px-3 py-1 text-sm",
};
</script>

<template>
  <span
    class="inline-flex shrink-0 items-center gap-1.5 rounded-full font-medium capitalize ring-1 ring-inset"
    :class="[variantClasses[variant], sizeClasses[size]]"
  >
    <span v-if="dot" class="h-1.5 w-1.5 rounded-full bg-current" aria-hidden="true" />
    <slot />
  </span>
</template>
