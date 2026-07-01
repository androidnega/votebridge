<script setup>
defineProps({
  currentStep: { type: Number, required: true },
  totalSteps: { type: Number, required: true },
  positionTitle: { type: String, default: "" },
  percent: { type: Number, default: 0 },
});
</script>

<template>
  <div class="mb-6">
    <div class="flex flex-wrap items-center justify-between gap-2 text-sm">
      <p class="font-semibold text-ink-primary">
        <span v-if="positionTitle">{{ positionTitle }}</span>
        <span v-else>Review</span>
      </p>
      <p class="text-ink-secondary">Step {{ currentStep }} of {{ totalSteps }}</p>
    </div>
    <div class="mt-3 h-2 overflow-hidden rounded-full bg-slate-200">
      <div
        class="h-full rounded-full bg-brand-700 transition-all duration-300"
        :style="{ width: `${Math.min(100, Math.max(0, percent))}%` }"
      />
    </div>
    <p class="mt-1 text-right text-xs text-ink-secondary">{{ percent }}%</p>
  </div>
</template>
