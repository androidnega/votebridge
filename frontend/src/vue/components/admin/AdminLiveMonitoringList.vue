<script setup>
defineProps({
  items: { type: Array, default: () => [] },
});

const toneClasses = {
  default: "text-[#1F2937]",
  success: "text-[#16A34A]",
  warning: "text-[#D97706]",
  danger: "text-[#DC2626]",
  neutral: "text-[#64748B]",
};
</script>

<template>
  <ul class="space-y-3">
    <li
      v-for="item in items"
      :key="item.id"
      class="flex items-center justify-between gap-4 rounded-input border border-[#E5E7EB] bg-[#F8FAFC] px-4 py-3"
    >
      <span class="text-sm text-[#64748B]">{{ item.label }}</span>
      <span class="text-sm font-semibold tabular-nums" :class="toneClasses[item.tone] || toneClasses.default">
        {{ item.value }}
      </span>
    </li>
  </ul>
</template>
