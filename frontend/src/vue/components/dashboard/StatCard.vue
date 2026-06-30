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
    default: "neutral",
  },
  loading: Boolean,
});
</script>

<template>
  <div class="vb-kpi-card">
    <p class="text-sm text-ink-secondary">{{ label }}</p>
    <div v-if="loading" class="mt-2 h-9 w-24 animate-pulse rounded-lg bg-surface-muted" />
    <p v-else class="mt-2 text-3xl font-semibold tabular-nums tracking-tight text-ink-primary">
      {{ value }}
    </p>
    <p v-if="hint && !loading" class="mt-2 text-xs text-ink-secondary">{{ hint }}</p>
    <div v-if="$slots.footer" class="mt-3 border-t border-border pt-3">
      <slot name="footer" />
    </div>
  </div>
</template>
