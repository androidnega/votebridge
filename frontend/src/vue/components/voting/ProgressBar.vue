<script setup>
import { computed } from "vue";

const props = defineProps({
  value: {
    type: Number,
    default: 0,
  },
  max: {
    type: Number,
    default: 100,
  },
  label: String,
});

const percent = computed(() => {
  if (props.max <= 0) return 0;
  return Math.min(100, Math.round((props.value / props.max) * 100));
});
</script>

<template>
  <div>
    <div v-if="label" class="mb-2 flex items-center justify-between text-xs text-slate-500">
      <span>{{ label }}</span>
      <span>{{ percent }}%</span>
    </div>
    <div
      class="h-2 overflow-hidden rounded-full bg-slate-100"
      role="progressbar"
      :aria-valuenow="value"
      :aria-valuemin="0"
      :aria-valuemax="max"
      :aria-label="label || 'Progress'"
    >
      <div
        class="h-full rounded-full bg-brand-600 transition-all duration-300 ease-out"
        :style="{ width: `${percent}%` }"
      />
    </div>
  </div>
</template>
