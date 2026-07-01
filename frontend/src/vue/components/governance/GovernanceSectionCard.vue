<script setup>
defineProps({
  title: { type: String, required: true },
  subtitle: { type: String, default: "" },
  noPadding: Boolean,
});
</script>

<template>
  <section class="flex h-full flex-col overflow-hidden rounded-card border border-[#E5E7EB] bg-white shadow-[0_1px_3px_0_rgb(15_23_42_/_0.06)]">
    <header class="shrink-0 border-b border-border bg-surface-muted px-6 py-4">
      <h3 class="text-base font-semibold text-[#1F2937]">{{ title }}</h3>
      <p v-if="subtitle" class="mt-1 text-sm text-[#64748B]">{{ subtitle }}</p>
    </header>
    <div class="min-w-0 flex-1" :class="noPadding ? '' : 'p-6'">
      <slot />
    </div>
  </section>
</template>
