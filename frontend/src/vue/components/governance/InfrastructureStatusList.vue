<script setup>
import OpsHealthBadge from "@/components/operations/OpsHealthBadge.vue";

defineProps({
  items: { type: Array, default: () => [] },
});
</script>

<template>
  <div class="grid grid-cols-1 gap-3 sm:grid-cols-2">
    <div
      v-for="item in items"
      :key="item.key"
      class="flex items-center justify-between gap-3 rounded-input border border-[#E5E7EB] bg-[#F8FAFC] px-4 py-3.5"
    >
      <span class="text-sm font-medium text-[#1F2937]">{{ item.label }}</span>
      <OpsHealthBadge :status="item.status" />
    </div>
  </div>
</template>
