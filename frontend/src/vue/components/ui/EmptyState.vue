<script setup>
import VIcon from "@/components/ui/VIcon.vue";

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
    default: "inbox",
  },
});
</script>

<template>
  <div
    class="flex flex-col items-center justify-center rounded-card border border-dashed border-border bg-surface-muted/50 px-6 py-10 text-center"
  >
    <div
      class="flex h-12 w-12 items-center justify-center rounded-full bg-white text-brand-600 shadow-card ring-1 ring-slate-900/5"
      aria-hidden="true"
    >
      <VIcon :name="icon" size="lg" />
    </div>
    <h4 class="mt-4 text-sm font-semibold text-slate-800">{{ title }}</h4>
    <p class="mt-1 max-w-sm text-sm text-slate-500">{{ description }}</p>
    <div v-if="$slots.action" class="mt-4">
      <slot name="action" />
    </div>
  </div>
</template>
