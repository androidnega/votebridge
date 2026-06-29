<script setup>
import { computed } from "vue";

const props = defineProps({
  score: { type: Number, default: null },
  loading: Boolean,
});

const scoreClass = computed(() => {
  if (props.score === null || props.score === undefined) return "text-slate-400";
  if (props.score >= 90) return "text-success-700";
  if (props.score >= 70) return "text-warning-700";
  return "text-danger-700";
});

const ringClass = computed(() => {
  if (props.score === null || props.score === undefined) return "ring-slate-600/40 bg-slate-800/50";
  if (props.score >= 90) return "ring-success-600/30 bg-success-50/10";
  if (props.score >= 70) return "ring-warning-600/30 bg-warning-50/10";
  return "ring-danger-600/30 bg-danger-50/10";
});
</script>

<template>
  <div
    class="vb-vault-panel ring-1 ring-inset"
    :class="ringClass"
    role="status"
    :aria-label="score !== null ? `Integrity score ${score} percent` : 'Integrity score unavailable'"
  >
    <p class="vb-vault-caption">Integrity score</p>
    <p class="mt-2 text-3xl font-bold tabular-nums text-slate-100" :class="scoreClass">
      <span v-if="loading" class="inline-block h-8 w-12 animate-pulse rounded bg-slate-700" />
      <span v-else-if="score !== null">{{ score }}%</span>
      <span v-else>—</span>
    </p>
  </div>
</template>
