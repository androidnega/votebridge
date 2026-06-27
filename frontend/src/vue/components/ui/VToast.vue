<script setup>
defineProps({
  toast: {
    type: Object,
    required: true,
  },
});

defineEmits(["dismiss"]);

const variantClasses = {
  success: "border-l-4 border-success-600 bg-white text-slate-800 ring-1 ring-slate-200",
  error: "border-l-4 border-danger-600 bg-white text-slate-800 ring-1 ring-slate-200",
  warning: "border-l-4 border-warning-600 bg-white text-slate-800 ring-1 ring-slate-200",
  info: "border-l-4 border-info-600 bg-white text-slate-800 ring-1 ring-slate-200",
};
</script>

<template>
  <div
    class="pointer-events-auto flex w-full max-w-sm items-start justify-between gap-3 rounded-input px-4 py-3 shadow-card"
    :class="variantClasses[toast.variant] || variantClasses.info"
    role="status"
  >
    <p class="text-sm font-medium">{{ toast.message }}</p>
    <button
      type="button"
      class="min-h-touch min-w-touch rounded p-1 text-slate-500 hover:text-slate-800"
      aria-label="Dismiss notification"
      @click="$emit('dismiss', toast.id)"
    >
      ✕
    </button>
  </div>
</template>
