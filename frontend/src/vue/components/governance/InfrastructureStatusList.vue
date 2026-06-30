<script setup>
import OpsHealthBadge from "@/components/operations/OpsHealthBadge.vue";

defineProps({
  items: { type: Array, default: () => [] },
});
</script>

<template>
  <ul class="divide-y divide-[#E5E7EB]">
    <li
      v-for="item in items"
      :key="item.key"
      class="flex items-center justify-between gap-3 py-3 first:pt-0 last:pb-0"
    >
      <span class="text-sm font-medium text-[#1F2937]">{{ item.label }}</span>
      <OpsHealthBadge :status="item.status" />
    </li>
  </ul>
</template>
