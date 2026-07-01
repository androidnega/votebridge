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
  <ul class="grid grid-cols-2 gap-3 md:grid-cols-3">
    <li
      v-for="item in items"
      :key="item.id"
      class="flex min-h-touch flex-col justify-center gap-1 rounded-input border border-[#E5E7EB] bg-[#F8FAFC] px-3 py-3 sm:px-4"
    >
      <span class="text-xs leading-snug text-[#64748B]">{{ item.label }}</span>
      <span
        class="text-lg font-semibold tabular-nums leading-tight"
        :class="toneClasses[item.tone] || toneClasses.default"
      >
        {{ item.value }}
      </span>
    </li>
  </ul>
</template>
