<script setup>
import { formatRelativeTime } from "@/utils/formatTime";

defineProps({
  items: { type: Array, default: () => [] },
});
</script>

<template>
  <ul v-if="items.length" class="relative space-y-0">
    <li
      v-for="(item, index) in items"
      :key="item.id"
      class="relative flex gap-4 pb-6 last:pb-0"
    >
      <span
        v-if="index < items.length - 1"
        class="absolute left-[11px] top-6 h-[calc(100%-12px)] w-px bg-border"
        aria-hidden="true"
      />
      <span
        class="relative z-10 mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-[#E8F5EE] text-xs font-bold text-[#166534]"
        aria-hidden="true"
      >
        ✓
      </span>
      <div class="min-w-0 flex-1 pt-0.5">
        <p class="text-sm font-medium text-ink-primary">{{ item.title }}</p>
        <p v-if="item.meta" class="mt-0.5 text-xs text-ink-secondary">{{ item.meta }}</p>
        <p v-if="item.timestamp" class="mt-1 text-xs font-medium text-[#2563EB]">
          {{ formatRelativeTime(item.timestamp) }}
        </p>
      </div>
    </li>
  </ul>
</template>
