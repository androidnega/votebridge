<script setup>
defineProps({
  items: { type: Array, default: () => [] },
});
</script>

<template>
  <ul v-if="items.length" class="relative space-y-0">
    <li
      v-for="(item, index) in items"
      :key="item.id"
      class="relative flex gap-4 pb-5 last:pb-0"
    >
      <span
        v-if="index < items.length - 1"
        class="absolute left-[7px] top-4 h-[calc(100%-4px)] w-px bg-[#E5E7EB]"
        aria-hidden="true"
      />
      <span
        class="relative z-10 mt-1.5 h-3.5 w-3.5 shrink-0 rounded-full border-2 border-white bg-[#2563EB] ring-2 ring-[#2563EB]/20"
        aria-hidden="true"
      />
      <div class="min-w-0 flex-1 pt-0.5">
        <p class="text-sm font-medium text-[#1F2937]">{{ item.title }}</p>
        <p v-if="item.meta" class="mt-0.5 text-xs text-[#64748B]">{{ item.meta }}</p>
      </div>
    </li>
  </ul>
</template>
