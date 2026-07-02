<script setup>
defineProps({
  label: { type: String, required: true },
  value: { type: String, default: "" },
  percent: { type: Number, default: 0 },
  tone: { type: String, default: "brand" },
});

const toneClasses = {
  brand: "bg-brand-600",
  blue: "bg-info-600",
  amber: "bg-warning-600",
  slate: "bg-slate-500",
};
</script>

<template>
  <div>
    <div class="mb-1.5 flex items-center justify-between gap-2 text-xs">
      <span class="font-medium text-slate-600">{{ label }}</span>
      <span class="tabular-nums font-semibold text-slate-800">{{ value }}</span>
    </div>
    <div class="h-2 overflow-hidden rounded-full bg-slate-100">
      <div
        class="h-full rounded-full transition-all duration-500"
        :class="toneClasses[tone] || toneClasses.brand"
        :style="{ width: `${Math.min(100, Math.max(0, percent))}%` }"
      />
    </div>
  </div>
</template>
