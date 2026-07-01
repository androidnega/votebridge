<script setup>
import { StatusBadge } from "@/components/ui";

defineProps({
  items: { type: Array, default: () => [] },
});
</script>

<template>
  <ul v-if="items.length" class="divide-y divide-border rounded-xl border border-border overflow-hidden">
    <li
      v-for="item in items"
      :key="item.id"
      class="flex items-center justify-between gap-4 bg-white px-4 py-3.5 transition duration-200 hover:bg-[#F9FAFB]"
    >
      <div class="min-w-0">
        <p class="text-sm font-medium text-ink-primary">{{ item.title }}</p>
        <p v-if="item.meta" class="mt-0.5 truncate text-xs text-ink-secondary">{{ item.meta }}</p>
      </div>
      <StatusBadge :status="item.severity || 'warning'" :label="item.label || item.count" />
    </li>
  </ul>
</template>
