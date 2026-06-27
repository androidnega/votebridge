<script setup>
import { computed } from "vue";

const props = defineProps({
  score: { type: Number, default: null },
  loading: Boolean,
});

const scoreClass = computed(() => {
  if (props.score === null || props.score === undefined) return "text-slate-400";
  if (props.score >= 90) return "text-green-700";
  if (props.score >= 70) return "text-amber-700";
  return "text-red-700";
});

const ringClass = computed(() => {
  if (props.score === null || props.score === undefined) return "ring-slate-200";
  if (props.score >= 90) return "ring-green-200 bg-green-50";
  if (props.score >= 70) return "ring-amber-200 bg-amber-50";
  return "ring-red-200 bg-red-50";
});
</script>

<template>
  <div
    class="rounded-xl p-5 shadow-sm ring-1 ring-inset"
    :class="ringClass"
    role="status"
    :aria-label="score !== null ? `Integrity score ${score} percent` : 'Integrity score unavailable'"
  >
    <p class="text-xs font-medium uppercase tracking-wide text-slate-500">Integrity score</p>
    <p class="mt-2 text-3xl font-bold tabular-nums" :class="scoreClass">
      <span v-if="loading" class="inline-block h-8 w-12 animate-pulse rounded bg-slate-200" />
      <span v-else-if="score !== null">{{ score }}%</span>
      <span v-else>—</span>
    </p>
  </div>
</template>
