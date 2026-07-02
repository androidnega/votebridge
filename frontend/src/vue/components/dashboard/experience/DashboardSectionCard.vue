<script setup>
defineProps({
  title: { type: String, required: true },
  subtitle: { type: String, default: "" },
  noPadding: Boolean,
});
</script>

<template>
  <section class="flex h-full min-h-0 flex-col rounded-2xl border border-border bg-white shadow-[0_1px_2px_0_rgb(15_23_42_/_0.04)]">
    <header class="shrink-0 border-b border-border px-5 py-4 sm:px-6 sm:py-4">
      <div class="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h3 class="text-base font-semibold text-ink-primary">{{ title }}</h3>
          <p v-if="subtitle" class="mt-1 text-sm text-ink-secondary">{{ subtitle }}</p>
        </div>
        <slot name="actions" />
      </div>
    </header>
    <div class="flex min-h-0 flex-1 flex-col" :class="noPadding ? '' : 'p-5 sm:p-6'">
      <slot />
    </div>
  </section>
</template>
