<script setup>
import { StatusBadge, VButton } from "@/components/ui";

defineProps({
  items: { type: Array, default: () => [] },
});

defineEmits(["select"]);
</script>

<template>
  <ul v-if="items.length" class="space-y-3">
    <li
      v-for="item in items"
      :key="item.id"
      class="rounded-2xl border border-border bg-[#F9FAFB] p-5 transition duration-200 hover:border-[#D1D5DB] hover:bg-white"
    >
      <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div class="min-w-0">
          <div class="flex flex-wrap items-center gap-2">
            <p class="truncate text-base font-semibold text-ink-primary">{{ item.title }}</p>
            <StatusBadge :status="item.status || 'scheduled'" />
          </div>
          <p v-if="item.faculty" class="mt-1 text-sm text-ink-secondary">{{ item.faculty }}</p>
          <p class="mt-2 text-xs text-ink-secondary">
            Opens {{ item.startDate ? new Date(item.startDate).toLocaleString() : "—" }}
          </p>
        </div>
        <div class="flex shrink-0 flex-col items-start gap-2 sm:items-end">
          <p v-if="item.countdown" class="text-sm font-semibold tabular-nums text-[#166534]">
            {{ item.countdown }}
          </p>
          <VButton variant="secondary" size="sm" @click="$emit('select', item.route)">View</VButton>
        </div>
      </div>
    </li>
  </ul>
</template>
