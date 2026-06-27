<script setup>
defineProps({
  title: {
    type: String,
    default: "Nothing here yet",
  },
  description: {
    type: String,
    default: "Check back later for updates.",
  },
  icon: {
    type: String,
    default: "📭",
  },
});
</script>

<template>
  <div class="flex flex-col items-center justify-center rounded-xl border border-dashed border-slate-200 bg-slate-50/50 px-6 py-10 text-center">
    <span class="text-3xl" aria-hidden="true">{{ icon }}</span>
    <h4 class="mt-3 text-sm font-semibold text-slate-900">{{ title }}</h4>
    <p class="mt-1 max-w-sm text-sm text-slate-500">{{ description }}</p>
    <div v-if="$slots.action" class="mt-4">
      <slot name="action" />
    </div>
  </div>
</template>
