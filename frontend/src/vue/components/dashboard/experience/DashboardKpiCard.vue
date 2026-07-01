<script setup>
import { computed } from "vue";
import VIcon from "@/components/ui/VIcon.vue";

const props = defineProps({
  id: { type: String, default: "" },
  title: { type: String, required: true },
  value: { type: [String, Number], default: "—" },
  detail: { type: String, default: "" },
  hint: { type: String, default: "" },
  icon: { type: String, default: "elections" },
  accent: { type: String, default: "blue" },
  trend: { type: Array, default: () => [] },
  clickable: Boolean,
});

defineEmits(["click"]);

const accentStyles = {
  blue: { bg: "#EFF6FF", icon: "#2563EB", value: "#1E40AF" },
  green: { bg: "#E8F5EE", icon: "#166534", value: "#166534" },
  amber: { bg: "#FFFBEB", icon: "#D97706", value: "#B45309" },
  red: { bg: "#FEF2F2", icon: "#DC2626", value: "#B91C1C" },
  slate: { bg: "#F3F4F6", icon: "#6B7280", value: "#1F2937" },
};

const palette = computed(() => accentStyles[props.accent] || accentStyles.blue);
</script>

<template>
  <article
    class="flex min-h-[132px] flex-col rounded-2xl border border-border bg-white p-6 shadow-[0_1px_2px_0_rgb(15_23_42_/_0.04)] transition duration-200"
    :class="clickable ? 'cursor-pointer hover:border-[#D1D5DB] hover:shadow-[0_4px_12px_-4px_rgb(15_23_42_/_0.08)]' : ''"
    @click="clickable ? $emit('click') : undefined"
  >
    <div class="flex items-start justify-between gap-3">
      <div class="flex min-w-0 items-center gap-3">
        <span
          class="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl"
          :style="{ backgroundColor: palette.bg, color: palette.icon }"
          aria-hidden="true"
        >
          <VIcon :name="icon" size="sm" />
        </span>
        <p class="text-sm font-medium text-ink-secondary">{{ title }}</p>
      </div>
    </div>

    <div class="mt-4 flex items-end justify-between gap-3">
      <div>
        <p class="text-[1.75rem] font-semibold leading-none tabular-nums" :style="{ color: palette.value }">
          {{ value }}
        </p>
        <p v-if="detail" class="mt-1.5 text-sm text-ink-secondary">{{ detail }}</p>
      </div>
      <svg
        v-if="trend.length > 1"
        viewBox="0 0 64 24"
        class="h-6 w-16 shrink-0 opacity-80"
        aria-hidden="true"
      >
        <polyline
          fill="none"
          :stroke="palette.icon"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          :points="trend.map((v, i) => `${(i / (trend.length - 1)) * 64},${24 - (v / Math.max(...trend, 1)) * 20}`).join(' ')"
        />
      </svg>
    </div>

    <p v-if="hint" class="mt-3 text-xs text-ink-secondary">{{ hint }}</p>
  </article>
</template>
