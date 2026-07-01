<script setup>
import { getGovernanceSoftPalette } from "@/config/governanceDashboard";

defineProps({
  items: { type: Array, default: () => [] },
});

function tileStyle(index) {
  const palette = getGovernanceSoftPalette(index);
  return {
    backgroundColor: palette.bg,
    borderColor: palette.border,
    "--tile-accent": palette.icon,
  };
}
</script>

<template>
  <dl class="grid grid-cols-3 gap-2 sm:gap-2.5">
    <div
      v-for="(item, index) in items"
      :key="item.label"
      class="min-w-0 rounded-input border px-2.5 py-2 sm:px-3 sm:py-2.5"
      :style="tileStyle(index)"
    >
      <dt
        class="text-[0.625rem] font-semibold uppercase tracking-wide sm:text-[0.6875rem]"
        style="color: var(--tile-accent)"
      >
        {{ item.label }}
      </dt>
      <dd
        class="mt-0.5 line-clamp-2 text-xs font-medium leading-tight text-[#1F2937] [overflow-wrap:anywhere] sm:mt-1"
        :title="String(item.value)"
      >
        {{ item.value }}
      </dd>
    </div>
  </dl>
</template>
