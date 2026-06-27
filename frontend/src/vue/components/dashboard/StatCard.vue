<script setup>
defineProps({
  label: {
    type: String,
    required: true,
  },
  value: {
    type: [String, Number],
    default: "—",
  },
  hint: String,
  accent: {
    type: String,
    default: "brand",
  },
  loading: Boolean,
});

const accentClasses = {
  brand: "bg-brand-50 text-brand-700",
  green: "bg-success-50 text-success-600",
  amber: "bg-warning-50 text-warning-600",
  red: "bg-danger-50 text-danger-600",
  slate: "bg-slate-100 text-slate-600",
};
</script>

<template>
  <div class="rounded-card bg-white p-card shadow-card ring-1 ring-slate-900/5 vb-fade-in">
    <div
      class="mb-3 inline-flex rounded-lg px-2.5 py-1 text-xs font-semibold uppercase tracking-wide"
      :class="accentClasses[accent] || accentClasses.brand"
    >
      {{ label }}
    </div>
    <div v-if="loading" class="h-9 w-24 animate-pulse rounded-lg bg-slate-100" />
    <p v-else class="text-3xl font-bold tracking-tight text-slate-800">{{ value }}</p>
    <p v-if="hint && !loading" class="mt-2 text-sm text-slate-500">{{ hint }}</p>
    <div v-if="$slots.footer" class="mt-3 border-t border-border pt-3">
      <slot name="footer" />
    </div>
  </div>
</template>
