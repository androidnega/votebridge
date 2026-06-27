<script setup>
defineProps({
  variant: {
    type: String,
    default: "card",
  },
  rows: {
    type: Number,
    default: 3,
  },
});
</script>

<template>
  <div v-if="variant === 'stats'" class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
    <div v-for="n in rows" :key="n" class="animate-pulse rounded-xl bg-white p-5 ring-1 ring-slate-900/5">
      <div class="h-4 w-20 rounded bg-slate-200" />
      <div class="mt-4 h-8 w-16 rounded bg-slate-200" />
      <div class="mt-3 h-3 w-28 rounded bg-slate-100" />
    </div>
  </div>

  <div v-else-if="variant === 'list'" class="space-y-3">
    <div v-for="n in rows" :key="n" class="animate-pulse rounded-lg bg-slate-100 px-4 py-4">
      <div class="h-4 w-2/3 rounded bg-slate-200" />
      <div class="mt-2 h-3 w-1/2 rounded bg-slate-200" />
    </div>
  </div>

  <div v-else class="animate-pulse rounded-xl bg-white p-6 ring-1 ring-slate-900/5">
    <div class="h-5 w-1/3 rounded bg-slate-200" />
    <div class="mt-4 space-y-3">
      <div class="h-4 w-full rounded bg-slate-100" />
      <div class="h-4 w-5/6 rounded bg-slate-100" />
      <div class="h-4 w-4/6 rounded bg-slate-100" />
    </div>
  </div>
</template>
