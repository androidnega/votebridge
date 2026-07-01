<script setup>
defineProps({
  label: { type: String, required: true },
  value: { type: [String, Number], required: true },
});
</script>

<template>
  <div class="flex flex-col items-center justify-center rounded-input border border-[#E5E7EB] bg-[#F8FAFC] px-3 py-5 text-center">
    <p class="text-3xl font-semibold tabular-nums tracking-tight text-[#1F2937]">{{ value }}</p>
    <p class="mt-2 text-xs font-medium leading-snug text-[#64748B]">{{ label }}</p>
  </div>
</template>
