<script setup>
defineProps({
  status: {
    type: String,
    default: "unknown",
  },
});
const variants = {
  healthy: "bg-success-50 text-success-600",
  warning: "bg-warning-50 text-warning-600",
  critical: "bg-danger-50 text-danger-600",
  unknown: "bg-slate-100 text-slate-600",
};
</script>

<template>
  <span
    class="inline-flex items-center rounded-input px-2.5 py-1 text-xs font-semibold capitalize"
    :class="variants[status] || variants.unknown"
  >
    {{ status }}
  </span>
</template>
